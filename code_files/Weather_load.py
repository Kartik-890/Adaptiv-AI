import os
import csv
from datetime import datetime
from collections import defaultdict, Counter
import pandas as pd


def list_weather_files_to_csv():
    """List weather files and save to CSV with comprehensive reporting"""

    
    # Weather base path
    weather_base = r"C:\Users\karti\Desktop\data_set\Weather data\Weather data"
    
    print("LISTING ALL WEATHER FILES")
    print("="*50)
    
    weather_count = 0
    years_found = set()
    weather_files_data = []
    
    # For detailed reporting
    year_stats = defaultdict(int)
    extension_stats = defaultdict(int)
    folder_stats = defaultdict(int)
    total_size = 0
    
    
    for root, dirs, files in os.walk(weather_base):
        for file in files:
            if file.endswith(('.xlsx', '.xls', '.csv', '.txt')):
                full_path = os.path.join(root, file)
                print(full_path)
                weather_count += 1
                
                # Extract year from path
                year = "Unknown"
                if '2017' in full_path: 
                    years_found.add('2017')
                    year = '2017'
                elif '2018' in full_path: 
                    years_found.add('2018')
                    year = '2018'
                elif '2019' in full_path: 
                    years_found.add('2019')
                    year = '2019'
                elif '2020' in full_path: 
                    years_found.add('2020')
                    year = '2020'
                elif '2021' in full_path: 
                    years_found.add('2021')
                    year = '2021'
                
                # Extract file extension
                file_extension = os.path.splitext(file)[1]
                
                # Get file size
                try:
                    file_size = os.path.getsize(full_path)
                    file_size_mb = round(file_size / (1024 * 1024), 2)
                    total_size += file_size
                except:
                    file_size_mb = 0
                
                # Update statistics
                year_stats[year] += 1
                extension_stats[file_extension] += 1
                folder_stats[os.path.basename(root)] += 1
                
                # Add to data list
                weather_files_data.append({
                    'File_Name': file,
                    'Full_Path': full_path,
                    'Year': year,
                    'File_Extension': file_extension,
                    'File_Size_MB': file_size_mb,
                    'Folder_Path': root
                })
    
    # Generate comprehensive report
    generate_weather_report(weather_count, years_found, year_stats, extension_stats, 
                          folder_stats, total_size, weather_files_data)
    
    # Create CSV file
    csv_filename = f"weather_files_list_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['File_Name', 'Full_Path', 'Year', 'File_Extension', 'File_Size_MB', 'Folder_Path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        # Write header
        writer.writeheader()
        
        # Write data
        for file_data in weather_files_data:
            writer.writerow(file_data)
    
    print(f"\nCSV file created: {csv_filename}")
    print(f"Location: {os.path.abspath(csv_filename)}")
    
    return weather_files_data, csv_filename

def generate_weather_report(weather_count, years_found, year_stats, extension_stats, 
                          folder_stats, total_size, weather_files_data):
    """Generate comprehensive weather data report"""
    
    print("\n" + "="*60)
    print("COMPREHENSIVE WEATHER DATA REPORT")
    print("="*60)
    
    # Basic Statistics
    print(f"\n📊 BASIC STATISTICS")
    print("-" * 30)
    print(f"Total Weather Files Found: {weather_count}")
    print(f"Total Data Size: {round(total_size / (1024 * 1024), 2)} MB")
    print(f"Years Covered: {sorted(years_found)}")
    print(f"Date Range: {min(years_found) if years_found else 'N/A'} - {max(years_found) if years_found else 'N/A'}")
    
    # Files by Year
    print(f"\n📅 FILES BY YEAR")
    print("-" * 30)
    for year in sorted(year_stats.keys()):
        percentage = (year_stats[year] / weather_count) * 100
        print(f"{year}: {year_stats[year]} files ({percentage:.1f}%)")
    
    # Files by Extension
    print(f"\n📁 FILES BY TYPE")
    print("-" * 30)
    for ext in sorted(extension_stats.keys()):
        percentage = (extension_stats[ext] / weather_count) * 100
        print(f"{ext}: {extension_stats[ext]} files ({percentage:.1f}%)")
    
    # Files by Folder
    print(f"\n📂 FILES BY FOLDER")
    print("-" * 30)
    for folder in sorted(folder_stats.keys()):
        percentage = (folder_stats[folder] / weather_count) * 100
        print(f"{folder}: {folder_stats[folder]} files ({percentage:.1f}%)")
    
    # File Size Analysis
    print(f"\n💾 FILE SIZE ANALYSIS")
    print("-" * 30)
    sizes = [file_data['File_Size_MB'] for file_data in weather_files_data if file_data['File_Size_MB'] > 0]
    if sizes:
        print(f"Largest File: {max(sizes):.2f} MB")
        print(f"Smallest File: {min(sizes):.2f} MB")
        print(f"Average File Size: {sum(sizes)/len(sizes):.2f} MB")
        
        # Size categories
        small_files = len([s for s in sizes if s < 1])
        medium_files = len([s for s in sizes if 1 <= s < 10])
        large_files = len([s for s in sizes if s >= 10])
        
        print(f"\nFile Size Distribution:")
        print(f"Small files (<1MB): {small_files}")
        print(f"Medium files (1-10MB): {medium_files}")
        print(f"Large files (>10MB): {large_files}")
    
    # Top 10 Largest Files
    print(f"\n🔝 TOP 10 LARGEST FILES")
    print("-" * 30)
    sorted_files = sorted(weather_files_data, key=lambda x: x['File_Size_MB'], reverse=True)
    for i, file_data in enumerate(sorted_files[:10], 1):
        print(f"{i:2d}. {file_data['File_Name']} - {file_data['File_Size_MB']:.2f} MB ({file_data['Year']})")
    
    # Data Coverage Analysis
    print(f"\n📈 DATA COVERAGE ANALYSIS")
    print("-" * 30)
    if years_found:
        year_range = list(range(int(min(years_found)), int(max(years_found)) + 1))
        missing_years = [str(year) for year in year_range if str(year) not in years_found]
        
        print(f"Complete Years: {len(years_found)}")
        print(f"Expected Years in Range: {len(year_range)}")
        if missing_years:
            print(f"Missing Years: {missing_years}")
        else:
            print("No missing years in the range!")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("-" * 30)
    
    if weather_count == 0:
        print("⚠️  No weather files found. Check the directory path.")
    elif weather_count < 10:
        print("⚠️  Limited data files found. Consider adding more data sources.")
    else:
        print("✅ Good amount of weather data available for analysis.")
    
    if len(extension_stats) > 3:
        print("⚠️  Multiple file formats detected. Consider standardizing to one format.")
    
    if 'Unknown' in year_stats and year_stats['Unknown'] > 0:
        print(f"⚠️  {year_stats['Unknown']} files have unknown years. Consider renaming for better organization.")
    
    # Generate summary report file
    generate_summary_report_file(weather_count, years_found, year_stats, extension_stats, 
                               folder_stats, total_size, weather_files_data)

def generate_summary_report_file(weather_count, years_found, year_stats, extension_stats, 
                               folder_stats, total_size, weather_files_data):
    """Generate a detailed summary report file"""
    
    report_filename = f"weather_data_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(report_filename, 'w', encoding='utf-8') as report_file:
        report_file.write("WEATHER DATA ANALYSIS REPORT\n")
        report_file.write("="*50 + "\n")
        report_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        report_file.write("SUMMARY STATISTICS\n")
        report_file.write("-"*30 + "\n")
        report_file.write(f"Total Files: {weather_count}\n")
        report_file.write(f"Total Size: {round(total_size / (1024 * 1024), 2)} MB\n")
        report_file.write(f"Years: {sorted(years_found)}\n\n")
        
        report_file.write("FILES BY YEAR\n")
        report_file.write("-"*30 + "\n")
        for year in sorted(year_stats.keys()):
            report_file.write(f"{year}: {year_stats[year]} files\n")
        
        report_file.write("\nFILES BY TYPE\n")
        report_file.write("-"*30 + "\n")
        for ext in sorted(extension_stats.keys()):
            report_file.write(f"{ext}: {extension_stats[ext]} files\n")
        
        report_file.write("\nDETAILED FILE LIST\n")
        report_file.write("-"*30 + "\n")
        for file_data in sorted(weather_files_data, key=lambda x: x['Year']):
            report_file.write(f"{file_data['Year']} | {file_data['File_Name']} | {file_data['File_Size_MB']} MB\n")
    
    print(f"\n📄 Detailed report saved: {report_filename}")

if __name__ == "__main__":
    weather_data, csv_file = list_weather_files_to_csv()
