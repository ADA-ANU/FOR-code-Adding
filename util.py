import logging
import pandas as pd
from pathlib import Path

def get_csv_content(csv: Path):
  abs_csv = csv.absolute()

  if not csv.is_file():
    error = "Error, CSV ({0}) does not exist. Exiting script..."
    print(error.format(csv))
    logging.error(error.format(abs_csv))
    exit()

  if csv.suffix.lower()!=".csv": # rudimentary check
    error = "Error, the 'CSV' ({0}) does not have a '.csv' suffix. Exiting script..."
    print(error.format(csv))
    logging.error(error.format(abs_csv))
    exit()
  
  df = pd.read_csv(csv)
  logging.info(f"Read '.csv' ({abs_csv}), it was of size '{df.size}'.")
  return df
  

def setup_logging(filename: str="preservation-output.log"):
  """
  Sets up the log file to track the output of the script.

  Parameters:
    - filename  <str> : Sets the filename for the output file
  """
  parent = Path(filename).parent
  if not parent.exists():
    parent.mkdir(parents=True)

  logging.basicConfig(filename=filename, encoding="utf-8", level=logging.DEBUG)
  logging.info("Start FOR Code Additions")