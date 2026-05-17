import requests
import pandas as pd
from pathlib import Path

class HolidayExtractor:
    """
    Extracts Brazilian national holidays using the Brasil API.
    """
    
    def __init__(self, years: list[int] = None, output_dir: str = "../data"):
        """
        Initializes the Holiday Extractor.
        
        Args:
            years (list[int]): List of years to fetch holidays for. Defaults to [2016, 2017, 2018].
                               The Olist dataset covers approx Sep 2016 to Oct 2018.
            output_dir (str): Directory to save the extracted dataset.
        """
        self.years = years if years else [2016, 2017, 2018]
        
        # Resolve path relative to this script
        base_path = Path(__file__).parent
        self.output_dir = (base_path / output_dir).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.base_url = "https://brasilapi.com.br/api/feriados/v1/"
        
    def fetch_holidays(self) -> pd.DataFrame:
        """
        Fetches holidays for the specified years and returns a combined DataFrame.
        """
        all_holidays = []
        
        for year in self.years:
            print(f"Fetching holidays for year {year}...")
            response = requests.get(f"{self.base_url}{year}")
            
            if response.status_code == 200:
                holidays_data = response.json()
                all_holidays.extend(holidays_data)
            else:
                print(f"Failed to fetch holidays for {year}. Status code: {response.status_code}")
                
        if not all_holidays:
            raise ValueError("No holidays data could be fetched.")
            
        df = pd.DataFrame(all_holidays)
        
        # Data Transformation for consistency
        df['date'] = pd.to_datetime(df['date'])
        
        return df
        
    def save_data(self, df: pd.DataFrame, filename: str = "brazil_holidays.csv") -> None:
        """
        Saves the DataFrame to a CSV file.
        """
        file_path = self.output_dir / filename
        df.to_csv(file_path, index=False)
        print(f"Holidays data saved to: {file_path}")

if __name__ == "__main__":
    extractor = HolidayExtractor()
    df_holidays = extractor.fetch_holidays()
    extractor.save_data(df_holidays)
