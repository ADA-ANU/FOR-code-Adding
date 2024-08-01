import logging
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from pandas import DataFrame
from tqdm import tqdm

from util import get_environ_values, clean_dataset, get_datasets_content, setup_logging, topic_classification, triplets_check
from invoke.main import create_session, publish_dataset, request_dataset, update_dataset

def main(dataverse_url: str, dataverse_api_key: str, csv: Path, for_column_name: str, doi_column_name: str):
  """
  Given a valid csv which at minimum contains a 'FoR' and 'DOI' column, iterate over each row to update each 
  dataset (based on DOI) to add it's equivalent FoR code(s).

  Parameters:
    - dataverse_url     <str>   : The URL to the given Dataverse instance
    - dataverse_api_key <str>   : API key used to invoke the given Dataverse instance
    - csv               <Path>  : Path to the CSV
    - for_column_name   <str>   : Name of the column which has FOR data
    - doi_column_name   <str>   : Name of the column which has DOI  

  """
  print("Beginning to append FoR codes to Dataverse...")
  output = []
  datasets = get_datasets_content(csv)
  datasets = [clean_dataset(dataset, for_column_name) for dataset in datasets if triplets_check(dataset, for_column_name, doi_column_name)]
  session = create_session(dataverse_url, dataverse_api_key)
  for dataset in tqdm(datasets):
    dataset_metadata = request_dataset(session, dataset[doi_column_name])
    version_state = dataset_metadata.get("latestVersion", {}).get("versionState")
    if not version_state:
      logging.error(f"Could not determine the versionState for the dataset: {dataset[doi_column_name]}")
      output.append([dataset[doi_column_name], False, "Bad response after requesting dataset metadata"])
      continue
    
    new_topic_classification = topic_classification(dataset[for_column_name])
    response = update_dataset(session, dataset[doi_column_name], new_topic_classification)

    if version_state.upper()!="DRAFT":
      publish_dataset(session, dataset[doi_column_name])

  df = DataFrame(output, columns=["DOI", "Success", "Error Reason"])
  csv_filename = f"FoR-Output-{str(datetime.now().isoformat())}.csv"
  df.to_csv(csv_filename, index=False)
  print("Completed appending FoR codes to Dataverse!")

if __name__=="__main__":
  parser = ArgumentParser(prog='Add-FOR-Codes', description='Will add FOR codes to dataverse datasets')
  parser.add_argument("csv", type=Path)                                                 # CSV to read and iterate over
  parser.add_argument("-f", "--for_column_name", type=str, default="FINAL TRIPLETS")    # FoR column name in CSV
  parser.add_argument("-d", '--doi_column_name', type=str, default="DOI")               # DOI column name in CSV
  setup_logging(f"logs/preservation-{str(datetime.now().isoformat())}.log")             # Create log file to save all data
  dataverse_url, dataverse_api_key = get_environ_values()
  args = parser.parse_args()
  main(dataverse_url, dataverse_api_key, **vars(args))