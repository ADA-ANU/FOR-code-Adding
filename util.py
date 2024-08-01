import logging, re
import pandas as pd
from json import loads
from os import environ
from pathlib import Path

def get_environ_values():
  try:
    return environ["DATAVERSE_URL"], environ["DATAVERSE_API_KEY"]
  except:
    print("Error! Ensure that you've created an '.env' file and that it contains the values 'DATAVERSE_URL' and 'DATAVERSE_API_KEY'.\nIf you have, and you're still getting this error, restart your 'poetry shell' before running the script again.")
    logging.error("Values 'DATAVERSE_URL' and 'DATAVERSE_API_KEY' were not defined within the '.env' file. If you have, and you're still getting this error, restart your 'poetry shell' before running the script again.")
    exit()

def get_datasets_content(csv: Path):
  """
  Read in and process a 'CSV' file, but first checking that it exists and is a CSV.
  Expected 'CSV' file format is as follow (where 'FINAL TRIPLETS' may, or may not, be given):

  |------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | dataset_id | dataset_title                                                                | URL                                                                         | DOI                 | FINAL TRIPLETS                                                                                                                                              |
  |------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | 7603       | Accident Survey' Study of Morbidity in Elizabeth Area, South Australia, 1978 | https://dataverse.ada.edu.au/dataset.xhtml?persistentId=doi:10.26193/2C5SBD | doi:10.26193/2C5SBD | "HEALTH SCIENCES;ANZSRC FoR;https://linked.data.gov.au/def/anzsrc-for/2020/42"                                                                              |
  | 16930      | "Yes, I Can! adult literacy campaign"                                        | https://dataverse.ada.edu.au/dataset.xhtml?persistentId=doi:10.26193/ICYRQG | doi:10.26193/ICYRQG | "HUMAN SOCIETY;ANZSRC FoR;  https://linked.data.gov.au/def/anzsrc-for/2020/44~EDUCATION;ANZSRC  FoR; https://linked.data.gov.au/def/anzsrc-for/2020/39"     |
  | ...        | ...                                                                          | ...                                                                         | ...                 | ...                                                                                                                                                         |
  |------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|

  Parameter:
    - csv   <Path> : Path to the file

  Returns: <dict[]>    
    [
      {
        "dataset_id": 7603,
        "dataset_title": "Accident Survey' Study of Morbidity in Elizabeth Area, South Australia, 1978",
        "URL": "https://dataverse.ada.edu.au/dataset.xhtml?persistentId=doi:10.26193/2C5SBD",
        "DOI": "doi:10.26193/2C5SBD",
        "FINAL TRIPLETS": "\"HEALTH SCIENCES;ANZSRC FoR;https://linked.data.gov.au/def/anzsrc-for/2020/42\""
      },
      {
        "dataset_id": 16930,
        "dataset_title": "\u2018Yes, I Can!\u2019 adult literacy campaign",
        "URL": "https://dataverse.ada.edu.au/dataset.xhtml?persistentId=doi:10.26193/ICYRQG",
        "DOI": "doi:10.26193/ICYRQG",
        "FINAL TRIPLETS": "\"HUMAN SOCIETY;ANZSRC FoR; https://linked.data.gov.au/def/anzsrc-for/2020/44~EDUCATION;ANZSRC FoR;https://linked.data.gov.au/def/anzsrc-for/2020/39\""
      },
      ...
    ]
  
  """
  abs_csv = csv.absolute()

  if not csv.is_file():
    error = "Error, CSV ({0}) does not exist. Exiting script..."
    print(error.format(csv))
    logging.error(error.format(abs_csv))
    exit()

  if csv.suffix.lower()!=".csv": # rudimentary extension check
    error = "Error, the 'CSV' ({0}) does not have a '.csv' suffix. Exiting script..."
    print(error.format(csv))
    logging.error(error.format(abs_csv))
    exit()
  
  # TODO - Check that all the columns exist within the given CSV

  df = pd.read_csv(csv)
  logging.info(f"Read '.csv' ({abs_csv}), it contained '{df.size}' datasets.")
  return loads(df.to_json(orient="records"))

def triplets_check(dataset: dict, for_column_name: str, id_column_name: str):
  """
  Check for a required FOR column and log an error for a given dataset which did not have a FOR column.

  Parameter:
    - dataset           <dict> : Dictionary based on a particular row within the CSV.
    - for_column_name   <str>  : 
    - id_column_name    <str>  : Identifier is used for error logs if an issue occurs
  
  Return: <boolean>
  
  """
  triples_exist = dataset.get(for_column_name)!=None
  if not triples_exist:
    logging.error(f"Dataset '{dataset[id_column_name]}' did not have any triplets and was excluded from the set")
  return triples_exist

def clean_dataset(dataset: dict, for_column_name: str):
  """
  Employs regex and splits the string content to clean it for using FOR triplets.

  Parameters:
    - dataset           <dict> : Dictionary based on a particular row within the CSV.
    - for_column_name   <str>  : String used as the key to return the FOR value
  
  """
  temp_for_col = dataset[for_column_name]
  temp_for_col = re.sub(r'\"', '', temp_for_col)
  dataset[for_column_name] = [sub_triplet.split(";") for sub_triplet in temp_for_col.split("~")]
  return dataset

def value_topic_classification(sub_for_codes: list[str] = list()):
  """
  
  Will return an empty dict if sub_for_codes is not a length of 3.
  
  """
  if len(sub_for_codes)!=3:
    # TODO - Warn user about this
    return {}

  type_name = ["topicClassValue", "topicClassVocab", "topicClassVocabURI"]
  return {f'citation:{sub_typename}': sub_val for sub_val, sub_typename in zip(sub_for_codes, type_name)}

def topic_classification(for_codes: list[list[str]] = list()):
  """
  """
  return {
    "citation:topicClassification": [
      value_topic_classification(for_code_triplet) 
      for for_code_triplet in for_codes 
      if len(for_code_triplet)==3
    ],
    "@context":{
      "citation": "https://dataverse.org/schema/citation/"
    }
  }

def setup_logging(filename: str="preservation-output.log"):
  """
  Sets up the log file to track the output of the script.

  Parameter:
    - filename  <str> : Sets the filename for the output file
  
  """
  parent = Path(filename).parent
  if not parent.exists():
    parent.mkdir(parents=True)
  
  logging.basicConfig(filename=filename, encoding="utf-8", level=logging.DEBUG)
  logging.info("Start FOR Code Additions")
