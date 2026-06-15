import os
from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi

class KaggleDownloader:
    
    def __init__(self, download_dir: str = "data"):
        self.download_dir = Path(download_dir)
        # Ensure the download directory exists
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.api = KaggleApi()
        self._authenticated = False
        
    def authenticate(self) -> None:
        """Authenticates with the Kaggle API using available credentials."""
        if not self._authenticated:
            print("Authenticating with Kaggle API...")
            self.api.authenticate()
            self._authenticated = True
            print("Kaggle authentication successful.")

    def download_dataset(self, dataset_name: str, unzip: bool = True) -> None:
        """
        Downloads a specific dataset from Kaggle.
        
        Args:
            dataset_name (str): The dataset name on Kaggle (format: 'owner/dataset-name').
            unzip (bool): Whether to unzip the downloaded files automatically.
        """
        dataset_slug = dataset_name.split('/')[-1]
        dataset_path = self.download_dir / dataset_slug

        if dataset_path.exists() and any(dataset_path.iterdir()):
            print(f"Dataset '{dataset_name}' already exists at '{dataset_path}'. Skipping download.")
            return

        self.authenticate()
        
        try:
            print(f"Starting download for dataset '{dataset_name}'...")
            dataset_path.mkdir(parents=True, exist_ok=True)
            print(f"Target directory: {dataset_path.absolute()}")
            
            self.api.dataset_download_files(
                dataset=dataset_name,
                path=str(dataset_path),
                unzip=unzip
            )
            
            print(f"Successfully downloaded dataset: {dataset_name}")
            
        except Exception as e:
            print(f"Error downloading dataset '{dataset_name}': {e}")
            raise
