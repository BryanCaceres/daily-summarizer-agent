import logging
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)
from core.settings import settings

class GmailTool:
    def __init__(self):
        self.set_tool()
        if not settings.google_credentials:
            raise ValueError("Google credentials are not set in the environment variables")
        self.credentials = settings.google_credentials

    def set_tool(self):
        try:
            credentials = get_gmail_credentials(
            token_file="token.json",
            scopes=["https://mail.google.com/"],
            client_secrets_file=self.credentials,
            )
            api_resource = build_resource_service(credentials=credentials)
            toolkit = GmailToolkit(api_resource=api_resource)
            self.tool = toolkit.get_tools()

        except Exception as e:
            logging.error(f"Error al obtener credenciales: {e}")
            raise ValueError("Error en la configuración de Gmail") from e

gmail_tools = GmailTool().tool

# Can review scopes here https://developers.google.com/gmail/api/auth/scopes
# For instance, readonly scope is 'https://www.googleapis.com/auth/gmail.readonly'
