def run_django():
    import os
    import sys
    from django.core.management import execute_from_command_line

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskify.settings')
    sys.argv = ['manage.py', 'runserver', '--noreload']
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    run_django()
