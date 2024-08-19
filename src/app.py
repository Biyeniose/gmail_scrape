import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup
import re
from methods.parse_data import get_email_body, extract_total, extract_store

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

    
def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    prices = []
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build("gmail", "v1", credentials=creds)
        
        # Define the query to search for emails
        start= "2024/06/01"
        end= "2024/06/21"
        query = f'subject:Uber after:{start} before:{end}'
        
        # Get the list of messages matching the query
        results = service.users().messages().list(userId="me", q=query).execute()
        messages = results.get("messages", [])

        if not messages:
            print("No emails found.")
            return

        print(f"Found {len(messages)} email(s):")
        for msg in messages:
            # Get the email details
            message = service.users().messages().get(userId="me", id=msg['id']).execute()
            headers = message.get('payload', {}).get('headers', [])
            subject = next(header['value'] for header in headers if header['name'] == 'Subject')
            date = next(header['value'] for header in headers if header['name'] == 'Date')
            #print(f"\nSubject: {subject}, Date: {date}")
            print(f"\nDate: {date}")
            print(f"Subject: {subject}")
            
            if "Uber Holdings" in subject:
                continue

            # Extract the body of the email
            body = get_email_body(message)
            if body:
                # Extract and print the total amount
                amount, curr = extract_total(body)
                #amount = extract_total(body)
                store = extract_store(body)
                print(f"Total Amount: {amount}")
                print(f"Currency: {curr}")
                print(f"Store: {store}")
                prices.append(amount)
                
                
            else:
                print("No body content found.")
                
            

    except HttpError as error:
        # Handle errors from Gmail API
        print(f"An error occurred: {error}")
        
    print(f"\nTotal Spent from {start} to {end} is:")
    print(f'{sum(prices)}')

if __name__ == "__main__":
    main()
