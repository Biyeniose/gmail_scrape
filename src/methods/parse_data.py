from base64 import urlsafe_b64decode
from bs4 import BeautifulSoup


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
        
        # Extracts the dollar amount from the total_value string
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
        
        
        #return extract_amount_and_currency(total_value)
    
    
    return 0, None


def extract_store(body):
    """Extract the total amount from 'Total' to the first occurrence of '$CA' in the email body."""
    soup = BeautifulSoup(body, 'html.parser')
    text = soup.get_text()
    
    text = text.strip()  # Removes any leading or trailing whitespace
    # Normalize all whitespace to single spaces
    text = ' '.join(text.split()) 
    print(text) 

    if "Vous avez commandé" in text and "." in text:
        total_start = text.find("Vous avez commandé")  # Find the position of "Total"
        ca_end = text.find(".", total_start) + len(".")  # Find the position of "$CA" after "Total" and include "$CA" in the result
        total_value = text[total_start:ca_end]  # Slice the string from "Total" to the end of "$CA"
        
        total_start2 = total_value.find("chez")  # Find the position of "Total"
        ca_end2 = total_value.find(".", total_start2) + len(".")  # Find the position of "$CA" after "Total" and include "$CA" in the result
        total_value2 = total_value[total_start2+5:ca_end2]  # Slice the string from "Total" to the end of "$CA"
        
        return total_value2
    
    return "Uber Ride"