

from twilio.rest import Client
from twilio.request_validator import RequestValidator

import uuid
import requests
import os
BASE_DIR = os.getcwd()
DOC_DIR = os.path.join(BASE_DIR, 'document')
os.makedirs(DOC_DIR, exist_ok=True)

account_sid = "AC26778d96aa9dbb9ef3eff0d724482da2"
auth_token = "d22bac364143e6c089ba4aca2512b979"

async def download_image(media_url,phone_no):
  try:
    response = requests.get(media_url, auth=(account_sid, auth_token))
    unique_id = uuid.uuid4()
    filename = f"{phone_no}_{unique_id}.jpg"
    file_path = os.path.join(DOC_DIR, filename)
    if response.status_code == 200:
        with open(file_path, "wb") as f:
            f.write(response.content)
        print("Media downloaded successfully.")
        return file_path
    else:
        print(f"Failed to download media: {response.status_code} - {response.text}")
        return ""
  except Exception as e:
    print("Failed to download")
# download_image(media_url="https://api.twilio.com/2010-04-01/Accounts/AC26778d96aa9dbb9ef3eff0d724482da2/Messages/MM4b1bd0c123d522308baab4295f2611ba/Media/ME8e39aea444a1b484a4c9019f7f8d709f",
#                phone_no="987654390")

async def send_twilio(msg, sender):

    try:
        client = Client(account_sid, auth_token)

        message = client.messages.create(
            from_="whatsapp:+14142625304",
            body=msg,
            to=f"whatsapp:{sender}"
        )

        print(f"message.sid :{message.sid}")
        return message.sid
    except:
        print("Error: Twilio server issue")
        return None
# msg = """
# Hello how are you \n good to see you
# """
# sender="+918144792775"
# sid = send_twilio(msg, sender)
# print(sid)