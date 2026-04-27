import csv
import logging
import sys
import pandas as pd
import json
from extract import extraction

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                    handlers = [
                        logging.FileHandler('app.log'),
                        logging.StreamHandler(sys.stdout)
                    ]
)
logger = logging.getLogger(__name__)


def transformation():
    try:
        with open('bronze.json', 'r', encoding='utf-8') as f:
            data = json.load(f)

            symbol = list(data.keys())  # Get all symbols from the data
            with open('silver.csv', 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=['symbol', 'market_date', 'open', 'high', 'low', 'close', 'volume'])
                writer.writeheader()
                
                for sym in symbol:
                    try:
                        df = pd.DataFrame(data[sym]['Time Series (Daily)']).T
                        df['symbol'] = sym  # Add a column for the symbol
                        df = df.reset_index().rename(columns={'index': 'market_date'})  # Reset index and rename it to 'date'
                        df = df.rename(columns={
                        '1. open': 'open',
                        '2. high': 'high',
                        '3. low': 'low',
                        '4. close': 'close',
                        '5. volume': 'volume'
                    })  # Rename columns to more readable names
                        df = df[['symbol', 'market_date', 'open', 'high', 'low', 'close', 'volume']]  # Reorder columns
                        df['market_date'] = pd.to_datetime(df['market_date'])  # Convert date column to datetime
                        df['market_date'] = df['market_date'].dt.strftime('%Y-%m-%d')  # Format date as YYYY-MM-DD
                        df = df.sort_values(by='market_date')  # Sort by date
                        df['open'] = df['open'].astype(float)  # Convert open to float
                        df['high'] = df['high'].astype(float)  # Convert high to float
                        df['low'] = df['low'].astype(float)  # Convert low to float
                        df['close'] = df['close'].astype(float)  # Convert close to float
                        df['volume'] = df['volume'].astype(int)  # Convert volume to int
                        writer.writerows(df.to_dict('records'))  # Write rows to CSV
                        logger.info(f"Data transformed and written to CSV for symbol: {sym}")
                    except Exception as e:
                        logger.error(f"An error occurred while transforming data for symbol {sym}: {e}")
                        
                    
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        raise


