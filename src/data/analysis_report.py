"""
Generate reports from collected skin analysis data.
"""
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from typing import List, Dict
import os

class AnalysisReport:
    def __init__(self, dataset_path: str):
        self.dataset_path = dataset_path

    def generate_daily_report(self, output_dir: str = "reports") -> str:
        """Generate a daily report with graphs and statistics."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Read and process data
        df = pd.read_csv(self.dataset_path)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Generate plots
        plt.figure(figsize=(12, 6))
        
        # Dryness score over time
        plt.subplot(1, 2, 1)
        plt.plot(df['timestamp'], df['dryness_score'])
        plt.title('Dryness Score Over Time')
        plt.xticks(rotation=45)
        
        # Status distribution
        plt.subplot(1, 2, 2)
        df['status'].value_counts().plot(kind='pie', autopct='%1.1f%%')
        plt.title('Status Distribution')
        
        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(output_dir, f"skin_analysis_report_{timestamp}.png")
        plt.savefig(report_path)
        plt.close()
        
        return report_path

    def get_statistics(self) -> Dict:
        """Calculate statistics from the dataset."""
        df = pd.read_csv(self.dataset_path)
        
        return {
            'total_measurements': len(df),
            'average_dryness': df['dryness_score'].mean(),
            'max_dryness': df['dryness_score'].max(),
            'min_dryness': df['dryness_score'].min(),
            'status_distribution': df['status'].value_counts().to_dict()
        }