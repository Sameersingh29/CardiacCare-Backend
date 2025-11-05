How to run the backend?

1. Ensure you have pip $ python version 3.11.4 or higher
2. Create and activate a virtual env (Example - python -m venv .venv -> .venv\Scripts\Activate.ps1)
3. Run pip install -r .\requirement.txt
4. Download mySQL and setup your account there
5. Goto cad_predictor/settings.py -> DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'CardiacCare',
        'USER': '<your_userID>',
        'PASSWORD': '<your_pass>',
        'HOST': 'localhost',  # Or the MySQL server IP address
        'PORT': '3306',  # Default MySQL port
    }
}
6. Run -> python manage.py makemigrations
7. Run -> python manage.py migrate
8. Run -> python manage.py runserver 8000