from googleapiclient.discovery import build
from base64 import urlsafe_b64decode, b64decode
from bs4 import BeautifulSoup
from src.creds import creds
import json
from datetime import datetime

service = build("gmail", "v1", credentials=creds)

msgs = service.users().messages()


def get_last_netflix_mail(from_email, subject=[]):
    from_query = f"to:{from_email}" if from_email else ""
    query = f"info@account.netflix.com {from_query} {"".join(subject)}"
    results = msgs.list(
        userId="me",
        q=query,
        maxResults=1,
    ).execute()
    messages = results.get("messages", [])

    for message in messages:
        msg = msgs.get(userId="me", id=message["id"]).execute()
        open("msg.json", "w").write(json.dumps(msg))
        part = next(
            part for part in msg["payload"]["parts"] if part["mimeType"] == "text/html"
        )
        timestamp_ms = msg.get("internalDate")
        date = datetime.fromtimestamp(int(timestamp_ms) / 1000)
        formatted_date = date.strftime("%d-%m-%Y %H:%M:%S")
        data = part["body"]["data"]

        try:
            content = urlsafe_b64decode(data).decode("utf-8", errors="ignore")
           #  open("content.txt", "w").write(content)
            html = BeautifulSoup(content, "lxml")
            link = html.select_one("td.h5.button-td > a").get("href")
        except Exception as e:
            print(e)
            # open("data.txt", "w").write(data)

        return link, formatted_date
