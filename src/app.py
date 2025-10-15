"""
F1 Historical Data Dashboard
Main Streamlit application with enhanced styling and schedule
"""

import streamlit as st
import sys
import os
import time

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import F1DataLoader
from src.schedule_handler import load_schedule
from src.visualizations import (
    create_driver_championship_chart,
    create_constructor_heatmap,
    create_circuit_winners_chart,
    create_head_to_head_comparison,
    create_stats_cards,
    create_schedule_cards_html
)

# Page configuration
st.set_page_config(
    page_title="F1 Analytics Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with Titillium Web font
st.markdown("""
    <style>
        /* Import Titillium Web font */
        @import url('https://fonts.googleapis.com/css2?family=Titillium+Web:wght@300;400;500;600;700;900&display=swap');
        
        /* Main background and fonts */
        .main {
            background: linear-gradient(135deg, #0E1117 0%, #1a1a2e 100%);
        }
        
        html, body, [class*="css"] {
            font-family: 'Titillium Web', sans-serif;
        }
        
        /* Header styling */
        h1 {
            font-family: 'Titillium Web', sans-serif !important;
            font-weight: 900 !important;
            font-size: 3.5rem !important;
            text-transform: uppercase !important;
            letter-spacing: 2px !important;
            background: linear-gradient(90deg, #E10600 0%, #FF6600 50%, #E10600 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            animation: shimmer 3s infinite;
            margin-bottom: 0 !important;
        }
        
        @keyframes shimmer {
            0%, 100% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
        }
        
        h2, h3 {
            color: #FFFFFF !important;
            font-weight: 700 !important;
            text-transform: uppercase !important;
            letter-spacing: 1px !important;
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: rgba(21, 21, 30, 0.6);
            padding: 10px;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 60px;
            background: linear-gradient(135deg, #15151E 0%, #2a2a3e 100%);
            border-radius: 10px;
            color: #FFFFFF;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 2px solid transparent;
            transition: all 0.3s ease;
            padding: 0 30px;
        }
        
        .stTabs [data-baseweb="tab"]:hover {
            border-color: #E10600;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(225, 6, 0, 0.3);
        }
        
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, #E10600 0%, #FF6600 100%);
            border-color: #FF6600;
            box-shadow: 0 5px 20px rgba(225, 6, 0, 0.5);
        }
        
        /* Select boxes */
        .stSelectbox > div > div {
            background-color: #15151E;
            border: 2px solid #E10600;
            border-radius: 8px;
            color: #FFFFFF;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        
        .stSelectbox > div > div:hover {
            border-color: #FF6600;
            box-shadow: 0 0 15px rgba(225, 6, 0, 0.3);
        }
        
        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #E10600 0%, #FF6600 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 15px 40px;
            font-weight: 700;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(225, 6, 0, 0.4);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(225, 6, 0, 0.6);
        }
        
        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 2.5rem;
            font-weight: 900;
            color: #E10600;
        }
        
        [data-testid="stMetricLabel"] {
            font-size: 1rem;
            font-weight: 600;
            color: #FFFFFF;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Metric containers */
        [data-testid="metric-container"] {
            background: linear-gradient(135deg, #15151E 0%, #2a2a3e 100%);
            padding: 20px;
            border-radius: 12px;
            border: 2px solid #E10600;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        
        [data-testid="metric-container"]:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(225, 6, 0, 0.4);
        }
        
        /* Markdown text */
        .stMarkdown {
            color: #CCCCCC;
            font-size: 1rem;
            font-weight: 400;
        }
        
        /* Success/Info boxes */
        .stSuccess {
            background-color: rgba(0, 208, 132, 0.1);
            border-left: 4px solid #00D084;
            padding: 15px;
            border-radius: 8px;
            font-weight: 500;
        }
        
        /* Loading animation */
        .stSpinner > div {
            border-color: #E10600 transparent transparent transparent !important;
        }
        
        /* Divider */
        hr {
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #E10600, transparent);
            margin: 30px 0;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 10px;
            height: 10px;
        }
        
        ::-webkit-scrollbar-track {
            background: #15151E;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #E10600;
            border-radius: 5px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #FF6600;
        }
        
        /* Plotly charts */
        .js-plotly-plot {
            border-radius: 12px;
            overflow: hidden;
        }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_data():
    """Load F1 historical data with caching"""
    loader = F1DataLoader()
    if loader.load_all_data():
        return loader
    else:
        st.error("Failed to load data. Please check that CSV files are in the 'data' folder.")
        return None

def show_loading_screen():
    """Display animated loading screen"""
    loading_html = """
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 400px;">
        <div style="font-size: 80px; animation: race 2s infinite;">🏎️</div>
        <h2 style="color: #E10600; margin-top: 20px; font-family: 'Titillium Web', sans-serif; font-weight: 700; text-transform: uppercase; animation: pulse 1.5s infinite;">Loading F1 Data</h2>
        <div style="width: 300px; height: 4px; background: #15151E; border-radius: 2px; margin-top: 20px; overflow: hidden;">
            <div style="width: 100%; height: 100%; background: linear-gradient(90deg, #E10600, #FF6600); animation: loading 1.5s infinite;"></div>
        </div>
    </div>
    
    <style>
        @keyframes race {
            0%, 100% { transform: translateX(-50px); }
            50% { transform: translateX(50px); }
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        @keyframes loading {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
    </style>
    """
    return loading_html

def main():
    # Animated Header
    st.markdown("""
        <div style="text-align: center; padding: 20px 0;">
            <h1>Formula 1 Analytics</h1>
            <p style="font-size: 1.2rem; color: #CCCCCC; margin-top: -10px; font-weight: 400; letter-spacing: 1px;">
                EXPLORING SEVEN DECADES OF RACING EXCELLENCE
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Show loading screen while data loads
    loading_placeholder = st.empty()
    loading_placeholder.markdown(show_loading_screen(), unsafe_allow_html=True)
    
    # Load historical data
    loader = load_data()
    
    # Load schedule data
    schedule_handler = load_schedule(2025)
    
    # Clear loading screen
    time.sleep(0.5)
    loading_placeholder.empty()
    
    if loader is None:
        st.stop()
    
    # Create tabs 
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "RACE CALENDAR",
        "CHAMPIONSHIP EVOLUTION",
        "CONSTRUCTOR DOMINANCE",
        "CIRCUIT ANALYSIS",
        "DRIVER COMPARISONS"
    ])
    
    # TAB 1: Race Schedule
    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("2025 FIA Formula 1 World Championship")
        st.markdown("*Complete race calendar with live countdown to the next Grand Prix*")
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Load schedule
        schedule_handler_local = load_schedule(2025)
        
        if schedule_handler_local and schedule_handler_local.races:
            schedule_data = schedule_handler_local.get_formatted_schedule()
            
            if schedule_data:
                next_race = schedule_handler_local.get_next_race()
                
                countdown = None
                if next_race:
                    countdown = schedule_handler_local.calculate_countdown(next_race['sessions']['gp'])
                
                # Show upcoming races count
                st.success(f"🏁 **{len(schedule_data)} upcoming race(s)** in the 2025 season")
                
                # Render cards
                html_output = create_schedule_cards_html(schedule_data, countdown)
                st.components.v1.html(html_output, height=800, scrolling=True)
            else:
                st.info("🏆 **2025 F1 Season Complete!** All races have finished.")
                
        else:
            st.error("Unable to load 2025 F1 schedule. Please check that the schedule file exists in the data folder.")
            
    # TAB 2: Championship Evolution
    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("Driver Championship Progression")
        st.markdown("*Watch how championships unfold race by race*")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            available_years = sorted(loader.races['year'].unique(), reverse=True)
            available_years = [y for y in available_years if y >= 2010]
            
            st.markdown("<br>", unsafe_allow_html=True)
            selected_year = st.selectbox(
                "SELECT SEASON",
                available_years,
                index=0
            )
        
        championship_data = loader.get_driver_championship_data(start_year=2010)
        
        with st.spinner('Generating championship visualization...'):
            fig = create_driver_championship_chart(championship_data, selected_year)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader(f"Final Top 5 - {selected_year} Season")
        
        year_final = championship_data[championship_data['year'] == selected_year]
        final_standings = year_final.groupby('driver_name')['cumulative_points'].max().sort_values(ascending=False).head(5)
        
        cols = st.columns(5)
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        
        for idx, (col, (driver, points)) in enumerate(zip(cols, final_standings.items())):
            with col:
                st.metric(
                    label=f"{medals[idx]} {driver.split()[-1]}",
                    value=f"{points:.0f}",
                    delta="pts"
                )
    
    # TAB 3: Constructor Dominance
    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("Constructor Championship Heatmap")
        st.markdown("*Visualize team performance and dominance across seasons*")
        
        constructor_data = loader.get_constructor_championship_data(start_year=2010)
        
        with st.spinner('Building constructor dominance map...'):
            fig = create_constructor_heatmap(constructor_data)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #15151E 0%, #2a2a3e 100%); 
                        padding: 20px; border-radius: 12px; border-left: 4px solid #E10600;">
                <h4 style="color: #E10600; margin-top: 0;">HEAT INTENSITY</h4>
                <p style="color: #CCCCCC;">Darker red indicates more points scored</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #15151E 0%, #2a2a3e 100%); 
                        padding: 20px; border-radius: 12px; border-left: 4px solid #FF6600;">
                <h4 style="color: #FF6600; margin-top: 0;">TOP TEAMS</h4>
                <p style="color: #CCCCCC;">Shows top 10 constructors by total points</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #15151E 0%, #2a2a3e 100%); 
                        padding: 20px; border-radius: 12px; border-left: 4px solid #00D0FF;">
                <h4 style="color: #00D0FF; margin-top: 0;">PATTERNS</h4>
                <p style="color: #CCCCCC;">Identify dominant eras for each team</p>
            </div>
            """, unsafe_allow_html=True)
    
    # TAB 4: Circuit Analysis
    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("Circuit Performance Analysis")
        st.markdown("*Discover the masters of each legendary track*")
        
        circuit_stats = loader.get_circuit_stats()
        available_circuits = sorted(circuit_stats['name'].unique())
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_circuit = st.selectbox(
                "SELECT CIRCUIT",
                available_circuits,
                index=available_circuits.index("Monaco Grand Prix") if "Monaco Grand Prix" in available_circuits else 0
            )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.spinner('Analyzing circuit data...'):
            fig = create_circuit_winners_chart(circuit_stats, selected_circuit)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        circuit_data = circuit_stats[circuit_stats['name'] == selected_circuit]
        total_races = circuit_data['wins'].sum()
        most_successful = circuit_data.iloc[0]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("TOTAL RACES", total_races)
        with col2:
            st.metric("CIRCUIT KING", most_successful['driver_name'])
        with col3:
            st.metric("VICTORIES", int(most_successful['wins']))
    
    # TAB 5: Driver Comparisons
    with tab5:
        st.markdown("<br>", unsafe_allow_html=True)
        st.header("Head-to-Head Driver Comparison")
        st.markdown("*Compare racing legends and see who dominated the sport*")
        
        top_drivers = loader.get_top_drivers_list(limit=30)
        
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            driver1_name = st.selectbox(
                "DRIVER 1",
                top_drivers['driver_name'].tolist(),
                index=0
            )
            driver1_id = top_drivers[top_drivers['driver_name'] == driver1_name]['driverId'].values[0]
        
        with col2:
            driver2_name = st.selectbox(
                "DRIVER 2",
                top_drivers['driver_name'].tolist(),
                index=1 if len(top_drivers) > 1 else 0
            )
            driver2_id = top_drivers[top_drivers['driver_name'] == driver2_name]['driverId'].values[0]
        
        with col3:
            st.markdown("<br><br>", unsafe_allow_html=True)
            compare_button = st.button("COMPARE", type="primary", use_container_width=True)
        
        if compare_button:
            with st.spinner('Analyzing driver statistics...'):
                time.sleep(0.5)
                
                comparison = loader.get_head_to_head_data(driver1_id, driver2_id)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(create_stats_cards(comparison), unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                fig = create_head_to_head_comparison(comparison)
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("---")
                
                if comparison['driver1_total_points'] > comparison['driver2_total_points']:
                    winner = comparison['driver1']
                    margin = comparison['driver1_total_points'] - comparison['driver2_total_points']
                    color = "#00D0FF"
                else:
                    winner = comparison['driver2']
                    margin = comparison['driver2_total_points'] - comparison['driver1_total_points']
                    color = "#FF6600"
                
                st.markdown(f"""
                    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #15151E 0%, #2a2a3e 100%); 
                                border-radius: 15px; border: 3px solid {color}; box-shadow: 0 0 30px rgba(225, 6, 0, 0.3);">
                        <h2 style="color: {color}; margin: 0; font-size: 2.5rem; text-transform: uppercase; font-weight: 900;">{winner}</h2>
                        <p style="color: #FFFFFF; font-size: 1.5rem; margin-top: 10px; font-weight: 500;">
                            LEADS BY <span style="color: {color}; font-weight: 900;">{margin:.0f}</span> CAREER POINTS
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; padding: 20px;'>
        <p style='color: #666; font-size: 0.85rem; font-weight: 500; letter-spacing: 0.5px;'>
            DATA SOURCE: KAGGLE F1 HISTORICAL DATASET (1950-2024) & OPENF1 API<br>
            BUILT WITH PYTHON, STREAMLIT & PLOTLY<br>
            <span style='color: #E10600; font-weight: 700; text-transform: uppercase;'>FORMULA 1 ANALYTICS DASHBOARD - PROJECT BY U. HEWAGE</span>
        </p>
        <p style='color: #888; font-size: 0.75rem; margin-top: 10px; font-style: italic;'>
            This is an unofficial project and is not associated with Formula 1 companies.<br>
            F1, FORMULA ONE, FORMULA 1, FIA FORMULA ONE WORLD CHAMPIONSHIP, GRAND PRIX and related marks are trademarks of Formula One Licensing B.V.
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()