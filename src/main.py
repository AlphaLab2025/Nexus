import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))

from pipeline.kaggle_download import KaggleDownloader
from pipeline.extract_external import HolidayExtractor
from pipeline.extract_ibge_locations import IBGELocationExtractor

class DataPipeline:
    
    def __init__(self, raw_data_dir: str = "../data"):
        """
        Initializes the data pipeline.
        
        Args:
            raw_data_dir (str): Relative path from this script to the data directory.
        """
        # Resolve the absolute path based on the location of main.py
        base_path = Path(__file__).parent
        self.download_dir = (base_path / raw_data_dir).resolve()
        
        # Instantiate the components
        self.downloader = KaggleDownloader(download_dir=str(self.download_dir))
        self.holiday_extractor = HolidayExtractor(output_dir=str(self.download_dir))
        self.ibge_location_extractor = IBGELocationExtractor(output_dir=str(self.download_dir))
        
    def run(self, dataset_name: str) -> None:
        """
        Executes the main pipeline steps.
        
        Args:
            dataset_name (str): The kaggle dataset identifier.
        """
        print(f"=== Starting Data Pipeline ===")
        print(f"Target Kaggle Dataset: {dataset_name}")
        
        # Step 1: Download from Kaggle (CSV Source)
        try:
            print("\n--- Step 1a: Extracting from Kaggle (CSVs) ---")
            self.downloader.download_dataset(dataset_name=dataset_name, unzip=True)
            print("Kaggle download phase completed.")
        except Exception as e:
            print(f"Pipeline failed during Kaggle download phase: {e}")
            return
            
        # Step 2: Download from External API (JSON Source)
        try:
            print("\n--- Step 1b: Extracting from External API (Holidays) ---")
            df_holidays = self.holiday_extractor.fetch_holidays()
            self.holiday_extractor.save_data(df_holidays)
            print("External API extraction completed.")
        except Exception as e:
            print(f"Pipeline failed during external API extraction phase: {e}")
            return

        try:
            print("\n--- Step 1c: Extracting from IBGE API (States and Regions) ---")
            states = self.ibge_location_extractor.fetch_states()
            self.ibge_location_extractor.save_data(states)
            print("IBGE API extraction completed.")
        except Exception as e:
            print(f"Pipeline failed during IBGE API extraction phase: {e}")
            return
            
        print("\n=== Pipeline Execution Finished ===")


if __name__ == "__main__":
    # For example: 'zillow/zecon' or 'mkechinov/ecommerce-events-history-in-cosmetics-shop'
    TARGET_DATASET = "olistbr/brazilian-ecommerce" 
    
    pipeline = DataPipeline()
    pipeline.run(dataset_name=TARGET_DATASET)
