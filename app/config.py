from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    PROJECT_ROOT: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    HTML_DOCS_PATH: str = os.getenv('HTML_DOCS_PATH')
    MARKDOWN_DOCS_PATH: str = os.getenv('MARKDOWN_DOCS_PATH')
    VECTOR_STORE_PATH: str = os.getenv('VECTOR_STORE_PATH')
    MODEL_SAVE_PATH: str = os.getenv("MODEL_SAVE_PATH")
    LOG_FILE_PATH: str = os.path.join(PROJECT_ROOT, "logs/app.log")

    # Download HTML Configuration
    EMAIL: str = os.getenv('EMAIL')
    API_TOKEN: str = os.getenv('API_TOKEN')
    BASE_URL: str = os.getenv('BASE_URL')

    # Model Configuration
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME")
    DEVICE: str = os.getenv("DEVICE")
    MODEL_TORCH_DTYPE: str = os.getenv("MODEL_TORCH_DTYPE")

    # Generation Parameters
    MAX_NEW_TOKENS: int = os.getenv("MAX_NEW_TOKENS")
    TEMPERATURE: float = os.getenv("TEMPERATURE")
    SIMILARITY_TOP_K: int = os.getenv("SIMILARITY_TOP_K")

    # API Configuration
    API_TITLE: str = os.getenv("API_TITLE")
    API_VERSION: str = os.getenv("API_VERSION")
    API_HOST: str = os.getenv("API_HOST")
    API_PORT: int = os.getenv("API_PORT")
    RELOAD_UVICORN: bool = os.getenv("RELOAD_UVICORN")

    def __init__(self, **values):
        super().__init__(**values)
        os.makedirs(os.path.dirname(self.LOG_FILE_PATH), exist_ok=True)
        os.makedirs(self.VECTOR_STORE_PATH, exist_ok=True)
        os.makedirs(self.MODEL_SAVE_PATH, exist_ok=True)
        os.makedirs(self.HTML_DOCS_PATH, exist_ok=True)
        os.makedirs(self.MARKDOWN_DOCS_PATH, exist_ok=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()