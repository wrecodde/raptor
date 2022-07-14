
from datetime import datetime
from environs import Env
from sqlalchemy import create_engine, Table, Column, Integer, String, DateTime, MetaData


env = Env()
env.read_env()

PG_URI = env('DATABASE')

engine = create_engine(f'postgresql://{PG_URI}')

meta = MetaData()

# => tables

# results table
RESULTS = Table(
    'results', meta,
    Column('id', Integer, primary_key=True),
    Column('key', String),
    Column('result', String),
    Column('created_at', DateTime)
)

meta.create_all(engine)


def results_insert(key:str, result:str, created_at:datetime):
    """Insert new data into the RESULTS table.
    """

    try:
        conn = engine.connect()
        result = conn.execute(
            RESULTS.insert(),
            {
                'key': key,
                'result': result,
                'created_at': created_at
            }
        )

        return result.rowcount
    except:
        # raise

        return 0
