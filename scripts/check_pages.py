import os
import sys
import django

# Ensure project root is on sys.path so `kavod` settings module can be imported
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kavod.settings')
django.setup()

from django.test import Client

client = Client()

def check(path):
    # Provide a host header to avoid DisallowedHost in test client
    resp = client.get(path, HTTP_HOST='127.0.0.1')
    print(path, resp.status_code)
    try:
        text = resp.content.decode('utf-8')
    except Exception:
        text = repr(resp.content)
    print(text[:800])

if __name__ == '__main__':
    check('/admissions/')
    print('\n' + '='*60 + '\n')
    check('/exams/')
