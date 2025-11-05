@echo off
set DJANGO_DEBUG=True
set DJANGO_SECRET_KEY=django-insecure-placeholder-secret-key-change-me
python -m daphne -b 0.0.0.0 -p 8000 app_passify.asgi:application