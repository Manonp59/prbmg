# Environment 

## Dependencies 

<code>pip install -r requirements-web_app.txt</code>

## Environment variables 

We need to ensure that environment variables are set up : 

- SECRET_KEY : to encrypt password ; 
- API_IA_SECRET_KEY : to request the API_IA ; 
- API_DATABASE_SECRET_KEY : to request the API_DATABASE ; 
- APPLICATIONINSIGHTS_CONNECTION_STRING : to monitor the application on Azure Monitor.

## Project structure 

```bash
web_app
│
├── prbmg/          # Django project directory
│   ├── __init__.py
│   ├── settings.py           # Project settings
│   ├── urls.py               # URL configurations
│   ├── wsgi.py               # WSGI application
│
├── clustering/                 # Django app directory
│   ├── __init__.py
│   ├── admin.py              # Admin configurations
│   ├── apps.py               # App configurations
│   ├── models.py             # Database models
│   ├── tests.py              # Application tests
│   ├── views.py              # Application views
│   ├── urls.py               # App URL configurations
│
├── manage.py                 # Django management script
├── requirements-web_app.txt  # Python dependencies
```

