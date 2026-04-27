
from sqlalchemy import MetaData, Table, create_engine, insert
import pandas as pd
import logging
import os
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert

load_dotenv()
db_user = os.getenv('connection_string')

logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def loading():
    try:
        engine = create_engine(db_user)
        metadata = MetaData()
        my_table = Table('market_statistics', metadata, autoload_with=engine)
        try:
            with engine.begin() as conn:
                logging.info("Database connection established successfully")
                with open('silver.csv', 'r') as f:
                    df = pd.read_csv(f)
                    stmt = insert(my_table).values(df.to_dict(orient='records'))

                    upsert_stmt = stmt.on_conflict_do_update(
                        index_elements=['symbol', 'market_date'],  # Assuming symbol and date together are unique
                        set_={
                                'open': stmt.excluded.open,
                                'high': stmt.excluded.high,
                                'low': stmt.excluded.low,
                                'close': stmt.excluded.close,
                                'volume': stmt.excluded.volume
                        }
                    )
                conn.execute(upsert_stmt)
        except Exception as e:
            logger.error(f"An error occurred while loading data into the database: {e}")
            
        

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise

