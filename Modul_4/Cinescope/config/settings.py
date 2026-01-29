import os
from dotenv import load_dotenv
load_dotenv()


def _norm_url(url: str) -> str:
    if not url:
        raise ValueError("URL is empty")
    return url.rstrip("/") + "/"


class Settings:
    def __init__(self):
        # UI (Playwright)
        self.base_url = _norm_url(os.getenv("UI_URL", "https://dev-cinescope.coconutqa.ru/"))
        # AUTH домен для cookie (requests -> playwright cookies)
        self.auth_url = _norm_url(os.getenv("AUTH_URL", "https://auth.dev-cinescope.coconutqa.ru/"))
        # дефолтный таймаут UI
        self.ui_timeout_ms = int(os.getenv("UI_TIMEOUT_MS", "30000"))


settings = Settings()