"""
Visualization functions for F1 Dashboard
Creates all Plotly charts and graphs
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime, timezone

# Color scheme for consistent branding
F1_COLORS = {
    'primary': '#E10600',
    'secondary': '#15151E',
    'accent': '#FFFFFF',
    'grid': '#38383F'
}

def create_driver_championship_chart(data: pd.DataFrame, selected_year: int) -> go.Figure:
    """Create animated line chart showing championship progression"""
    # Filter for selected year
    year_data = data[data['year'] == selected_year].copy()
    
    # Get top 10 drivers by final points
    final_standings = year_data.groupby('driver_name')['cumulative_points'].max().sort_values(ascending=False).head(10)
    top_drivers = final_standings.index.tolist()
    
    year_data = year_data[year_data['driver_name'].isin(top_drivers)]
    
    # Create figure
    fig = go.Figure()
    
    # Add line for each driver
    for driver in top_drivers:
        driver_data = year_data[year_data['driver_name'] == driver].sort_values('round')
        
        fig.add_trace(go.Scatter(
            x=driver_data['round'],
            y=driver_data['cumulative_points'],
            mode='lines+markers',
            name=driver,
            line=dict(width=3),
            marker=dict(size=8)
        ))
    
    # Update layout
    fig.update_layout(
        title=f"{selected_year} Driver Championship Progression",
        xaxis_title="Race Number",
        yaxis_title="Cumulative Points",
        hovermode='x unified',
        plot_bgcolor=F1_COLORS['secondary'],
        paper_bgcolor=F1_COLORS['secondary'],
        font=dict(color=F1_COLORS['accent'], size=12),
        legend=dict(
            orientation="v",
            yanchor="top",
            y=0.99,
            xanchor="right",
            x=0.99,
            bgcolor='rgba(21, 21, 30, 0.8)'
        ),
        height=600,
        xaxis=dict(gridcolor=F1_COLORS['grid']),
        yaxis=dict(gridcolor=F1_COLORS['grid'])
    )
    
    return fig

def create_constructor_heatmap(data: pd.DataFrame) -> go.Figure:
    """Create heatmap showing constructor dominance over years"""
    # Pivot data for heatmap
    pivot_data = data.pivot(index='name', columns='year', values='points')
    pivot_data = pivot_data.fillna(0)
    
    # Sort by total points
    pivot_data['total'] = pivot_data.sum(axis=1)
    pivot_data = pivot_data.sort_values('total', ascending=False).head(10)
    pivot_data = pivot_data.drop('total', axis=1)
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_data.values,
        x=pivot_data.columns,
        y=pivot_data.index,
        colorscale='Reds',
        text=pivot_data.values.astype(int),
        texttemplate='%{text}',
        textfont={"size": 10},
        hovertemplate='<b>%{y}</b><br>Year: %{x}<br>Points: %{z}<extra></extra>'
    ))
    
    fig.update_layout(
        title="Constructor Championship Points Heatmap (Top 10 Teams)",
        xaxis_title="Year",
        yaxis_title="Constructor",
        plot_bgcolor=F1_COLORS['secondary'],
        paper_bgcolor=F1_COLORS['secondary'],
        font=dict(color=F1_COLORS['accent'], size=12),
        height=600
    )
    
    return fig

def create_circuit_winners_chart(data: pd.DataFrame, selected_circuit: str) -> go.Figure:
    """Create bar chart showing most successful drivers at a circuit"""
    # Filter for selected circuit
    circuit_data = data[data['name'] == selected_circuit].copy()
    circuit_data = circuit_data.sort_values('wins', ascending=False).head(10)
    
    # Create bar chart
    fig = go.Figure(data=[
        go.Bar(
            x=circuit_data['wins'],
            y=circuit_data['driver_name'],
            orientation='h',
            marker=dict(
                color=F1_COLORS['primary'],
                line=dict(color=F1_COLORS['accent'], width=1)
            ),
            text=circuit_data['wins'],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=f"Most Successful Drivers at {selected_circuit}",
        xaxis_title="Number of Wins",
        yaxis_title="Driver",
        plot_bgcolor=F1_COLORS['secondary'],
        paper_bgcolor=F1_COLORS['secondary'],
        font=dict(color=F1_COLORS['accent'], size=12),
        height=500,
        xaxis=dict(gridcolor=F1_COLORS['grid']),
        yaxis=dict(autorange="reversed")
    )
    
    return fig

def create_head_to_head_comparison(comparison: Dict) -> go.Figure:
    """Create radar chart comparing two drivers"""
    categories = ['Wins', 'Podiums', 'Total Points', 'Avg Position (inverted)']
    
    # Normalize data for radar chart (0-100 scale)
    max_wins = max(comparison['driver1_wins'], comparison['driver2_wins']) or 1
    max_podiums = max(comparison['driver1_podiums'], comparison['driver2_podiums']) or 1
    max_points = max(comparison['driver1_total_points'], comparison['driver2_total_points']) or 1
    
    # For average position, lower is better, so we invert it
    # Assume max position is 20
    driver1_avg_pos_normalized = (20 - comparison['driver1_avg_position']) / 20 * 100
    driver2_avg_pos_normalized = (20 - comparison['driver2_avg_position']) / 20 * 100
    
    driver1_values = [
        (comparison['driver1_wins'] / max_wins) * 100,
        (comparison['driver1_podiums'] / max_podiums) * 100,
        (comparison['driver1_total_points'] / max_points) * 100,
        driver1_avg_pos_normalized
    ]
    
    driver2_values = [
        (comparison['driver2_wins'] / max_wins) * 100,
        (comparison['driver2_podiums'] / max_podiums) * 100,
        (comparison['driver2_total_points'] / max_points) * 100,
        driver2_avg_pos_normalized
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=driver1_values,
        theta=categories,
        fill='toself',
        name=comparison['driver1'],
        line=dict(color='#00D0FF', width=2)
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=driver2_values,
        theta=categories,
        fill='toself',
        name=comparison['driver2'],
        line=dict(color='#FF6600', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                gridcolor=F1_COLORS['grid']
            ),
            bgcolor=F1_COLORS['secondary']
        ),
        showlegend=True,
        title="Head-to-Head Driver Comparison",
        plot_bgcolor=F1_COLORS['secondary'],
        paper_bgcolor=F1_COLORS['secondary'],
        font=dict(color=F1_COLORS['accent'], size=12),
        height=500
    )
    
    return fig

def create_stats_cards(comparison: Dict) -> str:
    """Create HTML for statistics cards"""
    html = f"""
    <style>
        .stats-container {{
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }}
        .stat-card {{
            background: #15151E;
            border: 2px solid #E10600;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            min-width: 150px;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #E10600;
        }}
        .stat-label {{
            font-size: 14px;
            color: #FFFFFF;
            margin-top: 5px;
        }}
        .driver-name {{
            font-size: 18px;
            font-weight: bold;
            color: #FFFFFF;
            margin-bottom: 10px;
        }}
    </style>
    
    <div class="stats-container">
        <div class="stat-card">
            <div class="driver-name">{comparison['driver1']}</div>
            <div class="stat-value">{comparison['driver1_wins']}</div>
            <div class="stat-label">Wins</div>
        </div>
        <div class="stat-card">
            <div class="driver-name">{comparison['driver2']}</div>
            <div class="stat-value">{comparison['driver2_wins']}</div>
            <div class="stat-label">Wins</div>
        </div>
    </div>
    
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-value">{comparison['driver1_podiums']}</div>
            <div class="stat-label">Podiums</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{comparison['driver2_podiums']}</div>
            <div class="stat-label">Podiums</div>
        </div>
    </div>
    
    <div class="stats-container">
        <div class="stat-card">
            <div class="stat-value">{comparison['driver1_total_points']:.0f}</div>
            <div class="stat-label">Career Points</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{comparison['driver2_total_points']:.0f}</div>
            <div class="stat-label">Career Points</div>
        </div>
    </div>
    """
    
    return html


def get_flag_emoji(country_code: str) -> str:
    """Return country flag emoji"""
    flags = {
        'BHR': '🇧🇭', 'SAU': '🇸🇦', 'AUS': '🇦🇺', 'JPN': '🇯🇵', 'CHN': '🇨🇳',
        'USA': '🇺🇸', 'ITA': '🇮🇹', 'MCO': '🇲🇨', 'ESP': '🇪🇸', 'CAN': '🇨🇦',
        'AUT': '🇦🇹', 'GBR': '🇬🇧', 'HUN': '🇭🇺', 'BEL': '🇧🇪', 'NLD': '🇳🇱',
        'AZE': '🇦🇿', 'SGP': '🇸🇬', 'MEX': '🇲🇽', 'BRA': '🇧🇷', 'UAE': '🇦🇪',
        'QAT': '🇶🇦', 'LVA': '🇱🇻', 'PRT': '🇵🇹', 'F1': '🏁'
    }
    return flags.get(country_code, '🏁')


def get_status_icon_svg(is_past: bool, is_next: bool) -> str:
    """Return status icon SVG"""
    if is_next:
        return '''
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="#00D084" stroke-width="2" fill="none"/>
                <circle cx="12" cy="12" r="6" fill="#00D084">
                    <animate attributeName="r" values="6;8;6" dur="1.5s" repeatCount="indefinite"/>
                </circle>
            </svg>
        '''
    elif is_past:
        return '''
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 6L9 17l-5-5" stroke="#666666" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
        '''
    else:
        return '''
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" stroke="#E10600" stroke-width="2" fill="none"/>
            </svg>
        '''


def format_session_time(iso_datetime: str) -> tuple:
    """Format session time to readable format"""
    try:
        dt = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
        date_str = dt.strftime('%a, %b %d')
        time_str = dt.strftime('%H:%M UTC')
        return date_str, time_str
    except:
        return "TBA", "TBA"


def create_schedule_cards_html(schedule_data: List[Dict], next_race_countdown: Optional[Dict] = None) -> str:
    """Create HTML for race schedule cards with F1 styling and ALL session data"""
    
    html = '<div class="schedule-container">'
    
    for race in schedule_data:
        status_class = 'next-race' if race['is_next'] else ('past-race' if race['is_past'] else 'upcoming-race')
        status_icon = get_status_icon_svg(race['is_past'], race['is_next'])
        flag = get_flag_emoji(race['country_code'])
        
        # Get all sessions from the raw race data
        sessions_html = ''
        if 'sessions' in race:
            sessions = race['sessions']
            
            # Session name mapping
            session_names = {
                'fp1': 'Practice 1',
                'fp2': 'Practice 2',
                'fp3': 'Practice 3',
                'qualifying': 'Qualifying',
                'sprint': 'Sprint Race',
                'sprintQualifying': 'Sprint Qualifying',
                'gp': 'Race'
            }
            
            # Session type colors
            session_colors = {
                'fp1': '#666666',
                'fp2': '#666666',
                'fp3': '#666666',
                'qualifying': '#FF6600',
                'sprint': '#00D084',
                'sprintQualifying': '#00D084',
                'gp': '#E10600'
            }
            
            sessions_html = '<div class="sessions-schedule">'
            for key, value in sessions.items():
                if value:
                    date_str, time_str = format_session_time(value)
                    display_name = session_names.get(key, key)
                    color = session_colors.get(key, '#666666')
                    
                    sessions_html += f'''
                    <div class="session-item" style="border-left-color: {color};">
                        <div class="session-info">
                            <div class="session-name">{display_name}</div>
                            <div class="session-time">{date_str} • {time_str}</div>
                        </div>
                    </div>
                    '''
            sessions_html += '</div>'
        
        # Countdown display for next race only
        countdown_html = ''
        if race['is_next']:
            race_timestamp = int(race['date'].timestamp() * 1000)
            countdown_html = f'''
            <div class="countdown-banner" id="countdown-{race['round']}" data-race-time="{race_timestamp}">
                <div class="countdown-section">
                    <div class="countdown-number" id="days-{race['round']}">-</div>
                    <div class="countdown-label">DAYS</div>
                </div>
                <div class="countdown-section">
                    <div class="countdown-number" id="hours-{race['round']}">-</div>
                    <div class="countdown-label">HRS</div>
                </div>
                <div class="countdown-section">
                    <div class="countdown-number" id="minutes-{race['round']}">-</div>
                    <div class="countdown-label">MIN</div>
                </div>
                <div class="countdown-section">
                    <div class="countdown-number" id="seconds-{race['round']}">-</div>
                    <div class="countdown-label">SEC</div>
                </div>
            </div>
            '''
        
        html += f'''
        <div class="race-card {status_class}">
            <div class="race-card-header">
                <div class="round-badge">ROUND {race['round']}</div>
                <div class="status-icon">{status_icon}</div>
            </div>
            
            <div class="race-card-body">
                <div class="race-details">
                    <div class="race-flag">{flag}</div>
                    <h3 class="race-name">{race['race_name']}</h3>
                    <div class="race-location">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            <circle cx="12" cy="10" r="3" stroke="currentColor" stroke-width="2"/>
                        </svg>
                        {race['circuit']}, {race['location']}
                    </div>
                    
                    {sessions_html}
                </div>
            </div>
            
            {countdown_html}
        </div>
        '''
    
    html += '</div>'
    
    # Enhanced CSS + JavaScript for live countdown
    html += '''
    <style>
        .schedule-container {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 24px;
            padding: 20px 0;
        }
        
        .race-card {
            background: linear-gradient(135deg, #15151E 0%, #1a1a2e 100%);
            border-radius: 16px;
            overflow: hidden;
            border: 2px solid #2a2a3e;
            transition: all 0.3s ease;
            position: relative;
        }
        
        .race-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
            border-color: #E10600;
        }
        
        .race-card.next-race {
            border: 3px solid #00D084;
            box-shadow: 0 0 30px rgba(0, 208, 132, 0.3);
        }
        
        .race-card.next-race:hover {
            box-shadow: 0 12px 40px rgba(0, 208, 132, 0.4);
        }
        
        .race-card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: rgba(0, 0, 0, 0.3);
            border-bottom: 1px solid #2a2a3e;
        }
        
        .round-badge {
            font-family: 'Titillium Web', sans-serif;
            font-weight: 700;
            font-size: 0.75rem;
            letter-spacing: 1px;
            color: #E10600;
            background: rgba(225, 6, 0, 0.1);
            padding: 6px 12px;
            border-radius: 6px;
            border: 1px solid #E10600;
        }
        
        .status-icon {
            display: flex;
            align-items: center;
        }
        
        .race-card-body {
            padding: 24px 20px;
        }
        
        .race-details {
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .race-flag {
            font-size: 3rem;
            line-height: 1;
            margin-bottom: 8px;
        }
        
        .race-name {
            font-family: 'Titillium Web', sans-serif;
            font-weight: 700;
            font-size: 1.4rem;
            color: #FFFFFF;
            margin: 0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            line-height: 1.3;
        }
        
        .race-location {
            display: flex;
            align-items: center;
            gap: 6px;
            font-size: 0.95rem;
            color: #AAAAAA;
            font-weight: 500;
            margin-bottom: 8px;
        }
        
        .sessions-schedule {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 12px;
        }
        
        .session-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 16px;
            background: rgba(225, 6, 0, 0.05);
            border-radius: 8px;
            border-left: 4px solid #E10600;
            transition: all 0.2s ease;
        }
        
        .session-item:hover {
            background: rgba(225, 6, 0, 0.1);
            transform: translateX(5px);
        }
        
        .session-info {
            flex: 1;
        }
        
        .session-name {
            font-family: 'Titillium Web', sans-serif;
            font-weight: 600;
            font-size: 0.9rem;
            color: #FFFFFF;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .session-time {
            font-size: 0.85rem;
            color: #AAAAAA;
            margin-top: 2px;
        }
        
        .countdown-banner {
            display: flex;
            justify-content: space-around;
            padding: 20px;
            background: linear-gradient(135deg, #00D084 0%, #00a066 100%);
            border-top: 2px solid #00D084;
        }
        
        .countdown-section {
            text-align: center;
        }
        
        .countdown-number {
            font-family: 'Titillium Web', sans-serif;
            font-weight: 700;
            font-size: 2rem;
            color: #FFFFFF;
            line-height: 1;
        }
        
        .countdown-label {
            font-family: 'Titillium Web', sans-serif;
            font-weight: 600;
            font-size: 0.7rem;
            color: rgba(255, 255, 255, 0.9);
            margin-top: 4px;
            letter-spacing: 1px;
        }
        
        @media (max-width: 768px) {
            .schedule-container {
                grid-template-columns: 1fr;
            }
        }
    </style>
    
    <script>
        function updateCountdowns() {
            const countdownElements = document.querySelectorAll('[id^="countdown-"]');
            
            countdownElements.forEach(element => {
                const raceTime = parseInt(element.getAttribute('data-race-time'));
                const now = Date.now();
                const diff = raceTime - now;
                
                if (diff > 0) {
                    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
                    
                    const round = element.id.split('-')[1];
                    const daysEl = document.getElementById('days-' + round);
                    const hoursEl = document.getElementById('hours-' + round);
                    const minutesEl = document.getElementById('minutes-' + round);
                    const secondsEl = document.getElementById('seconds-' + round);
                    
                    if (daysEl) daysEl.textContent = days;
                    if (hoursEl) hoursEl.textContent = String(hours).padStart(2, '0');
                    if (minutesEl) minutesEl.textContent = String(minutes).padStart(2, '0');
                    if (secondsEl) secondsEl.textContent = String(seconds).padStart(2, '0');
                }
            });
        }
        
        updateCountdowns();
        setInterval(updateCountdowns, 1000);
    </script>
    '''
    
    return html