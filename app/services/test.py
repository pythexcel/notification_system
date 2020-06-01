import os
from dotenv import load_dotenv
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')
dotenv_path = os.path.join(APP_ROOT, '.env')
# print(dotenv_path)
load_dotenv(dotenv_path)
def func():
    print(os.getenv('a'))

func()