import gspread
import os

CREDENTIALS_FILE = "/home/bucketlister/Desktop/iayyyyy/youcode-ai-agent/youcode-383711-be6f512e7af2.json"

try:
    gc = gspread.service_account(filename=CREDENTIALS_FILE)
    sh = gc.create("YouCode AI Data Store")
    # Share it so anyone with the link can view it, or we can just ask the user for their email
    sh.share(None, perm_type='anyone', role='writer')
    print("SPREADSHEET_ID:", sh.id)
    print("URL:", sh.url)
except Exception as e:
    print("Error:", e)
