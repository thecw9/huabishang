import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


KAFKA_BOOTSTRAP_SERVERS = os.environ["KAFKA_BOOTSTRAP_SERVERS"]
KAFKA_REALDATA_TOPIC = os.environ["KAFKA_REALDATA_TOPIC"]

POSTGRES_HOST = os.environ["DATASOURCE_POSTGRES_HOST"]
POSTGRES_PORT = os.environ["DATASOURCE_POSTGRES_PORT"]
POSTGRES_DB = os.environ["DATASOURCE_POSTGRES_DB"]
POSTGRES_USER = os.environ["DATASOURCE_POSTGRES_USER"]
POSTGRES_PASSWORD = os.environ["DATASOURCE_POSTGRES_PASSWORD"]
POSTGRES_URI = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(POSTGRES_URI, echo=False)