
import json
import time
import requests
import os
import logging
import tickers
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    handlers = [
                        logging.FileHandler('app.log'),
                        logging.StreamHandler(sys.stdout)
                    ]
)
logger = logging.getLogger(__name__)


def extraction():
    try:
        logger.info("Application started")
        apikey = os.getenv("apikey")
        data = {}
        # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
        
        for symbol in tickers.symbols:
            try:
                url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={apikey}'
                r = requests.get(url)
                json_response = r.json()
                time.sleep(12)  # Alpha Vantage allows 5 API calls per minute, so we wait 12 seconds between calls
                if "Time Series (Daily)" not in json_response:
                    logger.warning(f"API response for symbol {symbol} does not contain expected data. Response: {json_response}")
                    continue
                data[symbol] = json_response

                logger.info(f"Data extracted for symbol: {symbol}")
                
            except Exception as e:
                logger.error(f"An error occurred while extracting data for symbol {symbol}: {e}")
        
        with open('bronze.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4) # indent=4 makes it readable
        logger.info("Data extraction completed successfully")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise 
