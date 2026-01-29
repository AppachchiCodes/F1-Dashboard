"""
Data loading and preprocessing for F1 Dashboard
Handles all CSV operations and data transformations
"""

import pandas as pd
import os
from typing import Dict, Tuple

class F1DataLoader:
    """Load and process F1 historical data from CSV files"""
    
    def __init__(self, data_dir: str = "../data"):
        self.data_dir = data_dir
        self.races = None
        self.results = None
        self.drivers = None
        self.constructors = None
        self.qualifying = None
        
    def load_all_data(self) -> bool:
        """Load all CSV files and return success status"""
        try:
            # Load CSV files
            self.races = pd.read_csv(os.path.join(self.data_dir, "races.csv"))
            self.results = pd.read_csv(os.path.join(self.data_dir, "results.csv"))
            self.drivers = pd.read_csv(os.path.join(self.data_dir, "drivers.csv"))
            self.constructors = pd.read_csv(os.path.join(self.data_dir, "constructors.csv"))
            self.qualifying = pd.read_csv(os.path.join(self.data_dir, "qualifying.csv"))
            
            # Basic data cleaning
            self._clean_data()
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def _clean_data(self):
        """Clean and prepare data for analysis"""
        # Convert position to numeric, handling 'R' (retired) and 'W' (withdrawn)
        self.results['positionOrder'] = pd.to_numeric(self.results['positionOrder'], errors='coerce')
        
        # Ensure year is integer
        self.races['year'] = self.races['year'].astype(int)
        
        # Handle missing values in points
        self.results['points'] = self.results['points'].fillna(0)
        
    def get_driver_championship_data(self, start_year: int = 2010) -> pd.DataFrame:
        """Get driver championship points progression by year"""
        # Merge results with races to get year information
        merged = self.results.merge(self.races[['raceId', 'year', 'round']], on='raceId')
        
        # Filter by year
        merged = merged[merged['year'] >= start_year]
        
        # Merge with drivers to get driver names
        merged = merged.merge(
            self.drivers[['driverId', 'forename', 'surname']], 
            on='driverId'
        )
        merged['driver_name'] = merged['forename'] + ' ' + merged['surname']
        
        # Calculate cumulative points per driver per year
        merged = merged.sort_values(['year', 'driverId', 'round'])
        merged['cumulative_points'] = merged.groupby(['year', 'driverId'])['points'].cumsum()
        
        return merged[['year', 'round', 'driver_name', 'driverId', 'cumulative_points', 'points']]
    
    def get_constructor_championship_data(self, start_year: int = 2010) -> pd.DataFrame:
        """Get constructor championship data by year"""
        # Merge results with races and constructors
        merged = self.results.merge(self.races[['raceId', 'year']], on='raceId')
        merged = merged.merge(
            self.constructors[['constructorId', 'name']], 
            on='constructorId'
        )
        
        # Filter by year
        merged = merged[merged['year'] >= start_year]
        
        # Group by year and constructor
        constructor_points = merged.groupby(['year', 'name'])['points'].sum().reset_index()
        
        return constructor_points
    
    def get_circuit_stats(self) -> pd.DataFrame:
        """Get statistics for each circuit"""
        # Merge results with races to get circuit info
        merged = self.results.merge(
            self.races[['raceId', 'year', 'name', 'circuitId']], 
            on='raceId'
        )
        
        # Get winners (position 1)
        winners = merged[merged['positionOrder'] == 1].copy()
        
        # Merge with drivers
        winners = winners.merge(
            self.drivers[['driverId', 'forename', 'surname']], 
            on='driverId'
        )
        winners['driver_name'] = winners['forename'] + ' ' + winners['surname']
        
        # Count wins per circuit per driver
        circuit_stats = winners.groupby(['name', 'driver_name']).size().reset_index(name='wins')
        circuit_stats = circuit_stats.sort_values(['name', 'wins'], ascending=[True, False])
        
        return circuit_stats
    
    def get_head_to_head_data(self, driver1_id: int, driver2_id: int) -> Dict:
        """Compare two drivers head-to-head across their careers"""
        # Get all results for both drivers
        driver1_results = self.results[self.results['driverId'] == driver1_id].copy()
        driver2_results = self.results[self.results['driverId'] == driver2_id].copy()
        
        # Merge with races to get year
        driver1_results = driver1_results.merge(self.races[['raceId', 'year']], on='raceId')
        driver2_results = driver2_results.merge(self.races[['raceId', 'year']], on='raceId')
        
        # Get driver names
        driver1_name = self.drivers[self.drivers['driverId'] == driver1_id].iloc[0]
        driver2_name = self.drivers[self.drivers['driverId'] == driver2_id].iloc[0]
        
        comparison = {
            'driver1': f"{driver1_name['forename']} {driver1_name['surname']}",
            'driver2': f"{driver2_name['forename']} {driver2_name['surname']}",
            'driver1_wins': len(driver1_results[driver1_results['positionOrder'] == 1]),
            'driver2_wins': len(driver2_results[driver2_results['positionOrder'] == 1]),
            'driver1_podiums': len(driver1_results[driver1_results['positionOrder'] <= 3]),
            'driver2_podiums': len(driver2_results[driver2_results['positionOrder'] <= 3]),
            'driver1_total_points': driver1_results['points'].sum(),
            'driver2_total_points': driver2_results['points'].sum(),
            'driver1_avg_position': driver1_results['positionOrder'].mean(),
            'driver2_avg_position': driver2_results['positionOrder'].mean(),
        }
        
        return comparison
    
    def get_top_drivers_list(self, limit: int = 20) -> pd.DataFrame:
        """Get list of top drivers by total career points"""
        # Calculate total points per driver
        driver_points = self.results.groupby('driverId')['points'].sum().reset_index()
        driver_points = driver_points.sort_values('points', ascending=False).head(limit)
        
        # Merge with driver names
        driver_points = driver_points.merge(
            self.drivers[['driverId', 'forename', 'surname']], 
            on='driverId'
        )
        driver_points['driver_name'] = driver_points['forename'] + ' ' + driver_points['surname']
        
        return driver_points[['driverId', 'driver_name', 'points']].reset_index(drop=True)