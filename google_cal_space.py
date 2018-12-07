from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import json
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import random
import argparse
import datetime as dt
from functions import get_events_df, get_rooms_df


if __name__ == "__main__":


    # Step 1: Calling method get_rooms_df from functions.py that gets rooms info
    # Then places to a dataframe that outputs to a csv file called rooms.csv
    print('Started rooms.csv at ', datetime.now().isoformat())
    df_rooms = get_rooms_df()
    df_rooms = df_rooms[['capacity',
                         'generatedResourceName',
                         'resourceCategory',
                         'resourceDescription',
                         'resourceEmail',
                         'resourceId']]
    df_rooms = df_rooms[df_rooms['resourceCategory'].str.contains(
            "CONFERENCE_ROOM")]
    df_rooms = df_rooms.rename(columns={'capacity' : 'spaceCapacity'})
    df_rooms = df_rooms.rename(columns={'generatedResourceName' : 'googleSpaceName'})
    df_rooms = df_rooms.rename(columns={'resourceCategory' : 'googleSpaceCategory'})
    df_rooms = df_rooms.rename(columns={'resourceEmail' : 'googleSpaceEmail'})
    df_rooms = df_rooms.rename(columns={'resourceId' : 'googleSpaceId'})
    df_rooms['buildingNumber'] = df_rooms['resourceDescription'].str.split('-').str.get(0)
    df_rooms['spaceNumber'] = df_rooms['resourceDescription'].str.split('-').str.get(1)
    df_rooms = df_rooms.drop(columns=['resourceDescription'])
    # Adding "|" pipe separator since commas are filled throughout all of columns.
    # Use pipe filter to not run into data issues
    df_rooms['googleSpaceName'] = df_rooms['googleSpaceName'].str.replace('|', ' ')
    df_rooms['googleSpaceName'] = df_rooms['googleSpaceName'].str.replace(',', ' ')
    df_rooms.to_csv('rooms.csv', sep='|', index=False)
    print('Completed with rooms.csv at ', datetime.now().isoformat())


    # Step 2: Adding arguments for start and stop date of events.
    # The events on the start date are included while the events on the end date are not included.
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', type=lambda d: datetime.strptime(d, '%Y-%m-%d'))
    parser.add_argument('-e', type=lambda d: datetime.strptime(d, '%Y-%m-%d'))
    args = parser.parse_args()
    time_max = args.e.isoformat('T') + "Z"
    time_min = args.s.isoformat('T') + "Z"


    # Step 3: Calling method get_events_df that gets the events from functions.py
    # Then places to a dataframe that outputs to a csv file called events.csv
    # print('Started events.csv at ', datetime.now().isoformat())
    df_events = pd.DataFrame()
    for resourceEmail in df_rooms['googleSpaceEmail']:
        df_per_event = get_events_df(resourceEmail, time_max, time_min)
        df_events = df_events.append(df_per_event, ignore_index=True, sort=False)
    # Autofills the 'visibility' column's empty rows with 'not private'
    # Since visibility only prints if meetings are private
    df_events['summary'] = df_events['summary'].replace(np.NaN, 'events')
    df_events['visibility'] = df_events['visibility'].replace(np.NaN, 'not private')
    df_events = df_events[['summary',
                           'id',
                           'attendees',
                           'start.dateTime',
                           'end.dateTime',
                           'visibility']]
    df_events = df_events.dropna(subset=['attendees'])
    df_events = df_events.drop_duplicates('id')
    df_events = df_events.rename(columns={'summary' : 'eventName'})
    df_events = df_events.rename(columns={'id' : 'eventId'})
    df_events = df_events.rename(columns={'visibility' : 'meetingVisibility'})
    df_events['eventDate'] = df_events['start.dateTime'].str.split('T').str.get(0)
    df_events['eventDate'] = df_events['eventDate'].astype('datetime64[ns]')
    df_events['eventStartTime'] = df_events['start.dateTime'].str.split('T').str.get(1)
    df_events['eventStartTime'] = df_events['eventStartTime'].astype(str).str[:-6]
    df_events['eventEndTime'] = df_events['end.dateTime'].str.split('T').str.get(1)
    df_events['eventEndTime'] = df_events['eventEndTime'].astype(str).str[:-6]
    df_events = df_events.drop(columns=['start.dateTime'])
    df_events = df_events.drop(columns=['end.dateTime'])
    # Adding "|" pipe separator since commas are filled throughout all of columns.
    # Use pipe filter to not run into data issues
    # Replace events name that have commas or pipes so there isn't confusion when separating columns
    df_events['eventName'] = df_events['eventName'].str.replace('|', ' ')
    df_events['eventName'] = df_events['eventName'].str.replace(',', ' ')
    # Commented file output for events out since pipe separator is not working with the attendees column
    # df_events.to_csv('events.csv', sep='|', index=False)
    # print('Completed events.csv at ', datetime.now().isoformat())

    # Step 4: Creating a dataframe for the invitees and resourceEmail(rooms ID) since events.csv is nested
    # Only wants the attendees column from the events.csv
    # df_per_attendee contains information of only the atteendees column
    # df_row contains information of the other columns in events such as eventname, id, etc .
    print('Started invitees.csv at ', datetime.now().isoformat())
    df_attendees = pd.DataFrame()
    for index, row in df_events.iterrows():
        df_per_attendee = json_normalize(row['attendees'])
        df_row = row.to_frame()
        df_row= df_row.reset_index()
        df_row= df_row.rename(columns={df_row.columns[0]: "fields",
                                       df_row.columns[1]: "values"})
        df_row = df_row.pivot(index=None,
                              columns='fields',
                              values='values').bfill().iloc[[0],:]
        df_row['key'] = 1
        df_per_attendee['key'] = 1
        df_per_attendee = pd.merge(df_per_attendee, df_row, on='key')
        df_attendees = df_attendees.append(df_per_attendee, ignore_index=True, sort=False)
    df_attendees = df_attendees[['eventName','email', 'responseStatus', 'eventId']]
    df_attendees_copy = df_attendees.copy(deep=True)


    # Step 5: Getting googleSpaceEmail(rooms ID) of the events and merging with rooms.csv
    # Drops the invitees since googleSpaceEmail and invitees are both under the same 'attendees' column
    # Then merges with the attendees dataframe(df_attendees)
    df_attendees = df_attendees[df_attendees['email'].str.contains(
            "@resource.calendar.google.com")]
    df_attendees = df_attendees.rename(columns={'email' : 'googleSpaceEmail'})
    resource_email = pd.merge(df_attendees, df_rooms, how='left', on='googleSpaceEmail')


    # Step 6: Drops the rooms googleSpaceEmail(rooms ID) to have invitees only since they're both under 'atteendees' column.
    # Then merges with previous googleSpaceEmail df(resource_email) to have the googleSpaceEmail(room ID) and attendees in separate columns
    df_attendees_copy = df_attendees_copy[df_attendees_copy.email.str.contains(
            "@resource.calendar.google.com") == False]
    df_attendees_copy = df_attendees_copy.rename(columns={'email' : 'inviteeEmail'})
    invitees = pd.merge(resource_email, df_attendees_copy, how='left', on='eventId')


    # Step 7: Merging df invitees(invitees) with original df(df_events) to have all the categories(to include columns from rooms.csv).
    # Then grouping by categories to get the response status and outputs it to invitee_aggregated.csv
    df_events_and_rooms = pd.merge(df_events, invitees, how='left', on='eventId')
    df_events_and_rooms = df_events_and_rooms.drop(columns=['attendees',
                                                            'eventName_x',
                                                            'eventName_y',
                                                            'responseStatus_x'])
    df_events_and_rooms = df_events_and_rooms.rename(columns={'spaceCapacity' : 'eventCapacity'})
    df_events_and_rooms = df_events_and_rooms.rename(columns={'responseStatus_y' : 'responseStatus'})
    # Adding "|" pipe separator since commas are filled throughout all of columns.
    # Use pipe filter to not run into data issues
    df_events_and_rooms['eventName'] = df_events_and_rooms['eventName'].str.replace('|', ' ')
    df_events_and_rooms['eventName'] = df_events_and_rooms['eventName'].str.replace(',', ' ')
    df_events_and_rooms.to_csv('invitee.csv', sep='|', index=False)
    print('Completed invitees.csv at ', datetime.now().isoformat())
    print('Started invitees_aggreggated.csv at ', datetime.now().isoformat())
    df_combined_results = df_events_and_rooms.groupby(['eventName',
                                                       'eventId',
                                                       'eventDate',
                                                       'eventStartTime',
                                                       'eventEndTime',
                                                       'meetingVisibility',
                                                       'googleSpaceEmail',
                                                       'eventCapacity',
                                                       'googleSpaceName',
                                                       'googleSpaceCategory',
                                                       'buildingNumber',
                                                       'spaceNumber',
                                                       'googleSpaceId',
                                                       'responseStatus'])
    df_combined_results = df_combined_results.size().reset_index(
            name='attendeesResponse')
    # Adding "|" pipe separator since commas are filled throughout all of columns.
    # Use pipe filter to not run into data issues
    df_combined_results['eventName'] = df_combined_results['eventName'].str.replace('|', ' ')
    df_combined_results['eventName'] = df_combined_results['eventName'].str.replace(',', ' ')
    df_combined_results.to_csv('invitee_aggregated.csv', sep='|', index=False)
    print('Completed invitees_aggreggated.csv at ', datetime.now().isoformat())
