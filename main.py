import sys

from extract import extraction
from transform import transformation
from load import loading
import logging

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

        logging.info("ETL process completed successfully")
        
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    