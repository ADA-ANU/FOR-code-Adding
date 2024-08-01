import argparse, logging
from datetime import datetime
from json import dumps
from pathlib import Path
from tqdm import tqdm

from util import get_environ_values, clean_dataset, get_datasets_content, setup_logging, topic_classification, triplets_check
from invoke.main import create_session, request_dataset, update_dataset

def main(dataverse_url: str, dataverse_api_key: str, csv: Path, for_column_name: str, id_column_name: str, title_column_name: str, url_column_name: str, doi_column_name: str):
  """
  TODO - Finish the Docstring
  Given a valid csv which contains, 

  Parameters:
    - dataverse_url     <str>   : The URL to the given Dataverse instance
    - dataverse_api_key <str>   : API key used to invoke the given Dataverse instance
    - csv               <Path>  : Path to the CSV
    - for_column_name   <str>   : Name of the column which has FOR data
    - id_column_name    <str>   : Name of the column which has ADA ID data
    - title_column_name <str>   : Name of the column which has dataset title data
    - url_column_name   <str>   : Name of the column which has URL
    - doi_column_name   <str>   : Name of the column which has DOI  

  """
  datasets = get_datasets_content(csv)
  datasets = [clean_dataset(dataset, for_column_name) for dataset in datasets if triplets_check(dataset, for_column_name, id_column_name)]
  session = create_session(dataverse_url, dataverse_api_key)
  for dataset in tqdm(datasets):
    dataset_metadata = request_dataset(session, dataset[doi_column_name])
    
    with open("metadata-response.json", "w") as file:
      file.write(dumps(dataset_metadata, indent=2))

    version_state = dataset_metadata.get("latestVersion", {}).get("versionState")
    if not version_state:
      logging.error(f"Could not determine the versionState for the dataset: {dataset[doi_column_name]}")
      continue
    
    new_topic_classification = topic_classification(dataset[for_column_name])
    response = update_dataset(session, dataset[doi_column_name], new_topic_classification)

    with open("put-request-response.json", "w") as file:
      file.write(dumps(response, indent=2))

    if version_state.upper()!="DRAFT":
      pass # Publish the given dataset
      
    # with open("dataset-example.json", "w") as file:
    #   file.write(dumps(resp, indent=2))
    
    exit()
    # datasets[index]["json"] = topic_classification(dataset[for_column_name])
  
  # with open("test.json", "w") as file:
  #   file.write(dumps(datasets, indent=2))

if __name__=="__main__":
  parser = argparse.ArgumentParser(prog='Add-FOR-Codes', description='Will add FOR codes to dataverse datasets')
  
  parser.add_argument("csv", type=Path)                     # CSV to read in
  parser.add_argument("-f", "--for_column_name", 
                      type=str, default="FINAL TRIPLETS")
  parser.add_argument("-i", "--id_column_name", 
                      type=str, default="dataset_id")
  parser.add_argument("-t", '--title_column_name',
                      type=str, default="dataset_title")
  parser.add_argument("-u", '--url_column_name',
                      type=str, default="URL")
  parser.add_argument("-d", '--doi_column_name',
                      type=str, default="DOI")
  
  setup_logging(f"logs/preservation-{str(datetime.now().isoformat())}.log")

  try:
    dataverse_url, dataverse_api_key = get_environ_values()
  except:
    print("Error! Ensure that you've created an '.env' file and that it contains the values 'DATAVERSE_URL' and 'DATAVERSE_API_KEY'.\nIf you have, and you're still getting this error, restart your 'poetry shell' before running the script again.")
    logging.error("Values 'DATAVERSE_URL' and 'DATAVERSE_API_KEY' were not defined within the '.env' file. If you have, and you're still getting this error, restart your 'poetry shell' before running the script again.")
    exit()

  args = parser.parse_args()

  main(dataverse_url, dataverse_api_key,**vars(args))