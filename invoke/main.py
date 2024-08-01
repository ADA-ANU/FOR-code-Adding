import logging
from requests import Request
from requests_toolbelt import sessions

def create_session(dataverse: str, api_key: str):
  """
  Creates a reusable request session to not have to pass the API key and base url to every function.

  Parameters:
    - dataverse  <string> : the base dataverse url
    - api_key    <string> : the unique access key to utilise Dataverse headlessly

  Return: <BaseUrlSession>

  """
  session = sessions.BaseUrlSession(base_url=dataverse)
  session.headers.update({"X-Dataverse-key": api_key})
  return session

def create_request(session: sessions.BaseUrlSession, request: Request):
  """
  Utilises the BaseUrlSession class to send a particular request.

  Parameters:
    - session    <sessions.BaseUrlSession> : Reusable class that has base url and api key
    - request    <Request>                 : The request which 

  Return: requests.Response <class>
  
  """
  prepared_request = session.prepare_request(request)
  return session.send(prepared_request)

def request_dataset(session: sessions.BaseUrlSession, doi: str):
  response = create_request(session, Request(method='GET', url=f'/api/datasets/:persistentId/?persistentId={doi}'))
  if not response.ok or'application/json' not in response.headers.get('Content-Type', '') :
    logging.error(f"Failed to get dataset metadata for DOI '{doi}' - Status Code: {response.ok}, Response: {response.text}")
    return {}
  return response.json().get("data", {})

def update_dataset(session: sessions.BaseUrlSession, doi: str, json: dict):
  response = create_request(session, Request(method="PUT", url=f"/api/datasets/:persistentId/metadata?persistentId={doi}&replace=false", json=json, headers={"Content-Type": "application/ld+json"}))
  if not response.ok:
    logging.error(f"Failed to PUT new json metadata into '{doi}' - Status Code: {response.ok}, Response: {response.text}")
    return {}
  return response.json().get("data", {})