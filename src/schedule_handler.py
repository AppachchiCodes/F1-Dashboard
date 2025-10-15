"""
Schedule Handler for F1 Dashboard
Reads race calendar from local JSON file
"""

import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Optional
import streamlit as st

class F1ScheduleHandler:
    """Handles F1 race schedule from local JSON file"""
    
    def __init__(self, year: int = 2025):
        self.year = year
        self.races = []
        
    def load_schedule(self) -> bool:
        """Load schedule from local JSON file"""
        try:
            # Try multiple path strategies
            possible_paths = [
                os.path.join('data', f'f1-{self.year}-schedule.json'),
                os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', f'f1-{self.year}-schedule.json'),
                f'data/f1-{self.year}-schedule.json',
                f'./data/f1-{self.year}-schedule.json'
            ]
            
            json_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    json_path = path
                    break
            
            if not json_path:
                print(f"Could not find schedule file. Tried paths:")
                for path in possible_paths:
                    print(f"  - {path} (exists: {os.path.exists(path)})")
                print(f"Current working directory: {os.getcwd()}")
                return False
            
            print(f"Loading schedule from: {json_path}")
            
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.races = data.get('races', [])
            
            print(f"Loaded {len(self.races)} races")
            return len(self.races) > 0
            
        except Exception as e:
            print(f"Error loading schedule: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_next_race(self) -> Optional[Dict]:
        """Get the next upcoming race"""
        now = datetime.now(timezone.utc)
        
        for race in self.races:
            try:
                race_date = datetime.fromisoformat(race['sessions']['gp'].replace('Z', '+00:00'))
                if race_date > now:
                    return race
            except:
                continue
        
        return None
    
    def calculate_countdown(self, target_date_str: str) -> Dict[str, int]:
        """Calculate time until target date"""
        now = datetime.now(timezone.utc)
        target = datetime.fromisoformat(target_date_str.replace('Z', '+00:00'))
        delta = target - now
        
        if delta.total_seconds() < 0:
            return {'days': 0, 'hours': 0, 'minutes': 0, 'seconds': 0, 'expired': True}
        
        days = delta.days
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return {
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'expired': False
        }
    
    def get_formatted_schedule(self) -> List[Dict]:
        """Get formatted schedule data for display - UPCOMING RACES ONLY"""
        formatted = []
        now = datetime.now(timezone.utc)
        
        for race in self.races:
            try:
                race_date = datetime.fromisoformat(race['sessions']['gp'].replace('Z', '+00:00'))
                
                # ONLY include future races
                if race_date < now:
                    continue
                
                # Map country codes
                country_codes = {
                    'Australian': 'AUS', 'Chinese': 'CHN', 'Japanese': 'JPN',
                    'Bahrain': 'BHR', 'Saudi Arabian': 'SAU', 'Miami': 'USA',
                    'Emilia Romagna Grand Prix': 'ITA', 'Monaco': 'MCO',
                    'Spanish': 'ESP', 'Canadian': 'CAN', 'Austrian': 'AUT',
                    'British': 'GBR', 'Belgian': 'BEL', 'Hungarian': 'HUN',
                    'Dutch': 'NLD', 'Italian': 'ITA', 'Azerbaijan': 'AZE',
                    'Singapore': 'SGP', 'United States': 'USA', 'Mexican': 'MEX',
                    'Brazilian': 'BRA', 'Las Vegas': 'USA', 'Qatar': 'QAT',
                    'Abu Dhabi': 'UAE'
                }
                
                formatted.append({
                    'meeting_key': race['round'],
                    'round': race['round'],
                    'race_name': f"{race['name']} Grand Prix",
                    'country': race['name'],
                    'country_code': country_codes.get(race['name'], 'F1'),
                    'circuit': race['location'],
                    'location': race['location'],
                    'date': race_date,
                    'date_str': race_date.strftime('%B %d, %Y'),
                    'time_str': race_date.strftime('%H:%M'),
                    'is_past': False,
                    'is_next': False,
                    'sessions': race['sessions']
                })
            except Exception as e:
                print(f"Error processing race: {e}")
                continue
        
        # Sort by date
        formatted.sort(key=lambda x: x['date'])
        
        # Mark the first race as "next"
        if formatted:
            formatted[0]['is_next'] = True
        
        return formatted

@st.cache_data(ttl=3600)
def load_schedule(year: int = 2025):
    """Load schedule with caching"""
    handler = F1ScheduleHandler(year=year)
    if handler.load_schedule():
        return handler
    return None