"""
Manages the collection and storage of skin analysis data.
"""
import os
import csv
import datetime
from typing import Dict, List

class DatasetManager:
    def __init__(self, data_dir: str = "dataset"):
        self.data_dir = data_dir
        self.csv_path = os.path.join(data_dir, "skin_analysis_data.csv")
        self._initialize_storage()

    def _initialize_storage(self):
        """Initialize the storage directory and CSV file if they don't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['timestamp', 'dryness_score', 'texture_score', 'status'])

    def save_analysis(self, results: Dict[str, float]) -> None:
        """Save analysis results to the dataset."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = self._determine_status(results['dryness_score'])
        
        with open(self.csv_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp,
                f"{results['dryness_score']:.2f}",
                f"{results['texture_score']:.2f}",
                status
            ])

    def _determine_status(self, dryness_score: float) -> str:
        """Determine skin status based on dryness score."""
        if dryness_score > 0.7:
            return "Very Dry"
        elif dryness_score > 0.4:
            return "Moderately Dry"
        return "Normal"

    def get_recent_analyses(self, limit: int = 10) -> List[Dict]:
        """Retrieve recent analysis results."""
        results = []
        try:
            with open(self.csv_path, 'r') as file:
                reader = csv.DictReader(file)
                results = list(reader)[-limit:]
        except FileNotFoundError:
            pass
        return results