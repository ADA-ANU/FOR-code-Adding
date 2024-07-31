import argparse
import pandas as pd
from datetime import datetime
from pathlib import Path

from util import get_csv_content, setup_logging

def main(csv: Path):
  """
  Given a valid csv, 
  """
  df = get_csv_content(csv)

if __name__=="__main__":
  parser = argparse.ArgumentParser(prog='Add-FOR-Codes', description='Will add FOR codes to dataverse datasets')
  
  parser.add_argument('csv', type=Path)                     # Preservation output location
  
  args = parser.parse_args()

  setup_logging(f"logs/preservation-{str(datetime.now().isoformat())}.log")
  main(**vars(args))