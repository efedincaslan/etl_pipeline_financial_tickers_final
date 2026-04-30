import sys
from sqlalchemy import text
from extract import extraction
from transform import transformation
from load import loading
import logging
from database import engine
from tickers import symbols

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    handlers = [
                        logging.FileHandler('app.log'),
                        logging.StreamHandler(sys.stdout)
                    ]
)

def main():
    try:
        extraction()
        logging.info("Extraction completed successfully")
        transformation()
        logging.info("Transformation completed successfully")
        loading()
        logging.info("Loading completed successfully")

        # database query to check if data is loaded correctly
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT symbol, COUNT(*) FROM market_statistics GROUP BY symbol"))
                rows = result.fetchall()
                for row in rows:
                    if row[1] > 0 and row[0] in symbols:
                        logging.info(f"Data for symbol: {row[0]} loaded successfully with {row[1]} records")
                    else:
                        logging.warning(f"No data found for symbol: {row[0]}")
                for i in symbols:
                    if i not in [row[0] for row in rows]:
                        logging.warning(f"No data found for symbol: {i}")


        except Exception as e:
            logging.error(f"An error occurred while querying data from the database: {e}")
        



        logging.info("ETL process completed successfully")
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
     