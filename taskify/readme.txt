-Import the database in your pc and configure it in taskify settings.py if needed
                or
-You can register your own new database and configure it in settings.py

1- Install Required Packages
        Run:
            pip install -r requirements.txt
2- Set Up the Database
        Run:
            python manage.py makemigrations
            python manage.py migrate
3- Create a Superuser (Admin Account) to access the django admin panel and seed a admin in Signupusers
        Run:
            python manage.py createsuperuser
4- Run Work hours time tracking checks within office hours
        Run:
            python manage.py check_office_hours
5- Run Daphne Server(this command is valid from project global directory where manage.py file is placed)
        Run: 
            daphne -p 8000 taskify.asgi:application 
6- Run Django App Server
        Run:
            python mnaage.py runserver

