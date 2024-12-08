from core.settings import settings
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://mail.google.com/"
]

credentials = get_gmail_credentials(
    service_account_file=settings.google_credentials_path,
    scopes=SCOPES,
    use_domain_wide=True,
    delegated_user=settings.google_delegated_user
)
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)

gmail_toolkit = toolkit.get_tools()
