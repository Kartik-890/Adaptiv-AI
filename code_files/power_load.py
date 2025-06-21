import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path


base_path = r"C:\Users\karti\Desktop\data_set\Electric power load data\Electric power load data"

# Define building types and years
building_types = ['Office', 'Commercial', 'Public', 'Residential']
years = ['2016', '2017', '2018', '2019', '2020', '2021']

def diagnose_directory_structure():
    print("DIRECTORY STRUCTURE DIAGNOSIS")
    print("="*50)
    
    print(f"Base path: {base_path}")
    print(f"Base path exists: {os.path.exists(base_path)}")
    
    if os.path.exists(base_path):
        print(f"Contents of base directory:")
        try:
            for item in os.listdir(base_path):
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path):
                    print(f"  {item}/")
                else:
                    print(f"  {item}")
        except Exception as e:
            print(f"Error listing base directory: {e}")
    
    # Check each expected year directory
    for year in years:
        year_path = os.path.join(base_path, year)
        print(f"\nYear {year}:")
        print(f"  Path: {year_path}")
        print(f"  Exists: {os.path.exists(year_path)}")
        
        if os.path.exists(year_path):
            print(f"  Contents:")
            try:
                for item in os.listdir(year_path):
                    item_path = os.path.join(year_path, item)
                    if os.path.isdir(item_path):
                        print(f"    {item}/")
                    else:
                        print(f"    {item}")
                        
                # Check 1_hour directory
                hour_path = os.path.join(year_path, '1_hour')
                if os.path.exists(hour_path):
                    print(f"    1_hour directory contents:")
                    for item in os.listdir(hour_path):
                        item_path = os.path.join(hour_path, item)
                        if os.path.isdir(item_path):
                            print(f"      {item}/")
                            # List files in building type directories
                            try:
                                files = os.listdir(item_path)
                                excel_files = [f for f in files if f.endswith(('.xlsx', '.xls', '.csv'))]
                                print(f"        Excel/CSV files: {len(excel_files)}")
                                if excel_files:
                                    for f in excel_files[:3]:  # Show first 3 files
                                        print(f"          {f}")
                                    if len(excel_files) > 3:
                                        print(f"          ... and {len(excel_files) - 3} more files")
                            except Exception as e:
                                print(f"        Error listing files: {e}")
                        else:
                            print(f"       {item}")
            except Exception as e:
                print(f"  Error listing year directory: {e}")

def find_all_excel_files():
    """Find all Excel files in the directory structure"""
    print("\n" + "="*50)
    print("SEARCHING FOR ALL EXCEL FILES")
    print("="*50)
    
    all_files = []
    
    # Walk through all directories
    for root, dirs, files in os.walk(base_path):
        excel_files = [f for f in files if f.endswith(('.xlsx', '.xls', '.csv'))]
        if excel_files:
            print(f"\nFound {len(excel_files)} files in: {root}")
            for file in excel_files:
                file_path = os.path.join(root, file)
                all_files.append(file_path)
                print(f"  {file}")
    
    print(f"\nTotal Excel/CSV files found: {len(all_files)}")
    return all_files

def load_sample_file(file_path):
    """Load and examine a sample file"""
    print(f"\nEXAMINING SAMPLE FILE: {file_path}")
    print("="*50)
    
    try:
        # Try different methods to read the file
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        print(f"File loaded successfully!")
        print(f"Shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"\nFirst few rows:")
        print(df.head())
        print(f"\nData types:")
        print(df.dtypes)
        
        return df
        
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def load_all_data_flexible():
    """Load all data with flexible approach"""
    print("\n" + "="*50)
    print("LOADING ALL DATA (FLEXIBLE APPROACH)")
    print("="*50)
    
    all_files = find_all_excel_files()
    
    if not all_files:
        print("No Excel/CSV files found!")
        return pd.DataFrame()
    
    all_dataframes = []
    
    for file_path in all_files:
        try:
            print(f"\nLoading: {file_path}")
            
            # Extract metadata from path
            path_parts = file_path.replace(base_path, '').split(os.sep)
            year = None
            building_type = None
            
            # Try to extract year and building type from path
            for part in path_parts:
                if part.isdigit() and len(part) == 4:
                    year = part
                elif any(bt in part for bt in building_types):
                    for bt in building_types:
                        if bt in part:
                            building_type = bt
                            break
            
            # Load the file
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Add metadata
            df['file_path'] = file_path
            df['file_name'] = os.path.basename(file_path)
            df['year'] = year if year else 'Unknown'
            df['building_type'] = building_type if building_type else 'Unknown'
            
            all_dataframes.append(df)
            print(f"  Loaded {len(df)} records")
            
        except Exception as e:
            print(f"   Error loading {file_path}: {e}")
    
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        print(f"\nTotal records loaded: {len(combined_df)}")
        return combined_df
    else:
        return pd.DataFrame()

def safe_summary_statistics(combined_df):
    """Generate summary statistics safely"""
    print("\n" + "="*50)
    print("SUMMARY STATISTICS")
    print("="*50)
    
    if combined_df.empty:
        print("No data loaded!")
        return
    
    print(f"Total records: {len(combined_df)}")
    
    if 'file_name' in combined_df.columns:
        print(f"Total files: {combined_df['file_name'].nunique()}")
    
    if 'year' in combined_df.columns:
        print(f"Years covered: {sorted(combined_df['year'].unique())}")
        print("\nRecords by year:")
        print(combined_df['year'].value_counts().sort_index())
    
    if 'building_type' in combined_df.columns:
        print(f"Building types: {sorted(combined_df['building_type'].unique())}")
        print("\nRecords by building type:")
        print(combined_df['building_type'].value_counts())
    
    print(f"\nAll columns in dataset:")
    for i, col in enumerate(combined_df.columns):
        print(f"  {i+1}. {col} ({combined_df[col].dtype})")
    
    # Show sample data
    print(f"\nSample data (first 5 rows):")
    print(combined_df.head())

def create_basic_visualizations(combined_df):
    """Create basic visualizations"""
    if combined_df.empty:
        print("No data to visualize")
        return
    
    plt.figure(figsize=(15, 10))
    
    # 1. Records by year (if available)
    if 'year' in combined_df.columns:
        plt.subplot(2, 2, 1)
        year_counts = combined_df['year'].value_counts().sort_index()
        plt.bar(year_counts.index, year_counts.values)
        plt.title('Records by Year')
        plt.xlabel('Year')
        plt.ylabel('Number of Records')
        plt.xticks(rotation=45)
    
    # 2. Records by building type (if available)
    if 'building_type' in combined_df.columns:
        plt.subplot(2, 2, 2)
        building_counts = combined_df['building_type'].value_counts()
        plt.pie(building_counts.values, labels=building_counts.index, autopct='%1.1f%%')
        plt.title('Distribution by Building Type')
    
    # 3. Data completeness
    plt.subplot(2, 2, 3)
    missing_data = combined_df.isnull().sum() / len(combined_df) * 100
    missing_data = missing_data.sort_values(ascending=False)[:10]  # Top 10
    
    if len(missing_data) > 0:
        plt.barh(range(len(missing_data)), missing_data.values)
        plt.yticks(range(len(missing_data)), missing_data.index)
        plt.xlabel('Missing Data Percentage')
        plt.title('Top 10 Columns with Missing Data')
    
    # 4. Numeric columns distribution
    numeric_cols = combined_df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        plt.subplot(2, 2, 4)
        # Plot histogram of first numeric column
        first_numeric = numeric_cols[0]
        combined_df[first_numeric].hist(bins=30)
        plt.title(f'Distribution of {first_numeric}')
        plt.xlabel(first_numeric)
        plt.ylabel('Frequency')
    
    plt.tight_layout()
    plt.show()

# Main execution
if __name__ == "__main__":
    print("ELECTRIC POWER DATA LOADER - DIAGNOSTIC VERSION")
    print("="*60)
    
    # Step 1: Diagnose directory structure
    diagnose_directory_structure()
    
    # Step 2: Find all Excel files
    all_files = find_all_excel_files()
    
    # Step 3: Load a sample file to understand structure
    if all_files:
        sample_df = load_sample_file(all_files[0])
    
    # Step 4: Load all data
    combined_df = load_all_data_flexible()
    
    # Step 5: Generate safe summary statistics
    safe_summary_statistics(combined_df)
    
    # Step 6: Create visualizations if data exists
    if not combined_df.empty:
        create_basic_visualizations(combined_df)
        
        # Save combined data
        output_file = "combined_electric_power_data.csv"
        combined_df.to_csv(output_file, index=False)
        print(f"\nCombined data saved to: {output_file}")
    
    print("\nDiagnostic complete!")
    
print("Saving combined data to CSV...")
combined_df.to_csv("combined_electric_power_data.csv", index=False)
print("Data saved to: combined_electric_power_data.csv")