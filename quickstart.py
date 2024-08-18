import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_email_body(message):
    """Extract the body from the message payload."""
    parts = message.get('payload', {}).get('parts', [])
    body = None

    if not parts:
        # If there are no parts, the body might be directly in the payload
        body = message.get('payload', {}).get('body', {}).get('data')
    else:
        for part in parts:
            # Look for the plain text or HTML part
            if part['mimeType'] == 'text/plain':
                body = part.get('body', {}).get('data')
                break
            elif part['mimeType'] == 'text/html':
                body = part.get('body', {}).get('data')

    if body:
        # Decode the base64 encoded email body
        body = urlsafe_b64decode(body).decode('utf-8')
        return body
    return None

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
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
        query = 'subject:Uber after:2024/07/25 before:2024/08/01'
        
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
            print(f"\nSubject: {subject}, Date: {date}")

            # Extract the body of the email
            body = get_email_body(message)
            if body:
                print("\nEmail Body:\n")
                # If the body is HTML, you might want to clean it up for display
                if message.get('payload', {}).get('mimeType') == 'text/html' or 'text/html' in [part['mimeType'] for part in message.get('payload', {}).get('parts', [])]:
                    # Parse the HTML content to get text
                    soup = BeautifulSoup(body, 'html.parser')
                    print(soup.get_text())
                else:
                    print(body)
            else:
                print("No body content found.")

    except HttpError as error:
        # Handle errors from Gmail API
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    main()
