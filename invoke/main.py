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
    - session    <sessions.BaseUrlSession> : Reusable class that includes the Dataverse base url and api key in every request
    - request    <Request>                 : The request which wants to be sent using the session

  Return: <requests.Response>
  
  """
  prepared_request = session.prepare_request(request)
  return session.send(prepared_request)

def request_dataset(session: sessions.BaseUrlSession, doi: str):
  """
  Given a DOI, get the given dataset's metadata.

  Parameters:
    - session    <sessions.BaseUrlSession> : Reusable class that includes the Dataverse base url and api key in every request

  Returns: <dict>

  """
  response = create_request(session, Request(method='GET', url=f'/api/datasets/:persistentId/?persistentId={doi}'))
  if not response.ok or'application/json' not in response.headers.get('Content-Type', '') :
    logging.error(f"Failed to get dataset metadata for DOI '{doi}' - Status Code: {response.ok}, Response: {response.text}")
    return {}
  return response.json().get("data", {}), response.ok

def update_dataset(session: sessions.BaseUrlSession, doi: str, json: dict):
  """
  Given a DOI, update the given dataset's metadata.

  Parameters:
    - session    <sessions.BaseUrlSession> : Reusable class that includes the Dataverse base url and api key in every request

  Returns: <dict>
  
  """
  response = create_request(session, Request(method="PUT", url=f"/api/datasets/:persistentId/metadata?persistentId={doi}&replace=false", json=json, headers={"Content-Type": "application/ld+json"}))
  if not response.ok:
    logging.error(f"Failed to PUT new json metadata into '{doi}' - Status Code: {response.ok}, Response: {response.text}")
    return {}
  return response.json().get("data", {})

def publish_dataset(session: sessions.BaseUrlSession, doi: str, release_type: str = "minor"):
  """
  
  """
  response = create_request(session, Request(method="POST", url=f"/api/datasets/:persistentId/actions/:publish?persistentId={doi}&type={release_type}"))