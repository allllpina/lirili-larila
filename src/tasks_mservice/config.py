import os
from os.path import dirname, join

from dotenv import load_dotenv

path = join(dirname(__file__), ".env")
res = load_dotenv(dotenv_path=path)
if res:
    DATABASE_HOST = os.environ.get("DATABASE_HOST")
    DATABASE_PORT = os.environ.get("DATABASE_PORT")
    DATABASE_NAME = os.environ.get("DATABASE_NAME")
else:
    raise EnvironmentError("Unable to load environmental variables")
