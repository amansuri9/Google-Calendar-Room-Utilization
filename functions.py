from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.oauth2 import service_account
import googleapiclient.discovery
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import random
import argparse
import datetime as dt


# Defining the scopes and credentials to access the methods retrieving both rooms and events
google_scopes = ['https://www.googleapis.com/auth/calendar.readonly',
                 'https://www.googleapis.com/auth/admin.directory.user.readonly',
                 'https://www.googleapis.com/auth/admin.directory.resource.calendar.readonly',
                 'https://www.googleapis.com/auth/admin.directory.resource.calendar']
service_account_file = 'json_file'
creds = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=google_scopes)
delegated_credentials = creds.with_subject('service_account_email')


# # # #
# Function Name: get_rooms_df
# Inputs: No inputs
# Output: Returns a dataframe containing a JSON template for calendar resource list
# Description: Pulls the space's resources such as space capacity, type, description, email, id, etc.
# # # #
def get_rooms_df():
    # Setup and call the Calendar API
    calendar_rooms = build('admin', 'directory_v1', credentials=delegated_credentials)
    page_token = None
    df_rooms = pd.DataFrame()
    while True:
        rooms_result = calendar_rooms.resources().calendars().list(
                customer='my_customer',
                maxResults='50',
                pageToken=page_token).execute()
        for room in rooms_result['items']:
            df_per_room = json_normalize(room)
            df_rooms = df_rooms.append(df_per_room, ignore_index=True, sort=False)
        page_token = rooms_result.get('nextPageToken')
        if not page_token:
            break
    return df_rooms


def get_events_df(resourceEmail, time_max, time_min):
    # Setup and call the Calendar API
    calendar_events = build('calendar', 'v3', credentials=delegated_credentials)
    page_token = None
    df_events = pd.DataFrame()
    while True:
        events_result = calendar_events.events().list(
                calendarId=resourceEmail,
                timeMin=time_min,
                timeMax=time_max,
                maxResults='50',
                singleEvents=True,
                orderBy='startTime',
                pageToken=page_token,
                timeZone='America/New_York').execute()
        for event in events_result['items']:
            df_per_event = json_normalize(event)
            df_events = df_events.append(df_per_event, ignore_index=True, sort=False)
        page_token = events_result.get('nextPageToken')
        if not page_token:
             break
    return df_events
