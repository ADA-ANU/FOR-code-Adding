import logging, re
import pandas as pd
from json import loads
from os import environ
from pathlib import Path

def get_environ_values():
  """
  Get environment variables from '.env' file.
  If getting environment variables fails, exit the script.

  Return: <tuple(<str>, <str>)>

  """
  try:
    return environ["DATAVERSE_URL"], environ["DATAVERSE_API_KEY"]
  except:
    print("Error! Ensure that you've created an '.env' file and that it contains the values 'DATAVERSE_URL' and 'DATAVERSE_API_KEY'.\nIf you have, and you're still getting this error, restart your 'poetry shell' before running the script again.")
    logging.error("Values 'DATAVERSE_URL' and 'DATAVERSE_API_KEY' were not defined within the '.env' file. If you have, and you're still getting this error, restart your 'poetry shell' before running the script again.")
    exit()

def get_datasets_content(csv: Path, for_column_name: str, doi_column_name: str):
  """
  Read in and process a 'CSV' file, but first checking that it exists, that the file is a CSV, and that the CSV contains the correct columns.
  Expected 'CSV' file format is as follow (where 'FINAL TRIPLETS' may, or may not, be given):

  |------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | dataset_id | dataset_title                                                                | URL                                                                         | DOI                 | FINAL TRIPLETS                                                                                                                                              |
  |------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | 7603       | Accident Survey' Study of Morbidity in Elizabeth Area, South Australia, 1978 | https://dataverse.ada.edu.au/dataset.xhtml?persistentId=doi:10.26193/2C5SBD | doi:10.26193/2C5SBD | "HEALTH SCIENCES;ANZSRC FoR;https://linked.data.gov.au/def/anzsrc-for/2020/42"                                                                              |
  | 16930      | "Yes, I Can! adult literacy campaign"                                        | https://dataverse.ada.edu.au/dataset.xhtml?persistentId=doi:10.26193/ICYRQG | doi:10.26193/ICYRQG | "HUMAN SOCIETY;ANZSRC FoR;  https://linked.data.gov.au/def/anzsrc-for/2020/44~EDUCATION;ANZSRC  FoR; https://linked.data.gov.au/def/anzsrc-for/2020/39"     |
  | ...        | ...                                                                          | ...                                                                         | ...                 | ...                                                                                                                                                         |
  |------------|------------------------------------------------------------------------------|-----------------------------------------------------------------------------|---------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|

  Parameter:
    - csv               <Path> : Path to the file
    - for_column_name   <str>  : The FoR column name (checked here to exist within the CSV)
    - doi_column_name   <str>  : The DOI column name (checked here to exist within the CSV)

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

  df = pd.read_csv(csv)
  cols = list(df.columns)
  if for_column_name not in cols and doi_column_name not in cols:
    print("Error! The FoR and/or DOI columns were not found within the given CSV.")
    logging.error(f"One or more of columns names '{for_column_name}' and '{doi_column_name}' could not be found within the file {abs_csv}.")
    exit()
  
  logging.info(f"Read '.csv' ({abs_csv}), it contained '{df.size}' datasets.")
  return loads(df.to_json(orient="records"))

def triplets_check(dataset: dict, for_column_name: str, doi_column_name: str):
  """
  Check for a required FoR column and log an error for a given dataset which did not have a FOR column.
  Note! The script has already checked that the column exists, but double check that the column has content for the given dataset.
  
  Parameter:
    - dataset           <dict> : Dictionary based on a particular row within the CSV.
    - for_column_name   <str>  : The key 
    - doi_column_name   <str>  : Dataset DOI is only used for error log information if an issue occurs
  
  Return: <boolean>
  
  """
  triples_exist = dataset.get(for_column_name)!=None
  if not triples_exist:
    logging.error(f"Dataset '{dataset[doi_column_name]}' did not have any triplets and was excluded from the set")
  return triples_exist

def clean_dataset(dataset: dict, for_column_name: str):
  """
  Employs regex and splits the string content to clean it for using FOR triplets.

  Parameters:
    - dataset           <dict> : Dictionary based on a particular row within the CSV.
    - for_column_name   <str>  : String used as the key to return the FOR value
  
  Cleaning Steps:
    1. Remove any '\"' values from FoR column value
    2. Split FoR codes by '~' delimiter
    3. Split sub-FoR codes by ';' delimiter

  Cleaning Example:
    0. \"INDIGENOUS STUDIES;ANZSRC FoR;https://linked.data.gov.au/def/anzsrc-for/2020/45~HUMAN SOCIETY;ANZSRC FoR;https://linked.data.gov.au/def/anzsrc-for/2020/44\"
    1. INDIGENOUS STUDIES;ANZSRC FoR;https://linked.data.gov.au/def/anzsrc-for/2020/45~HUMAN SOCIETY;ANZSRC FoR;https://linked.data.gov.au/def/anzsrc-for/2020/44
    2. [
      'INDIGENOUS STUDIES;ANZSRC FoR;https://linked.data.gov.au/def/anzsrc-for/2020/45', 
      'HUMAN SOCIETY;ANZSRC FoR;https://linked.data.gov.au/def/anzsrc-for/2020/44'
    ]
    3. [
      [
        'INDIGENOUS STUDIES',
        'ANZSRC FoR',
        'https://linked.data.gov.au/def/anzsrc-for/2020/45'
      ], 
      [
        'HUMAN SOCIETY',
        'ANZSRC FoR',
        'https://linked.data.gov.au/def/anzsrc-for/2020/44'
      ]
    ]

  Returns: <dict>

  """
  temp_for_col = dataset[for_column_name]
  temp_for_col = re.sub(r'\"', '', temp_for_col)
  dataset[for_column_name] = [sub_triplet.split(";") for sub_triplet in temp_for_col.split("~")]
  return dataset

def value_topic_classification(sub_for_codes: list[str] = list()):
  """
  Generate the values within the 'citation:topicClassification' key for the PUT request.

  Parameters:
    - sub_for_codes <str[]> : Values to populate the topic values.
      Assumed that they're organised in the following way: ['value', 'vocab', 'uri']
  
  Returns: <dict>

    {
      'citation:topicClassValue'    : sub_for_codes[0],
      'citation:topicClassVocab'    : sub_for_codes[1],
      'citation:topicClassVocabURI' : sub_for_codes[2]
    }

    OR

    {}

  """
  if len(sub_for_codes)!=3:
    return {}

  type_name = ["topicClassValue", "topicClassVocab", "topicClassVocabURI"]
  return {f'citation:{sub_typename}': sub_val for sub_val, sub_typename in zip(sub_for_codes, type_name)}

def generate_topic_classification(for_codes: list[list[str]] = list()):
  """
  Generate the JSON for the PUT request to update a given dataset's FoR codes.

  Parameters:
    - for_codes <[str[]]> : nested list of length N that contains a dataset's FoR codes.
  
  Returns: <dict>

    {
      "citation:topicClassification": [
        {
          'citation:topicClassValue'    : sub_for_codes[0][0],
          'citation:topicClassVocab'    : sub_for_codes[0][1],
          'citation:topicClassVocabURI' : sub_for_codes[0][2]
        },
        ...,
        {
          'citation:topicClassValue'    : sub_for_codes[N][0],
          'citation:topicClassVocab'    : sub_for_codes[N][1],
          'citation:topicClassVocabURI' : sub_for_codes[N][2]
        },
      ],
      "@context":{
        "citation": "https://dataverse.org/schema/citation/"
      }
    }

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

def setup_logging(filename: str="for-code-addition.log"):
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
