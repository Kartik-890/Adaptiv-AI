import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import warnings
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from scipy import stats
import seaborn as sns
warnings.filterwarnings('ignore')

# Set style for better plots
plt.style.use('seaborn-v0_8')

def load_power_data():
    power_df = pd.read_csv("combined_electric_power_data.csv")
    power_df['Time'] = pd.to_datetime(power_df['Time'])
    power_df = power_df.dropna(subset=['Power (kW)'])
    return power_df.sort_values('Time')

def plot_rolling_statistics(df):
    # Create a daily aggregated dataframe for smoother analysis
    daily_df = df.groupby(df['Time'].dt.date)['Power (kW)'].agg(['mean', 'std', 'median']).reset_index()
    daily_df['Time'] = pd.to_datetime(daily_df['Time'])
    
    # Calculate rolling statistics with 30-day window
    window_size = 30
    daily_df['rolling_mean'] = daily_df['mean'].rolling(window=window_size).mean()
    daily_df['rolling_std'] = daily_df['std'].rolling(window=window_size).mean()
    daily_df['rolling_cv'] = daily_df['rolling_std'] / daily_df['rolling_mean']  # Coefficient of variation
    daily_df['rolling_skew'] = daily_df['mean'].rolling(window=window_size).apply(lambda x: stats.skew(x))
    
    # Plot the rolling statistics
    fig, axs = plt.subplots(3, 1, figsize=(15, 15), sharex=True)
    
    # Rolling mean and standard deviation
    axs[0].plot(daily_df['Time'], daily_df['rolling_mean'], 
                label='30-day Rolling Mean', color='blue', linewidth=2)
    axs[0].fill_between(daily_df['Time'], 
                       daily_df['rolling_mean'] - daily_df['rolling_std'],
                       daily_df['rolling_mean'] + daily_df['rolling_std'],
                       color='blue', alpha=0.2, label='±1 Std Dev')
    axs[0].set_title('Rolling Mean with Standard Deviation Band (30-day window)', 
                    fontsize=14, fontweight='bold')
    axs[0].set_ylabel('Power (kW)')
    axs[0].legend()
    axs[0].grid(True, alpha=0.3)
    
    # Coefficient of variation
    axs[1].plot(daily_df['Time'], daily_df['rolling_cv'], 
                label='Coefficient of Variation', color='green', linewidth=2)
    axs[1].set_title('Rolling Coefficient of Variation (30-day window)', 
                    fontsize=14, fontweight='bold')
    axs[1].set_ylabel('CV (Std/Mean)')
    axs[1].legend()
    axs[1].grid(True, alpha=0.3)
    
    # Skewness
    axs[2].plot(daily_df['Time'], daily_df['rolling_skew'], 
                label='Skewness', color='purple', linewidth=2)
    axs[2].axhline(y=0, color='red', linestyle='--', alpha=0.7)
    axs[2].set_title('Rolling Skewness (30-day window)', fontsize=14, fontweight='bold')
    axs[2].set_ylabel('Skewness')
    axs[2].set_xlabel('Date')
    axs[2].legend()
    axs[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('08_rolling_statistics.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_autocorrelation(df):
    # Create hourly resampled data for autocorrelation analysis
    hourly_df = df.set_index('Time').resample('H')['Power (kW)'].mean().reset_index()
    hourly_df = hourly_df.dropna()
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
    
    # Autocorrelation function (ACF) - shows correlation with lagged values
    plot_acf(hourly_df['Power (kW)'], lags=168, ax=ax1)  # 168 hours = 1 week
    ax1.set_title('Autocorrelation Function (Hourly Data)', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Add vertical lines at 24, 48, 72, ... hours to highlight daily patterns
    for i in range(1, 8):
        ax1.axvline(x=i*24, color='red', linestyle='--', alpha=0.5, 
                   label='Daily cycle' if i==1 else None)
    
    # Partial Autocorrelation Function (PACF) - shows direct correlation with lagged values
    plot_pacf(hourly_df['Power (kW)'], lags=72, ax=ax2)  # 72 hours = 3 days
    ax2.set_title('Partial Autocorrelation Function (Hourly Data)', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # Add vertical lines at 24, 48, 72 hours
    for i in range(1, 4):
        ax2.axvline(x=i*24, color='red', linestyle='--', alpha=0.5, 
                   label='Daily cycle' if i==1 else None)
    
    plt.tight_layout()
    plt.savefig('09_autocorrelation.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # Create a more detailed daily lag plot
    plt.figure(figsize=(15, 8))
    
    # Add time features for correlation analysis
    hourly_df['hour'] = hourly_df['Time'].dt.hour
    hourly_df['day_of_week'] = hourly_df['Time'].dt.dayofweek
    hourly_df['month'] = hourly_df['Time'].dt.month
    
    # Create lagged features
    for lag in [1, 24, 48, 168]:  # 1 hour, 1 day, 2 days, 1 week
        hourly_df[f'lag_{lag}h'] = hourly_df['Power (kW)'].shift(lag)
    
    # Drop NaN values from lagged features
    hourly_df = hourly_df.dropna()
    
    # Create scatter plots of current vs lagged values
    fig, axs = plt.subplots(2, 2, figsize=(15, 12))
    axs = axs.flatten()
    
    lags = [1, 24, 48, 168]
    titles = ['1-Hour Lag', '24-Hour (Daily) Lag', '48-Hour (2-Day) Lag', '168-Hour (Weekly) Lag']
    
    for i, (lag, title) in enumerate(zip(lags, titles)):
        axs[i].scatter(hourly_df[f'lag_{lag}h'], hourly_df['Power (kW)'], 
                      alpha=0.5, s=10, color='blue')
        
        # Add correlation coefficient
        corr = hourly_df[f'lag_{lag}h'].corr(hourly_df['Power (kW)'])
        axs[i].set_title(f'{title}\nCorrelation: {corr:.3f}', fontsize=14, fontweight='bold')
        axs[i].set_xlabel(f'Power (kW) at t-{lag}')
        axs[i].set_ylabel('Power (kW) at t')
        axs[i].grid(True, alpha=0.3)
        
        # Add diagonal line
        min_val = min(hourly_df[f'lag_{lag}h'].min(), hourly_df['Power (kW)'].min())
        max_val = max(hourly_df[f'lag_{lag}h'].max(), hourly_df['Power (kW)'].max())
        axs[i].plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.7)
    
    plt.tight_layout()
    plt.savefig('10_lag_scatter_plots.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return hourly_df  # Return the hourly dataframe with lag features for correlation analysis

def plot_spearman_correlation(hourly_df, df):
    # Create correlation matrices
    
    # 1. Time features correlation with power
    plt.figure(figsize=(12, 10))
    
    # Create time features for original dataframe
    df_time = df.copy()
    df_time['hour'] = df_time['Time'].dt.hour
    df_time['day_of_week'] = df_time['Time'].dt.dayofweek
    df_time['day_of_month'] = df_time['Time'].dt.day
    df_time['month'] = df_time['Time'].dt.month
    df_time['year'] = df_time['Time'].dt.year
    df_time['is_weekend'] = df_time['Time'].dt.dayofweek >= 5
    
    # Select features for correlation
    time_features = ['hour', 'day_of_week', 'day_of_month', 'month', 'year', 'is_weekend', 'Power (kW)']
    
    # Calculate Spearman correlation
    corr_time = df_time[time_features].corr(method='spearman')
    
    # Plot heatmap
    sns.heatmap(corr_time, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, 
               fmt='.2f', linewidths=0.5)
    plt.title('Spearman Correlation: Time Features vs Power', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('11_spearman_correlation_time.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 2. Lag features correlation with power
    plt.figure(figsize=(12, 10))
    
    # Select lag features
    lag_cols = [col for col in hourly_df.columns if 'lag_' in col] + ['Power (kW)', 'hour', 'day_of_week', 'month']
    
    # Calculate Spearman correlation
    corr_lag = hourly_df[lag_cols].corr(method='spearman')
    
    # Plot heatmap
    sns.heatmap(corr_lag, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, 
               fmt='.2f', linewidths=0.5)
    plt.title('Spearman Correlation: Lag Features vs Power', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('12_spearman_correlation_lag.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    # 3. Building type correlation analysis
    if 'building_type' in df.columns:
        # Create dummy variables for building types
        building_dummies = pd.get_dummies(df['building_type'], prefix='building')
        df_building = pd.concat([df[['Power (kW)']], building_dummies], axis=1)
        
        # Calculate Spearman correlation
        corr_building = df_building.corr(method='spearman')
        
        # Plot heatmap
        plt.figure(figsize=(12, 10))
        sns.heatmap(corr_building, annot=True, cmap='coolwarm', vmin=-1, vmax=1, center=0, 
                   fmt='.2f', linewidths=0.5)
        plt.title('Spearman Correlation: Building Types vs Power', fontsize=16, fontweight='bold')
        plt.tight_layout()
        plt.savefig('13_spearman_correlation_building.png', dpi=300, bbox_inches='tight')
        plt.show()

def main():
    print("Creating Power Load Time Series Analysis with Enhanced Visualizations...")
    
    # Load data
    df = load_power_data()
    print(f"Loaded {len(df)} records")
    
    # Plot new visualizations
    print("Generating rolling statistics plots...")
    plot_rolling_statistics(df)
    
    print("Generating autocorrelation plots...")
    hourly_df = plot_autocorrelation(df)
    
    print("Generating Spearman correlation matrices...")
    plot_spearman_correlation(hourly_df, df)
    
    print("Analysis complete. All plots saved.")
    
if __name__ == "__main__":
    main()
