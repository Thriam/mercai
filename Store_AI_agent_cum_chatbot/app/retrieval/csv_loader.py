import pandas as pd
from pathlib import Path
from app.config.settings import settings
from app.config.logging_config import logger

class CSVLoader:
    """Load and parse CSV product data."""

    REQUIRED_COLUMNS = {'id', 'price', 'quantity', 'rating'}

    @staticmethod
    def load(csv_path: Path = None) -> list:
        """
        Load products from CSV.

        Args:
            csv_path: Path to CSV file (defaults to settings.CSV_FILE_PATH)

        Returns:
            List of product dictionaries
        """
        if csv_path is None:
            csv_path = settings.CSV_FILE_PATH

        if not csv_path.exists():
            logger.warning(f"CSV file not found: {csv_path}")
            return []

        df = pd.read_csv(csv_path)

        # Validate required columns
        missing = CSVLoader.REQUIRED_COLUMNS - set(df.columns)
        if missing:
            raise ValueError(f"Missing required columns: {missing}")

        products = []
        for _, row in df.iterrows():
            product = {
                'id': str(row['id']),
                'price': float(row['price']),
                'quantity': int(row['quantity']),
                'rating': float(row['rating']),
            }
            # Add optional columns
            for col in df.columns:
                if col not in CSVLoader.REQUIRED_COLUMNS:
                    product[col] = row[col]

            products.append(product)

        logger.info(f"Loaded {len(products)} products from CSV")
        return products
