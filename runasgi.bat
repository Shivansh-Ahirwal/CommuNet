set DJANGO_SETTINGS_MODULE=config.settings
uvicorn config.asgi:application --host 0.0.0.0 --port 8000