from googleapiclient.discovery import build
import base64
from bs4 import BeautifulSoup
from src.creds import creds
import json

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

        data = part["body"]["data"]
        content = base64.urlsafe_b64decode(data).decode("utf-8")
        open("content.txt", "w").write(content)
        html = BeautifulSoup(content, "lxml")
        link = html.select_one("td.h5.button-td > a").get("href")
        return link
