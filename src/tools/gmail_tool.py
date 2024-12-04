from core.settings import settings
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import (
    build_resource_service,
    get_gmail_credentials,
)

credentials = get_gmail_credentials(
    service_account_file=settings.google_credentials_path,
    scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    use_domain_wide=True,
    delegated_user=settings.google_delegated_user
)
api_resource = build_resource_service(credentials=credentials)
toolkit = GmailToolkit(api_resource=api_resource)

gmail_tool = toolkit.get_tools()

