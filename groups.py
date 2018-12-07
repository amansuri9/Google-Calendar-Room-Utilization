from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from google.oauth2 import service_account
import googleapiclient.discovery
import datetime
import pandas as pd
import json
from pandas.io.json import json_normalize
import numpy as np


# Defining the scopes and credentials to access the methods retrieving both groups and members
google_scopes = ['https://www.googleapis.com/auth/admin.directory.group.readonly',
                 'https://www.googleapis.com/auth/admin.directory.group',
                 'https://www.googleapis.com/auth/admin.directory.group.member.readonly',
                 'https://www.googleapis.com/auth/admin.directory.group.member']
service_account_file = 'json_file'
creds = service_account.Credentials.from_service_account_file(
        service_account_file, scopes=google_scopes)
delegated_credentials = creds.with_subject('service_account_email')

def get_groups_df():
    # Setup and call the Calendar API
    calendar_groups = build('admin', 'directory_v1', credentials=delegated_credentials)
    page_token = None
    df_groups = pd.DataFrame()
    while True:
        groups_result = calendar_groups.groups().list(
                customer='my_customer',
                orderBy='email',
                pageToken=page_token).execute()
        for group in groups_result['groups']:
            df_per_group = json_normalize(group)
            df_groups = df_groups.append(df_per_group, ignore_index=True)
        page_token = groups_result.get('nextPageToken')
        if not page_token:
            break
    return df_groups


def get_members_df(group_id):
    # Setup  and call the Calendar API
    calendar_members = build('admin', 'directory_v1', credentials=delegated_credentials)
    page_token = None
    df_members = pd.DataFrame()
    while True:
        members_result = calendar_members.members().list(
                groupKey=group_id,
                pageToken=page_token).execute()
        for group_members in members_result['members']:
            df_per_member = json_normalize(group_members)
            df_per_member['groupid'] = group_id
            df_members = df_members.append(df_per_member, ignore_index=True)
        page_token = members_result.get('nextPageToken')
        if not page_token:
            break
    return df_members


if __name__ == "__main__":

    # Step 1: Calling method get_groups_df that gets groups info
    # Then places to a dataframe that outputs to a csv file called groups.csv
    df_groups = get_groups_df()
    df_groups['directMembersCount'] = df_groups['directMembersCount'].replace('0', np.NaN)
    # Drops groups that do not have any members
    df_groups = df_groups.dropna(subset=['directMembersCount'])
    df_groups = df_groups.rename(columns={'directMembersCount' : 'groupCount'})
    df_groups = df_groups.rename(columns={'email' : 'groupEmail'})
    df_groups = df_groups.rename(columns={'id' : 'groupId'})
    df_groups = df_groups.rename(columns={'name' : 'groupName'})
    df_groups = df_groups[['groupCount',
                           'groupEmail',
                           'groupId',
                           'groupName',
                           'nonEditableAliases']]
    df_groups.to_csv('groups2.csv', index=False)


    # Step 2: Calling method get_members_df that gets members info
    # Then places to a dataframe that outputs to a csv file called members.csv
    df_members = pd.DataFrame()
    for group_id in df_groups['groupId']:
        df_per_group = get_members_df(group_id)
        df_members = df_members.append(df_per_group, ignore_index=False)
    df_members = df_members.rename(columns={'email' : 'memberEmail'})
    df_members = df_members.rename(columns={'groupid' : 'groupId'})
    df_members = df_members.rename(columns={'status' : 'memberStatus'})
    df_members = df_members[['memberEmail',
                             'groupId',
                             'id',
                             'memberStatus']]
    df_members.to_csv('members2.csv', index=False)

    # Step 3: Merges both dataframes of groups and members to have all information.
    df_memebers_groups = pd.merge(df_members, df_groups, on='groupId')
    df_memebers_groups = df_memebers_groups[['memberEmail',
                                             'groupId',
                                             'id',
                                             'memberStatus',
                                             'groupEmail',
                                             'groupName',
                                             'nonEditableAliases']]
    df_memebers_groups.to_csv('groups_and_members2.csv', index=False)
