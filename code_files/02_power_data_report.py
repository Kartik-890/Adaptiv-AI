import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
from pathlib import Path

class DataAnalyzer:
    def __init__(self, csv_file_path):
        self.csv_file = csv_file_path
        self.df = None
        self.output_dir = Path("outputs")
        self.output_dir.mkdir(exist_ok=True)
        
        # Create timestamp for this analysis session
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def load_data(self):
        print("Loading data from CSV")
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"Data loaded successfully: {len(self.df)} rows, {len(self.df.columns)} columns")
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def generate_basic_report(self):
        report_file = self.output_dir / f"01_basic_report_{self.timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ELECTRIC POWER DATA - BASIC ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Dataset Overview
            f.write("DATASET OVERVIEW\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total Records: {len(self.df):,}\n")
            f.write(f"Total Columns: {len(self.df.columns)}\n")
            f.write(f"Memory Usage: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n\n")
            
            # Column Information
            f.write("COLUMN INFORMATION\n")
            f.write("-" * 30 + "\n")
            for i, col in enumerate(self.df.columns, 1):
                dtype = str(self.df[col].dtype)
                non_null = self.df[col].count()
                null_count = self.df[col].isnull().sum()
                null_pct = (null_count / len(self.df)) * 100
                
                f.write(f"{i:2d}. {col:<30} | Type: {dtype:<10} | "
                       f"Non-null: {non_null:>8,} | Missing: {null_count:>6,} ({null_pct:5.1f}%)\n")
            
            # Data by Year
            if 'year' in self.df.columns:
                f.write(f"\nDATA BY YEAR\n")
                f.write("-" * 30 + "\n")
                year_counts = self.df['year'].value_counts().sort_index()
                for year, count in year_counts.items():
                    f.write(f"{year}: {count:,} records\n")
            
            # Data by Building Type
            if 'building_type' in self.df.columns:
                f.write(f"\nDATA BY BUILDING TYPE\n")
                f.write("-" * 30 + "\n")
                building_counts = self.df['building_type'].value_counts()
                for building, count in building_counts.items():
                    f.write(f"{building}: {count:,} records\n")
            
            # Sample Data
            f.write(f"\nSAMPLE DATA (First 10 rows)\n")
            f.write("-" * 50 + "\n")
            f.write(self.df.head(10).to_string(index=False))
            f.write("\n\n")
            
        print(f"Basic report saved to: {report_file}")
        return report_file
    
    def generate_statistical_report(self):
        report_file = self.output_dir / f"02_statistical_report_{self.timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ELECTRIC POWER DATA - STATISTICAL ANALYSIS REPORT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Numeric columns analysis
            numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
            
            if numeric_cols:
                f.write("NUMERIC COLUMNS STATISTICAL SUMMARY\n")
                f.write("-" * 40 + "\n")
                
                for col in numeric_cols:
                    if col not in ['year']:  # Skip metadata columns
                        f.write(f"\nColumn: {col}\n")
                        f.write("~" * 20 + "\n")
                        
                        series = self.df[col].dropna()
                        if len(series) > 0:
                            f.write(f"Count: {len(series):,}\n")
                            f.write(f"Mean: {series.mean():.4f}\n")
                            f.write(f"Median: {series.median():.4f}\n")
                            f.write(f"Std Dev: {series.std():.4f}\n")
                            f.write(f"Min: {series.min():.4f}\n")
                            f.write(f"Max: {series.max():.4f}\n")
                            f.write(f"25th Percentile: {series.quantile(0.25):.4f}\n")
                            f.write(f"75th Percentile: {series.quantile(0.75):.4f}\n")
                            
                            # Outlier detection (IQR method)
                            Q1 = series.quantile(0.25)
                            Q3 = series.quantile(0.75)
                            IQR = Q3 - Q1
                            lower_bound = Q1 - 1.5 * IQR
                            upper_bound = Q3 + 1.5 * IQR
                            outliers = series[(series < lower_bound) | (series > upper_bound)]
                            f.write(f"Outliers (IQR method): {len(outliers):,} ({len(outliers)/len(series)*100:.2f}%)\n")
                        else:
                            f.write("No valid numeric data found\n")
            
            # Categorical columns analysis
            categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
            
            if categorical_cols:
                f.write(f"\n\nCATEGORICAL COLUMNS ANALYSIS\n")
                f.write("-" * 40 + "\n")
                
                for col in categorical_cols:
                    f.write(f"\nColumn: {col}\n")
                    f.write("~" * 20 + "\n")
                    
                    value_counts = self.df[col].value_counts()
                    f.write(f"Unique values: {len(value_counts)}\n")
                    f.write(f"Most common values:\n")
                    
                    for value, count in value_counts.head(10).items():
                        pct = (count / len(self.df)) * 100
                        f.write(f"  {str(value)[:30]:<30}: {count:>8,} ({pct:5.1f}%)\n")
                    
                    if len(value_counts) > 10:
                        f.write(f"  and {len(value_counts) - 10} more unique values\n")
        
        print(f" Statistical report saved to: {report_file}")
        return report_file
    
    def generate_data_quality_report(self):
        report_file = self.output_dir / f"03_data_quality_report_{self.timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ELECTRIC POWER DATA - DATA QUALITY ASSESSMENT\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Missing Data Analysis
            f.write("MISSING DATA ANALYSIS\n")
            f.write("-" * 30 + "\n")
            
            missing_data = self.df.isnull().sum()
            missing_pct = (missing_data / len(self.df)) * 100
            
            f.write(f"{'Column':<30} | {'Missing Count':<15} | {'Missing %':<10}\n")
            f.write("-" * 60 + "\n")
            
            for col in self.df.columns:
                f.write(f"{col:<30} | {missing_data[col]:>13,} | {missing_pct[col]:>8.2f}%\n")
            
            # Data Completeness Score
            overall_completeness = (1 - missing_data.sum() / (len(self.df) * len(self.df.columns))) * 100
            f.write(f"\nOverall Data Completeness: {overall_completeness:.2f}%\n")
            
            # Duplicate Records
            f.write(f"\nDUPLICATE RECORDS ANALYSIS\n")
            f.write("-" * 30 + "\n")
            
            total_duplicates = self.df.duplicated().sum()
            f.write(f"Total duplicate rows: {total_duplicates:,}\n")
            f.write(f"Percentage of duplicates: {(total_duplicates/len(self.df)*100):.2f}%\n")
            
            # Check for duplicates by key columns
            if 'file_name' in self.df.columns:
                file_duplicates = self.df.duplicated(subset=['file_name']).sum()
                f.write(f"Duplicate file names: {file_duplicates:,}\n")
            
            f.write(f"\nDATA TYPE ANALYSIS\n")
            f.write("-" * 30 + "\n")
            
            dtype_counts = self.df.dtypes.value_counts()
            for dtype, count in dtype_counts.items():
                f.write(f"{str(dtype):<15}: {count} columns\n")
            
            # File Coverage Analysis
            if 'year' in self.df.columns and 'building_type' in self.df.columns:
                f.write(f"\nFILE COVERAGE ANALYSIS\n")
                f.write("-" * 30 + "\n")
                
                coverage = self.df.groupby(['year', 'building_type']).size().unstack(fill_value=0)
                f.write("Records by Year and Building Type:\n")
                f.write(coverage.to_string())
                f.write("\n")
        
        print(f"Data quality report saved to: {report_file}")
        return report_file
    
    def generate_time_series_report(self):
        report_file = self.output_dir / f"04_time_series_report_{self.timestamp}.txt"
        
        # Look for datetime-like columns
        datetime_cols = []
        for col in self.df.columns:
            if any(keyword in col.lower() for keyword in ['time', 'date', 'timestamp']):
                datetime_cols.append(col)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ELECTRIC POWER DATA - TIME SERIES ANALYSIS\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            if datetime_cols:
                f.write("DATETIME COLUMNS FOUND\n")
                f.write("-" * 30 + "\n")
                
                for col in datetime_cols:
                    f.write(f"\nAnalyzing column: {col}\n")
                    f.write("~" * 25 + "\n")
                    
                    try:
                        # Try to convert to datetime
                        dt_series = pd.to_datetime(self.df[col], errors='coerce')
                        valid_dates = dt_series.dropna()
                        
                        if len(valid_dates) > 0:
                            f.write(f"Valid datetime entries: {len(valid_dates):,}\n")
                            f.write(f"Invalid datetime entries: {len(dt_series) - len(valid_dates):,}\n")
                            f.write(f"Date range: {valid_dates.min()} to {valid_dates.max()}\n")
                            
                            # Time span
                            time_span = valid_dates.max() - valid_dates.min()
                            f.write(f"Time span: {time_span.days} days\n")
                            
                            # Frequency analysis
                            if len(valid_dates) > 1:
                                time_diffs = valid_dates.diff().dropna()
                                most_common_diff = time_diffs.mode()
                                if len(most_common_diff) > 0:
                                    f.write(f"Most common time interval: {most_common_diff.iloc[0]}\n")
                        else:
                            f.write("No valid datetime entries found\n")
                            
                    except Exception as e:
                        f.write(f"Error analyzing datetime column: {e}\n")
            else:
                f.write("NO DATETIME COLUMNS DETECTED\n")
                f.write("-" * 30 + "\n")
                f.write("Searched for columns containing: 'time', 'date', 'timestamp'\n")
                f.write("Available columns:\n")
                for i, col in enumerate(self.df.columns, 1):
                    f.write(f"  {i}. {col}\n")
        
        print(f"Time series report saved to: {report_file}")
        return report_file
    
    def generate_summary_dashboard(self):
        report_file = self.output_dir / f"00_SUMMARY_DASHBOARD_{self.timestamp}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ELECTRIC POWER DATA ANALYSIS - EXECUTIVE SUMMARY\n")
            f.write("=" * 60 + "\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Key Metrics
            f.write("KEY METRICS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Total Records: {len(self.df):,}\n")
            f.write(f"Total Columns: {len(self.df.columns)}\n")
            f.write(f"Dataset Size: {self.df.memory_usage(deep=True).sum() / 1024**2:.2f} MB\n")
            
            if 'year' in self.df.columns:
                years = sorted(self.df['year'].unique())
                f.write(f"Years Covered: {min(years)} - {max(years)} ({len(years)} years)\n")
            
            if 'building_type' in self.df.columns:
                building_types = self.df['building_type'].nunique()
                f.write(f"Building Types: {building_types}\n")
            
            if 'file_name' in self.df.columns:
                files = self.df['file_name'].nunique()
                f.write(f"Source Files: {files}\n")
            
            # Data Quality Score
            missing_pct = (self.df.isnull().sum().sum() / (len(self.df) * len(self.df.columns))) * 100
            quality_score = 100 - missing_pct
            f.write(f" Data Quality Score: {quality_score:.1f}%\n")
            
            # Top Issues
            f.write(f"\nTOP DATA ISSUES\n")
            f.write("-" * 20 + "\n")
            
            missing_by_col = self.df.isnull().sum().sort_values(ascending=False)
            top_missing = missing_by_col[missing_by_col > 0].head(5)
            
            if len(top_missing) > 0:
                f.write("Columns with most missing data:\n")
                for col, missing in top_missing.items():
                    pct = (missing / len(self.df)) * 100
                    f.write(f"  • {col}: {missing:,} missing ({pct:.1f}%)\n")
            else:
                f.write("No missing data found!\n")
            
            # Recommendations
            f.write(f"\nRECOMMendations\n")
            f.write("-" * 20 + "\n")
            
            if quality_score < 90:
                f.write("Investigate missing data patterns\n")
            if missing_pct > 50:
                f.write("High missing data - consider data cleaning\n")
            
            numeric_cols = len(self.df.select_dtypes(include=[np.number]).columns)
            if numeric_cols > 0:
                f.write("Ready for statistical analysis\n")
            
            if 'year' in self.df.columns and len(self.df['year'].unique()) > 1:
                f.write("Suitable for trend analysis\n")
            
            f.write("\n" + "="*60 + "\n")
            f.write("DETAILED REPORTS GENERATED:\n")
            f.write("01_basic_report_[timestamp].txt - Dataset overview\n")
            f.write("02_statistical_report_[timestamp].txt - Statistical analysis\n")
            f.write("03_data_quality_report_[timestamp].txt - Data quality assessment\n")
            f.write("04_time_series_report_[timestamp].txt - Time series analysis\n")
        
        print(f"Summary dashboard saved to: {report_file}")
        return report_file
    
    def run_complete_analysis(self):
        print("ELECTRIC POWER DATA ANALYSIS")
        print("="*40)
        
        if not self.load_data():
            return False
        
        print(f"\nGenerating analysis reports")
        print(f"Output directory: {self.output_dir.absolute()}")
        
        # Generate all reports
        reports = []
        reports.append(self.generate_summary_dashboard())
        reports.append(self.generate_basic_report())
        reports.append(self.generate_statistical_report())
        reports.append(self.generate_data_quality_report())
        reports.append(self.generate_time_series_report())
        
        print(f"\n Analysis complete! Generated {len(reports)} reports:")
        for report in reports:
            print(f" {report.name}")
        
        return True

# Main execution
if __name__ == "__main__":
    # Initialize analyzer with your CSV file
    analyzer = DataAnalyzer("combined_electric_power_data.csv")
    
    # Run complete analysis
    analyzer.run_complete_analysis()
    
    print(f"\n All analysis reports have been generated!")
    print(f"Check the 'outputs' folder for all text files.")