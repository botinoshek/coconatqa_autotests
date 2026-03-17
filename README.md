# Cinescope Autotests

Проект автотестов для сервиса **Cinescope**. Включает API, UI и DB тесты, а также проверки сервисов-заглушек. Тесты написаны на Python с использованием pytest и вспомогательных утилит проекта.

## Стек

- Python
- pytest
- requests
- faker
- python-dotenv
- pydantic
- Playwright (UI)
- SQLAlchemy + psycopg2 (DB)
- Allure (отчеты)

## Быстрый старт

1. Создать и активировать виртуальное окружение.
2. Установить зависимости:

```bash
pip install -r requirements.txt
pip install pytest-playwright playwright sqlalchemy psycopg2-binary allure-pytest
playwright install
```

3. Подготовить `.env` файл (см. ниже).

## Переменные окружения (.env)

Пример набора переменных:

```
# Super admin для API/UI
SUPER_ADMIN_USERNAME=...
SUPER_ADMIN_PASSWORD=...

# UI
UI_URL=https://dev-cinescope.coconutqa.ru/
AUTH_URL=https://auth.dev-cinescope.coconutqa.ru/
UI_TIMEOUT_MS=30000

# DB
HOSTDB=...
PORTDB=...
NAMEDB=...
USERDB=...
PASSWORDDB=...

# Playwright (опционально)
PW_CHROMIUM_CHANNEL=chrome
PW_HEADLESS=true
```

Можно также использовать шаблон `.env.example`.

## Запуск тестов

Все тесты:
```bash
pytest
```

API тесты:
```bash
pytest tests/api
```

UI тесты:
```bash
pytest tests/ui
```

DB тесты:
```bash
pytest tests/db
```

Тесты сервисов-заглушек:
```bash
pytest tests/test_services
```

Маркерные прогоны (см. `pytest.ini`):
```bash
pytest -m smoke
pytest -m regression
pytest -m slow
pytest -m api
```

## Отчеты Allure (опционально)

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

## Структура проекта

```
.
├── api/                    # API-клиенты и менеджеры
├── config/                 # Настройки проекта (UI URL, timeout и т.д.)
├── constans/               # Роли и константы (опечатка в имени папки историческая)
├── constants.py            # Базовые URL и заголовки
├── custom_requester/       # Обертка над requests
├── db_models/              # SQLAlchemy модели
├── db_requester/           # DB-клиент и хелперы
├── entities/               # Доменные сущности
├── enums/                  # Перечисления
├── files/                  # Артефакты тестов (например, traces)
├── models/                 # Pydantic модели и Page Object Models
├── resources/              # Доступы/секреты, загружаемые из .env
├── tests/                  # Тесты
│   ├── api/                # API тесты
│   ├── db/                 # DB тесты
│   ├── test_services/      # Тесты сервисов-заглушек
│   └── ui/                 # UI тесты (Playwright)
├── utils/                  # Генераторы данных и фабрики
├── conftest.py             # Общие pytest фикстуры
├── pytest.ini              # Конфигурация pytest и маркеры
├── requirements.txt        # Базовые зависимости
└── README.md               # Документация
```

## Полезные замечания

- UI тесты используют Playwright. Браузеры скачиваются локально.
- Артефакты тестов (Playwright traces, allure-results, кэши) **не должны** попадать в git.
- Для стабильной работы UI тестов важно иметь корректный `UI_URL` и доступность стенда.

## CI (пример)

Ниже пример сценария для GitHub Actions (можно адаптировать под любой CI):

```yaml
name: tests
on: [push, pull_request]
jobs:
  pytest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install deps
        run: |
          python -m pip install -U pip
          pip install -r requirements.txt
          pip install pytest-playwright playwright sqlalchemy psycopg2-binary allure-pytest
          playwright install --with-deps
      - name: Run API tests
        run: pytest tests/api -m "api"
      - name: Run UI tests
        env:
          UI_URL: ${{ secrets.UI_URL }}
          AUTH_URL: ${{ secrets.AUTH_URL }}
          SUPER_ADMIN_USERNAME: ${{ secrets.SUPER_ADMIN_USERNAME }}
          SUPER_ADMIN_PASSWORD: ${{ secrets.SUPER_ADMIN_PASSWORD }}
          PW_HEADLESS: "true"
        run: pytest tests/ui
```

## Docker (локально)

Пример `docker-compose.yml` для локального запуска (адаптируйте под окружение):

```yaml
version: "3.9"
services:
  tests:
    image: python:3.11-slim
    working_dir: /app
    volumes:
      - .:/app
    environment:
      UI_URL: ${UI_URL}
      AUTH_URL: ${AUTH_URL}
      SUPER_ADMIN_USERNAME: ${SUPER_ADMIN_USERNAME}
      SUPER_ADMIN_PASSWORD: ${SUPER_ADMIN_PASSWORD}
      PW_HEADLESS: "true"
    command: >
      bash -lc "pip install -U pip &&
                pip install -r requirements.txt &&
                pip install pytest-playwright playwright sqlalchemy psycopg2-binary allure-pytest &&
                playwright install --with-deps &&
                pytest"
```

Запуск:
```bash
docker compose run --rm tests
```

## Allure в CI

Пример публикации отчёта как артефакта GitHub Actions:

```yaml
      - name: Run tests with Allure
        run: pytest --alluredir=allure-results
      - name: Upload Allure results
        uses: actions/upload-artifact@v4
        with:
          name: allure-results
          path: allure-results
```

---

