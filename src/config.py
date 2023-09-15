from dotenv import load_dotenv
import os

load_dotenv()

PG_USER = os.environ.get('PG_USER')
PG_PASS = os.environ.get('PG_PASS')
PG_HOST = os.environ.get('PG_HOST')
PG_PORT = os.environ.get('PG_PORT')
PG_NAME = os.environ.get('PG_NAME')

HANA_USER = os.environ.get('HANA_USER')
HANA_PASS = os.environ.get('HANA_PASS')
HANA_HOST = os.environ.get('HANA_HOST')
HANA_PORT = os.environ.get('HANA_PORT')


