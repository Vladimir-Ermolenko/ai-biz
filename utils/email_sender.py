import base64
import pickle
import os
from typing import Dict
from logging import Logger

from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from requests import HTTPError


class EmailSender:
    def __init__(self, config: Dict[str, str], logger: Logger):
        self.config = config
        self.logger = logger

        self.SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

        creds = None
        if os.path.exists("token.pickle"):
            with open("token.pickle", "rb") as token:
                creds = pickle.load(token)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.config.get("CRED_PATH"), self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        self.service = build("gmail", "v1", credentials=creds)

    async def send_tw_link(self, email: str, product: str, product_link: str):
        product_name = product.replace("+", " ")

        message = MIMEText(self.config.get("EMAIL_TW_BODY").format(
            product_name=product_name,
            product_link=product_link))
        message["to"] = email
        message["subject"] = self.config.get("EMAIL_TW_SUBJECT").format(product_name=product_name)
        create_message = {"raw": base64.urlsafe_b64encode(message.as_bytes()).decode()}

        try:
            self.service.users().messages().send(userId="me", body=create_message).execute()
            self.logger.info(f"Sent link to {product_name} to {email}.")
        except HTTPError as error:
            self.logger.info(f"An error occurred when sending link to {product_name} to {email}: {str(error)}")
