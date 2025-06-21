import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
from collections import Counter


class WeatherAnalyzer:
    
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.df = pd.read_csv(csv_file)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def analyze_all(self):
        output_file = f"weather_complete_analysis_{self.timestamp}.txt"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("WEATHER DATA - COMPLETE ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Source: {self.csv_file}\n")
            f.write("=" * 60 + "\n\n")
            
            # BASIC OVERVIEW
            f.write("BASIC OVERVIEW\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Files: {len(self.df):,}\n")
            f.write(f"Columns: {len(self.df.columns)}\n")
            f.write(f"Dataset Size: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n")
            
            if 'File_Size_MB' in self.df.columns:
                total_gb = self.df['File_Size_MB'].sum() / 1024
                f.write(f"Total Storage: {total_gb:.2f} GB\n")
                f.write(f"Avg File Size: {self.df['File_Size_MB'].mean():.2f} MB\n")
                f.write(f"Largest File: {self.df['File_Size_MB'].max():.2f} MB\n")
            
            # DATA QUALITY
            missing_pct = (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
            f.write(f"Data Quality: {100-missing_pct:.1f}%\n")
            
            # YEAR BREAKDOWN
            if 'Year' in self.df.columns:
                f.write(f"\n FILES BY YEAR\n")
                f.write("-" * 30 + "\n")
                year_counts = self.df['Year'].value_counts().sort_index()
                for year, count in year_counts.items():
                    pct = (count / len(self.df)) * 100
                    f.write(f"{year}: {count:,} files ({pct:.1f}%)\n")
            
            # FILE TYPES
            if 'File_Extension' in self.df.columns:
                f.write(f"\n FILE TYPES\n")
                f.write("-" * 30 + "\n")
                ext_counts = self.df['File_Extension'].value_counts()
                for ext, count in ext_counts.items():
                    pct = (count / len(self.df)) * 100
                    f.write(f"{ext}: {count:,} files ({pct:.1f}%)\n")
            
            # FOLDERS
            if 'Folder_Name' in self.df.columns:
                f.write(f"\n TOP FOLDERS\n")
                f.write("-" * 30 + "\n")
                folder_counts = self.df['Folder_Name'].value_counts().head(10)
                for folder, count in folder_counts.items():
                    f.write(f"{folder}: {count:,} files\n")
            
            # WEATHER DATA DETECTION
            if 'File_Name' in self.df.columns:
                f.write(f"\n WEATHER DATA TYPES DETECTED\n")
                f.write("-" * 30 + "\n")
                
                weather_types = {
                    'Temperature': ['temp', 'temperature'],
                    'Humidity': ['humid', 'moisture'],
                    'Wind': ['wind', 'speed'],
                    'Rain': ['rain', 'precip'],
                    'Pressure': ['pressure', 'barometric'],
                    'Solar': ['solar', 'radiation'],
                    'Weather': ['weather', 'climate']
                }
                
                for weather_type, keywords in weather_types.items():
                    count = 0
                    for keyword in keywords:
                        count += self.df['File_Name'].str.contains(keyword, case=False, na=False).sum()
                    if count > 0:
                        pct = (count / len(self.df)) * 100
                        f.write(f"{weather_type}: {count:,} files ({pct:.1f}%)\n")
            
            # STATISTICS FOR NUMERIC COLUMNS
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                f.write(f"\nNUMERIC STATISTICS\n")
                f.write("-" * 30 + "\n")
                for col in numeric_cols:
                    if col != 'Year':
                        series = self.df[col].dropna()
                        if len(series) > 0:
                            f.write(f"\n{col}:\n")
                            f.write(f"  Mean: {series.mean():.2f}\n")
                            f.write(f"  Median: {series.median():.2f}\n")
                            f.write(f"  Min: {series.min():.2f}\n")
                            f.write(f"  Max: {series.max():.2f}\n")
                            f.write(f"  Std: {series.std():.2f}\n")
            
            # DATA ISSUES
            f.write(f"\n DATA ISSUES\n")
            f.write("-" * 30 + "\n")
            
            # Missing data
            missing_data = self.df.isnull().sum()
            missing_cols = missing_data[missing_data > 0]
            if len(missing_cols) > 0:
                f.write("Missing data:\n")
                for col, missing in missing_cols.items():
                    pct = (missing / len(self.df)) * 100
                    f.write(f"  {col}: {missing:,} ({pct:.1f}%)\n")
            else:
                f.write("No missing data\n")
            
            # Duplicates
            duplicates = self.df.duplicated().sum()
            f.write(f"Duplicate rows: {duplicates:,}\n")
            
            # Zero-size files
            if 'File_Size_MB' in self.df.columns:
                zero_files = (self.df['File_Size_MB'] == 0).sum()
                f.write(f"Zero-size files: {zero_files:,}\n")
            
            # YEAR-EXTENSION MATRIX
            if 'Year' in self.df.columns and 'File_Extension' in self.df.columns:
                f.write(f"\n FILES BY YEAR & TYPE\n")
                f.write("-" * 30 + "\n")
                matrix = pd.crosstab(self.df['Year'], self.df['File_Extension'], margins=True)
                f.write(matrix.to_string())
                f.write("\n")
            
            # RECOMMENDATIONS
            f.write(f"\n RECOMMENDATIONS\n")
            f.write("-" * 30 + "\n")
            
            if 100-missing_pct >= 95:
                f.write("Excellent data quality\n")
            elif 100-missing_pct >= 85:
                f.write(" Good data quality\n")
            else:
                f.write(" Check data quality issues\n")
            
            if 'Year' in self.df.columns:
                years = [y for y in self.df['Year'].unique() if y != 'Unknown']
                if len(years) > 1:
                    f.write(" Multi-year data available\n")
            
            if 'File_Size_MB' in self.df.columns:
                if total_gb > 10:
                    f.write("Large dataset - consider processing strategy\n")
                elif total_gb > 1:
                    f.write(" Medium dataset - manageable size\n")
                else:
                    f.write(" Small dataset - easy to process\n")
            
            # SAMPLE DATA
            f.write(f"\n SAMPLE DATA (First 5 rows)\n")
            f.write("-" * 50 + "\n")
            f.write(self.df.head(5).to_string(index=False))
            
            f.write(f"\n\n" + "="*60 + "\n")
            f.write("ANALYSIS COMPLETE\n")
            f.write("="*60 + "\n")
        
        print(f" Complete weather analysis saved to: {output_file}")
        return output_file

# Usage
if __name__ == "__main__":
    # Replace with your actual CSV filename
    analyzer = WeatherAnalyzer("weather_files_list.csv")
    analyzer.analyze_all()
    
    print("Weather data analysis completed!")
