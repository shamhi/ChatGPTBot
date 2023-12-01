from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Tokens
TOKEN1: str = str(getenv('TOKEN1'))
TOKEN2: str = str(getenv('TOKEN2'))
PAYMENTS_TOKEN: str = str(getenv('PAYMENTS_TOKEN'))
EDEN_API: str = str(getenv('EDEN_API'))

# Admin ids
IDS: list[int] = list(map(int, getenv('IDS').split(',')))


# PostgreSQL database
PG_HOST: str = str(getenv('PG_HOST'))
PG_PORT: int = int(getenv('PG_PORT'))
PG_USER: str = str(getenv('PG_USER'))
PG_PASSWORD: str = str(getenv('PG_PASSWORD'))
PG_DATABASE: str = str(getenv('PG_DATABASE'))

