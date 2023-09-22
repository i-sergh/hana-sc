from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta


from config import HANA_HOST, HANA_PASS, HANA_PORT, HANA_USER

HANA_URL = f'hana+hdbcli://{HANA_USER}:{HANA_PASS}@{HANA_HOST}:{HANA_PORT}'

Base: DeclarativeMeta = declarative_base()

engine = create_engine(HANA_URL)

SessionHana = sessionmaker(autoflush=False, bind=engine)

""" Inspector = inspect(engine) """

def get_session():
    with SessionHana() as session:
        yield session