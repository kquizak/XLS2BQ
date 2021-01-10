from __future__ import print_function
from googleapiclient.discovery import build
import os
from oauth2client import file, client, tools
from google.cloud import storage


SCOPES = ['profile', 'email','https://www.googleapis.com/auth/gmail.modify']

PROJECT_ID = os.getenv('PROJECT_ID', '<MY PROJECT>')
TOPIC = os.getenv('TOPIC', '<YOUR PUBSUB TOPIC NAME>')
BUCKET_NAME = os.getenv('BUCKET_NAME', '<YOUR BUCKET NAME HERE>')
STORE_NAME = os.getenv('STORE_NAME', '<SOME JSON FILE THAT STORES THE TOKEN>')
CLIENT_ID = os.getenv('CLIENT_ID', '<YOUR OAUTH CLIENT ID JSON>')


def main():
    """Pushes new email notification to pub/sub $TOPIC using Gmail API.
    """
    
    store = file.Storage(STORE_NAME)
    creds = store.get()
    # If there are no (valid) credentials available, let the user log in.
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_ID, SCOPES)
        creds = tools.run_flow(flow, store)
        
        gcs = storage.Client()
        print(f'client={gcs}')
        bucket = gcs.get_bucket(BUCKET_NAME) 
        print(f'bucket={bucket}')
        blob2 = bucket.blob(STORE_NAME)
        blob2.upload_from_filename(filename=STORE_NAME)
        

    service = build('gmail', 'v1', credentials=creds)

    # test connection
    result = service.users().getProfile(userId='me').execute()
    address = result.get('emailAddress')
    print(f'connected to {address} inbox')


    # create listener in pubsub for INBOX label
    # gmail sends a message like {emailAddress: INBOX@gmail.com, historyId: 4673254}  to pub/sub
    request = {
    'labelIds': ['UNREAD'],
    'topicName': f'projects/{PROJECT_ID}/topics/{TOPIC}'
    }
    service.users().watch(userId='me', body=request).execute()

    
if __name__ == '__main__':
    main()