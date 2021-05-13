from __future__ import print_function
import pickle
import os
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaFileUpload, MediaIoBaseDownload
import io
from apiclient import errors
from apiclient import http
import logging

from apiclient import discovery
import unzip as UNZIP

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']


# To list folders
def listfolders(service, filid, des):
    results = service.files().list(
        pageSize=1000, q="\'" + filid + "\'" + " in parents",
        fields="nextPageToken, files(id, name, mimeType)").execute()
    # logging.debug(folder)
    folder = results.get('files', [])
    for item in folder:
        if str(item['mimeType']) == str('application/vnd.google-apps.folder'):
            if not os.path.isdir(des+"/"+item['name']):
                os.mkdir(path=des+"/"+item['name'])
            print(item['name'])
            listfolders(service, item['id'], des+"/"+item['name'])  # LOOP un-till the files are found
        else:
            downloadfiles(service, item['id'], item['name'], des)
            print(item['name'])
    return folder


# To Download Files
def downloadfiles(service, dowid, name,dfilespath):
    request = service.files().get_media(fileId=dowid)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with io.open(dfilespath + "/" + name, 'wb') as f:
        fh.seek(0)
        f.write(fh.read())

def load_files():
    """Shows basic usage of the Drive v3 API.
    Prints the names and ids of the first 10 files the user has access to.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('creds/token.pickle'):
        with open('creds/token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'creds/credentials.json', SCOPES)  # credentials.json download from drive API
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('creds/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('drive', 'v3', credentials=creds)
    # Call the Drive v3 API

    with open('folder_ID.txt') as f:
        Folder_id = f.read()
    # Specify folder location

    results = service.files().list(
        pageSize=1000, q=Folder_id+" in parents", fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])
    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            if item['mimeType'] != 'application/vnd.google-apps.folder':
                if not os.path.isdir("Data"):
                   os.mkdir("Data")
                bfolderpath = os.getcwd()+"/Data"

                names = str(item['name']).split('.')
                if len(names)!=2:
                    continue
                name = names[0]
                identifier = names[1]
               
                # if identifier != 'zip':
                #    continue
                
                # if os.path.isfile(os.getcwd()+"/Data/" + name.replace('clean-dataset','hydrated_tweets_short.json')):
                #     print(name + ' is already downloaded and unzipped!')
                #     continue

                # if os.path.isfile(os.getcwd()+"/Data/" + name+ '.zip'):
                #     print(name + ' is already downloaded but still zipped!')
                #     continue

                if os.path.isfile(os.getcwd()+"/Data/" + name+ '.csv'):
                    print(name + ' is already downloaded!')
                    continue

                print(name)

                filepath = bfolderpath #+ item['name']
                downloadfiles(service, item['id'], item['name'], filepath)
                UNZIP.unzip_files()

