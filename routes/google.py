from fastapi import FastAPI, Depends, HTTPException, Request, APIRouter
from fastapi.responses import RedirectResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from dotenv import load_dotenv
import json

import os
load_dotenv()

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

router = APIRouter()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
SCOPES = [os.getenv("GOOGLE_SCOPES")]
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
if GOOGLE_CLIENT_SECRET is None:
    raise ValueError("Client secret JSON not found in environment variables")
GOOGLE_CLIENT_SECRET_JSON = json.loads(GOOGLE_CLIENT_SECRET)

user_credentials = {}

@router.get("/loginGoogle")
def login_with_google():
    flow = Flow.from_client_config(
        GOOGLE_CLIENT_SECRET_JSON,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, state = flow.authorization_url(access_type="offline", include_granted_scopes="true")
    return RedirectResponse(auth_url)

@router.get("/auth/google/callback")
async def auth_callback(request: Request):
    authorization_response = str(request.url)
    
    flow = Flow.from_client_config(
        GOOGLE_CLIENT_SECRET_JSON, 
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = flow.credentials
    user_id = "unique_user_id"
    user_credentials[user_id] = credentials.to_json()
    return { "message": "Authorization successful, credentials stored for user."}

@router.get("/events")
async def get_events(user_id: str):
    if user_id not in user_credentials:
        raise HTTPException(status_code=401, detail="User not authenticated")
    
    creds = Credentials.from_authorized_user_info(user_credentials[user_id])
    service = build("calendar", "v3", credentials=creds)
    
    events_result = service.events().list(calendarId="primary", maxResults=10, singleEvents=True, orderBy="startTime").execute()
    events = events_result.get("items", [])
    
    return {"events": events}