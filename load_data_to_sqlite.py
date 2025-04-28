import pandas as pd
import sqlite3
from pathlib import Path

# ------------------ Overview ------------------ #
# This script loads data from a CSV file into a SQLite database.
# It provides functionality to validate column names, filter duplicates, and load new data.

class YakkerTechDataLoader:
    def __init__(self, db_path: str = "sqllite_db.db"):
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    def connect_db(self):
        """Establish database connection"""
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()

    def close_db(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()

    def get_table_columns(self) -> list:
        """Get column names from yakkertech table"""
        self.cursor.execute("PRAGMA table_info(yakkertech)")
        return [row[1] for row in self.cursor.fetchall()]

    def validate_columns(self, csv_data: pd.DataFrame) -> bool:
        """Check if CSV columns match table schema"""
        table_columns = self.get_table_columns()
        csv_columns = list(csv_data.columns)
        
        if table_columns != csv_columns:
            print("❌ Column mismatch detected!")
            print(f"📁 CSV columns:    {csv_columns}")
            print(f"🗃️  Table columns: {table_columns}")
            print("ℹ️  Aborting upload to maintain schema consistency.")
            return False
        return True

    def filter_duplicates(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """Remove rows that already exist in database"""
        existing_data = pd.read_sql("SELECT * FROM yakkertech", self.connection)
        
        # Create composite key for comparison
        for df in [new_data, existing_data]:
            df['combined_key'] = (df['PitchNo'].astype(str) + '_' + 
                                df['Date'].astype(str) + '_' + 
                                df['Time'].astype(str))
        
        # Find and clean new rows
        new_rows = new_data[~new_data['combined_key'].isin(existing_data['combined_key'])]
        new_rows = new_rows.drop(columns=['combined_key'])
        
        duplicate_count = len(new_data) - len(new_rows)
        if duplicate_count > 0:
            print(f"⚠️  Found {duplicate_count} duplicate rows - skipping these")
            
        return new_rows

    def load_data(self, csv_path: str):
        """Main method to load CSV data into database"""
        try:
            # Load CSV
            data = pd.read_csv(csv_path)
            
            # Connect to DB
            self.connect_db()
            
            # Validate schema
            if not self.validate_columns(data):
                return
                
            # Filter duplicates
            new_rows = self.filter_duplicates(data)
            
            # Upload new data
            if len(new_rows) > 0:
                new_rows.to_sql(name="yakkertech", con=self.connection, 
                              if_exists="append", index=False)
                print(f"✅ Successfully added {len(new_rows)} new rows to table 'yakkertech'.")
            else:
                print("ℹ️  No new rows to add - all rows already exist in database.")
                
        finally:
            self.close_db()

def main():
    csv_path = "yakker_data/Syracuse@Georgia Tech Game 3.csv"
    loader = YakkerTechDataLoader()
    loader.load_data(csv_path)

if __name__ == "__main__":
    main()
