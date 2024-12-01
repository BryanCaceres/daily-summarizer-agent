import os

class Settings:
    def __init__(self):
        self.default_language = "Spanish"
        self.default_max_tokens = os.getenv("DEFAULT_MAX_TOKENS")
        self.default_open_ai_model = os.getenv("DEFAULT_OPEN_AI_MODEL")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.default_temperature = os.getenv("DEFAULT_TEMPERATURE")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
        self.build_google_credentials()


    def build_google_credentials(self):
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        project_id = os.getenv("GOOGLE_PROJECT_ID")
        auth_uri = os.getenv("GOOGLE_AUTH_URI")
        token_uri = os.getenv("GOOGLE_TOKEN_URI")
        auth_provider_x509_cert_url = os.getenv("GOOGLE_AUTH_PROVIDER_X509_CERT_URL")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        self.google_credentials = {
            "web": {
                "client_id": client_id,
                "project_id": project_id,
                "auth_uri": auth_uri,
                "token_uri": token_uri,
                "auth_provider_x509_cert_url": auth_provider_x509_cert_url,
                "client_secret": client_secret
            }
        }

settings = Settings()
        

