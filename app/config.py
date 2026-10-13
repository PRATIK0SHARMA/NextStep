from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ROOT / '.env'), extra='ignore')
    app_env: str = 'development'
    database_path: str = str(ROOT / 'data' / 'nextstep.sqlite3')
    public_origin: str = 'http://127.0.0.1:8000'
    access_code: str = ''
    llm_provider: str = 'demo'
    llm_base_url: str = 'http://127.0.0.1:11434'
    llm_model: str = ''
    llm_api_key: str = ''
    llm_timeout: float = 30
    session_days: int = 30

    def validate_release(self):
        if self.llm_provider not in {'demo', 'ollama', 'compatible'}:
            raise ValueError('LLM_PROVIDER must be demo, ollama, or compatible')
        if self.llm_provider != 'demo' and not self.llm_model:
            raise ValueError('Set LLM_MODEL for the selected provider')
        if self.app_env == 'production':
            if len(self.access_code) < 16:
                raise ValueError('Production requires ACCESS_CODE with at least 16 characters')
            if not self.public_origin.startswith('https://'):
                raise ValueError('Production requires an HTTPS PUBLIC_ORIGIN')

settings = Settings()
