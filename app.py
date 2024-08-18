import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup
import re

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

def extract_amount_and_currency(total_value):
    """Extracts the dollar amount from the total_value string."""
    parts = total_value.split()  # Split the string by spaces
    if len(parts) >= 3:
        amount = f"{parts[-2]} {parts[-1]}"  # Combine the last two parts
        
        currency = amount[-3:]
        price = amount[0:-3]
        
        try:
            price = float(price.replace(',', '.'))
        except ValueError:
            price = 0
        
        return price, currency
    return 0, None

def extract_total(body):
    """Extract the total amount from 'Total' to the first occurrence of '$CA' in the email body."""
    soup = BeautifulSoup(body, 'html.parser')
    text = soup.get_text()
    
    text = text.strip()  # Removes any leading or trailing whitespace
    text = ' '.join(text.split())  # Normalize all whitespace to single spaces

    if "Total" in text and "$CA" in text:
        total_start = text.find("Total")  # Find the position of "Total"
        ca_end = text.find("$CA", total_start) + len("$CA")  # Find the position of "$CA" after "Total" and include "$CA" in the result
        total_value = text[total_start:ca_end]  # Slice the string from "Total" to the end of "$CA"
        #print(text)
        return extract_amount_and_currency(total_value)
    
    
    return 0, None

def extract_store(body):
    """Extract the total amount from 'Total' to the first occurrence of '$CA' in the email body."""
    soup = BeautifulSoup(body, 'html.parser')
    text = soup.get_text()
    
    text = text.strip()  # Removes any leading or trailing whitespace
    text = ' '.join(text.split())  # Normalize all whitespace to single spaces

    if "Vous avez commandé" in text and "." in text:
        total_start = text.find("Vous avez commandé")  # Find the position of "Total"
        ca_end = text.find(".", total_start) + len(".")  # Find the position of "$CA" after "Total" and include "$CA" in the result
        total_value = text[total_start:ca_end]  # Slice the string from "Total" to the end of "$CA"
        
        total_start2 = total_value.find("chez")  # Find the position of "Total"
        ca_end2 = total_value.find(".", total_start2) + len(".")  # Find the position of "$CA" after "Total" and include "$CA" in the result
        total_value2 = total_value[total_start2+5:ca_end2]  # Slice the string from "Total" to the end of "$CA"
        
        return total_value2
    
    return "Uber Ride"
    
    
    
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
        start= "2024/01/01"
        end= "2024/02/01"
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
