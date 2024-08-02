import logging
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from pandas import DataFrame
from tqdm import tqdm

from util import clean_dataset, generate_topic_classification, get_datasets_content, get_environ_values, setup_logging, triplets_check
from invoke.main import create_session, publish_dataset, request_dataset, update_dataset

def main(log_filename: str, dataverse_url: str, dataverse_api_key: str, csv: Path, for_column_name: str, doi_column_name: str):
  """
  Given a valid csv which at minimum contains a 'FoR' and 'DOI' column, iterate over each row to update each 
  dataset (based on DOI) to add it's equivalent FoR code(s).

  Parameters:
    - log_filename        <str>   : The log file's filename
    - dataverse_url       <str>   : The URL to the given Dataverse instance
    - dataverse_api_key   <str>   : API key used to invoke the given Dataverse instance
    - csv                 <Path>  : Path to the CSV
    - for_column_name     <str>   : Name of the column which has FOR data
    - doi_column_name     <str>   : Name of the column which has DOI  
  
  """
  print("Beginning to append FoR codes to Dataverse...\n")
  output = []
  
  datasets = get_datasets_content(csv, for_column_name, doi_column_name)
  datasets = [clean_dataset(dataset, for_column_name) for dataset in datasets if triplets_check(dataset, for_column_name, doi_column_name)]
  
  session = create_session(dataverse_url, dataverse_api_key)
  
  for dataset in tqdm(datasets):
    dataset_metadata, okay_get_request = request_dataset(session, dataset[doi_column_name])

    version_state = dataset_metadata.get("latestVersion", {}).get("versionState")
    if not okay_get_request or not version_state:
      logging.error(f"Could not determine the versionState for the dataset: {dataset[doi_column_name]}")
      output.append([dataset[doi_column_name], False, "Bad response after requesting [GET] dataset metadata"])
      continue

    topic_classification_json = generate_topic_classification(dataset[for_column_name])
    update_response, okay_put_request = update_dataset(session, dataset[doi_column_name], topic_classification_json)
    if not okay_put_request and not update_response:
      logging.error(f"Did not succeed in UPDATING the dataset: {dataset[doi_column_name]}")
      output.append([dataset[doi_column_name], False, "Bad response after updating [PUT] dataset metadata"])
      continue

    if version_state.upper()!="DRAFT":
      publish_response, okay_post_request = publish_dataset(session, dataset[doi_column_name])
      if not publish_response and not okay_post_request:
        logging.error(f"Did not succeed in PUBLISHING the dataset: {dataset[doi_column_name]}")
        output.append([dataset[doi_column_name], "Partial", "Bad response after publishing [POST] dataset metadata"])
        continue
    
    logging.info(f"Successfully added the FoR codes for the dataset: {dataset[doi_column_name]}")
    output.append([dataset[doi_column_name], True, ""])

  df = DataFrame(output, columns=["DOI", "Success", "Error Reason"])
  csv_filename = f"FoR-Output-{str(datetime.now().isoformat())}.csv"
  df.to_csv(csv_filename, index=False)
  print(f"\nCompleted appending FoR codes to Dataverse!\n - View logs of this script to ensure that there were no problems: {Path(log_filename).absolute()}\n - See a CSV record of successful and failed FoR code transactions: {Path(csv_filename).absolute()}\n")

if __name__=="__main__":
  parser = ArgumentParser(prog='Add-FOR-Codes', description='Will add FOR codes to dataverse datasets')
  
  parser.add_argument("csv", type=Path)                                                 # CSV to read and iterate over
  parser.add_argument("-f", "--for_column_name", type=str, default="FINAL TRIPLETS")    # FoR column name in CSV
  parser.add_argument("-d", '--doi_column_name', type=str, default="DOI")               # DOI column name in CSV
  
  log_filename = f"logs/for-code-addition-{str(datetime.now().isoformat())}.log"
  setup_logging(log_filename)                                                           # Create log file to save all data
  
  dataverse_url, dataverse_api_key = get_environ_values()
  
  args = parser.parse_args()
  
  main(log_filename, dataverse_url, dataverse_api_key, **vars(args))