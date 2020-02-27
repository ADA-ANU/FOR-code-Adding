import dotenv
import os
dotenv.load_dotenv()

CATEGORY_NEWPOST = "24"

CATEGORY_UPDATEDPOST = "25"

API_FETCHDATASET = 'https://dataverse-dev.ada.edu.au/api/datasets/:persistentId/?persistentId='

API_UPDATEDATASET = "https://dataverse-dev.ada.edu.au/api/datasets/:persistentId/versions/:draft?persistentId="

API_PUBLISHDATASET = "https://dataverse-dev.ada.edu.au/api/datasets/:persistentId/actions/:publish?persistentId="

API_DATAVERSES_PUBLISHDATASET = "https://dataverse-dev.ada.edu.au/api/datasets/"

API_DATAVERSES_CREATEDATASET = "https://dataverse-dev.ada.edu.au/api/dataverses/DEV-ADA/datasets/"


API_METABASE_AUTHENTICATION_HEADER = {
    'Content-Type': 'application/json'
}

API_METABASE_AUTHENTICATION_BODY = {
    "username": os.getenv("METABASE_USERNAME"),
    "password": os.getenv("METABASE_PASSWORD")
}

API_WP_AUTHENTICATION_HEADER = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

API_WP_POSTS_HEADER = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

API_WP_AUTHENTICATION_BODY = {
    "username": os.getenv("WP_USERNAME"),
    "password": os.getenv("WP_PASSWORD"),
    "issueJWT": "true"
}

API_WP_VALIDATE_HEADER = {
    'Content-Type': 'application/json'
}

API_WP_CREATEPOTS_HEADER = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

API_DATAVERSES_PUBLISHDATASET_HEADER = {
    "X-Dataverse-key": os.getenv("DATAVERSE_TOKEN")
}

dateDiff = 14

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

