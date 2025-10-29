import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuration and Setup ---
st.set_page_config(
    page_title="EmiMeter: Logistics Emissions Calculator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Emission Factors (kg/unit) ---
# Extracted directly from the provided table (Page 5)
FACTORS = {
    'Cars': 0.18,        # kg/km
    'Trucks': 0.90,      # kg/km
    'Buses': 1.10,       # kg/km
    'Forklifts': 4.0,    # kg/hour
    'Planes': 9000.0,    # kg/hour
    'Lighting': 0.42,    # kg/kWh
    'Heating': 0.20,     # kg/kWh-th
    'Cooling': 0.42,     # kg/kWh
    'Computing': 0.42    # kg/kWh
}

DEFAULT_ACTIVITY_DATA = {
    'Cars_km': 250000,
    'Trucks_km': 150000,
    'Buses_km': 80000,
    'Forklifts_hr': 2000,
    'Planes_hr': 400,
    'Lighting_kWh': 120000,
    'Heating_kWhth': 50000,
    'Cooling_kWh': 300000,
    'Computing_kWh': 90000,
    # Subcontractors: Sub1, Sub2, Sub3
    'Subcontractors_tCO2e': [120, 45, 20] # Values from screenshot seem to be 120, 45, 20 (or 20/30/Formula)
}

# --- Core Calculation Logic ---

# Important: This function calculates the tCO2e for a single category based on the formula provided in the document.
def calculate_category_emissions(category, activity_data, adjustments=None):
    """
    Calculates CO2 emissions (tons CO2e) based on the specific formula from the provided table.
    The formula already incorporates the division by 1000 to convert kg to tons.
    """
    adjustments = adjustments if adjustments is not None else {}
    
    # Extract activity data
    A = activity_data
    F = FACTORS
    
    # --- Category-Specific Formulas (tons CO₂e) ---
    
    if category == 'Cars':
        # Formula: ((cars_km * 0.18) * (1 - 0.7 * EV/100) * (1 - KMRed/100)) / 1000
        # EV Share (%) and KM Reduction (%) are the adjustments
        EV = adjustments.get('EV_Share', 0)
        KMRed = adjustments.get('KM_Reduction', 0)
        
        # Note: The formula provided is slightly unusual with the + 1000 in the PDF text,
        # but the structure implies division by 1000. We follow the clear structure.
        emissions_kg = (A['Cars_km'] * F['Cars']) * (1 - 0.7 * EV / 100) * (1 - KMRed / 100)
        return emissions_kg / 1000
    
    elif category == 'Trucks':
        # Formula: (Trucks_km * 0.90) / 1000
        return (A['Trucks_km'] * F['Trucks']) / 1000
    
    elif category == 'Buses':
        # Formula: (Buses_km * 1.10) / 1000
        return (A['Buses_km'] * F['Buses']) / 1000
        
    elif category == 'Forklifts':
        # Formula: (Forklifts_hr * 4.0) / 1000
        return (A['Forklifts_hr'] * F['Forklifts']) / 1000
        
    elif category == 'Cargo Planes':
        # Formula: ((Planes_hr * 9000) * (LoadFactor/100)) / 1000
        # Load Factor (%) is the adjustment
        LoadFactor = adjustments.get('Load_Factor', 100) # Baseline is 100%
        emissions_kg = (A['Planes_hr'] * F['Planes']) * (LoadFactor / 100)
        return emissions_kg / 1000
        
    elif category == 'Office Lighting':
        # Formula: (Lighting_kWh * 0.42) / 1000
        return (A['Lighting_kWh'] * F['Lighting']) / 1000
    
    elif category == 'Heating':
        # Formula: (Heating_kWhth * 0.20) / 1000
        return (A['Heating_kWhth'] * F['Heating']) / 1000
        
    elif category == 'Cooling (A/C)':
        # Formula: (Cooling_kWh * 0.42) / 1000
        return (A['Cooling_kWh'] * F['Cooling']) / 1000
        
    elif category == 'Computing (IT)':
        # Formula: (Computing_kWh * 0.42) / 1000
        return (A['Computing_kWh'] * F['Computing']) / 1000
        
    elif category == 'Subcontractors':
        # Formula: Sub1 + Sub2 + Sub3 (Enter directly in tons CO₂e)
        return sum(A['Subcontractors_tCO2e'])

    return 0.0

def get_full_emission_dataframe(activity_data, adjustments):
    """Calculates emissions for all categories and returns a structured DataFrame."""
    
    categories = [
        'Cars', 'Trucks', 'Buses', 'Forklifts', 'Cargo Planes', 
        'Office Lighting', 'Heating', 'Cooling (A/C)', 'Computing (IT)', 'Subcontractors'
    ]
    
    results = []
    for cat in categories:
        emissions = calculate_category_emissions(cat, activity_data, adjustments)
        
        # Get the input value for display purposes
        input_value = ''
        if cat == 'Cars': input_value = activity_data['Cars_km']
        elif cat == 'Trucks': input_value = activity_data['Trucks_km']
        elif cat == 'Buses': input_value = activity_data['Buses_km']
        elif cat == 'Forklifts': input_value = activity_data['Forklifts_hr']
        elif cat == 'Cargo Planes': input_value = activity_data['Planes_hr']
        elif cat == 'Office Lighting': input_value = activity_data['Lighting_kWh']
        elif cat == 'Heating': input_value = activity_data['Heating_kWhth']
        elif cat == 'Cooling (A/C)': input_value = activity_data['Cooling_kWh']
        elif cat == 'Computing (IT)': input_value = activity_data['Computing_kWh']
        elif cat == 'Subcontractors': input_value = sum(activity_data['Subcontractors_tCO2e']) # Total tCO2e
            
        results.append({
            'Category': cat,
            'Activity Data': input_value,
            'Emissions (tCO2e)': emissions
        })
        
    return pd.DataFrame(results)

# --- Streamlit UI Components ---

# State initialization
if 'activity_data' not in st.session_state:
    st.session_state['activity_data'] = DEFAULT_ACTIVITY_DATA.copy()
if 'adj_ev_share' not in st.session_state:
    st.session_state['adj_ev_share'] = 30
if 'adj_km_red' not in st.session_state:
    st.session_state['adj_km_red'] = 10
if 'adj_load_factor' not in st.session_state:
    st.session_state['adj_load_factor'] = 80
if 'Cars_km' not in st.session_state:
    st.session_state['Cars_km'] = DEFAULT_ACTIVITY_DATA['Cars_km']

def load_sample_data():
    st.session_state['activity_data'] = DEFAULT_ACTIVITY_DATA.copy()
    st.session_state['adj_ev_share'] = 30
    st.session_state['adj_km_red'] = 10
    st.session_state['adj_load_factor'] = 80

def reset_data():
    # Set activity data back to 0 or initial values
    st.session_state['activity_data'] = {k: 0 for k in DEFAULT_ACTIVITY_DATA if k != 'Subcontractors_tCO2e'}
    st.session_state['activity_data']['Subcontractors_tCO2e'] = [0, 0, 0]
    st.session_state['adj_ev_share'] = 0
    st.session_state['adj_km_red'] = 0
    st.session_state['adj_load_factor'] = 100 # Reset load factor to 100%


# Title / description measurements (customize these values)
TITLE_FONT_FAMILY = "Inter, Century Gothic, Century Gothic"
TITLE_FONT_SIZE_PX = 102
TITLE_FONT_WEIGHT = 1000
DESCRIPTION_FONT_SIZE_PX = 16
DESCRIPTION_MAX_WIDTH_PX = 900

LOGO_PATH = "assets/logo.png"
LOGO_URL = None
LOGO_WIDTH = 160

if LOGO_URL:
    st.image(LOGO_URL, width=LOGO_WIDTH)
else:
    try:
        st.image(LOGO_PATH, width=LOGO_WIDTH)
    except Exception:
        pass

# Centered title and adjustable description
st.markdown(f"""
<div style="text-align:center; font-family:{TITLE_FONT_FAMILY};">
  <div style="font-size:{TITLE_FONT_SIZE_PX}px; font-weight:{TITLE_FONT_WEIGHT}; color:#1f77b4; line-height:1;">
    emiMeter
  </div>
  </div>
  </div>
  </div>
  </div>
  <div style="font-size:{DESCRIPTION_FONT_SIZE_PX}px; color:#FFFFFF; margin-top:32px; max-width:{DESCRIPTION_MAX_WIDTH_PX}px; margin-left:auto; margin-right:auto;">
    Monitor, calculate, and optimize your organization’s carbon emissions with the EmiMeter App. Input your logistics and energy data to visualize CO₂ impact across categories, compare baseline and optimized scenarios, and drive measurable sustainability improvements.
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- Top Control Bar ---
st.caption("AWARE LOGISTICS CARBON MANAGEMENT")
col_load, col_reset, col_calc = st.columns([1, 1, 4])
with col_load:
    st.button("Load Sample Data", on_click=load_sample_data)
with col_reset:
    st.button("Reset", on_click=reset_data)
with col_calc:
    st.empty() # Placeholder to match screenshot layout

st.markdown("---")


# --- INPUTS AND ADJUSTMENTS COLUMN ---
input_col, chart_col = st.columns([1.5, 3])

with input_col:
    st.subheader("INPUTS: ACTIVITY DATA")
    
    # --- Helper to manage input values (we use keys directly now) ---
    def get_input_value(key):
        # We need to explicitly read from the top-level session state created by the input widgets
        # If the input key exists, use it. Otherwise, use the initial value from DEFAULT_ACTIVITY_DATA.
        # This allows us to use simple keys like 'Cars_km' in the widget.
        if key in st.session_state:
            return st.session_state[key]
        return st.session_state['activity_data'].get(key, DEFAULT_ACTIVITY_DATA.get(key, 0))

    # --- INPUT WIDGETS ---

    # Car, Truck, Bus, Forklift Inputs
    st.markdown("Cars - distance (km/year)")
    st.number_input(
        "Cars_km_input", 
        value=st.session_state['activity_data']['Cars_km'],
        min_value=0,
        label_visibility="collapsed",
        key="Cars_km" # This key is now simple and directly accessible
    )

    st.markdown("Trucks - distance (km/year)")
    st.number_input(
        "Trucks_km_input", 
        value=st.session_state['activity_data']['Trucks_km'],
        min_value=0,
        label_visibility="collapsed",
        key="Trucks_km"
    )

    st.markdown("Buses - distance (km/year)")
    st.number_input(
        "Buses_km_input", 
        value=st.session_state['activity_data']['Buses_km'],
        min_value=0,
        label_visibility="collapsed",
        key="Buses_km"
    )

    st.markdown("Forklifts - operating time (hours/year)")
    st.number_input(
        "Forklifts_hr_input", 
        value=st.session_state['activity_data']['Forklifts_hr'],
        min_value=0,
        label_visibility="collapsed",
        key="Forklifts_hr"
    )

    # Planes, Lighting, Heating, Cooling, Computing Inputs
    st.markdown("Cargo Planes - flight time (hours/year)")
    st.number_input(
        "Planes_hr_input", 
        value=st.session_state['activity_data']['Planes_hr'],
        min_value=0,
        label_visibility="collapsed",
        key="Planes_hr"
    )
    
    st.markdown("Office Lighting - electricity (kWh/year)")
    st.number_input(
        "Lighting_kWh_input", 
        value=st.session_state['activity_data']['Lighting_kWh'],
        min_value=0,
        label_visibility="collapsed",
        key="Lighting_kWh"
    )

    st.markdown("Heating - thermal energy (kWh-th/year)")
    st.number_input(
        "Heating_kWhth_input", 
        value=st.session_state['activity_data']['Heating_kWhth'],
        min_value=0,
        label_visibility="collapsed",
        key="Heating_kWhth"
    )

    st.markdown("Cooling (A/C) - electricity (kWh/year)")
    st.number_input(
        "Cooling_kWh_input", 
        value=st.session_state['activity_data']['Cooling_kWh'],
        min_value=0,
        label_visibility="collapsed",
        key="Cooling_kWh"
    )
    
    st.markdown("Computing (IT) - electricity (kWh/year)")
    st.number_input(
        "Computing_kWh_input", 
        value=st.session_state['activity_data']['Computing_kWh'],
        min_value=0,
        label_visibility="collapsed",
        key="Computing_kWh"
    )
    
    # Subcontractors Inputs (requires on_change to update the list)
    st.markdown("Subcontractors - tons CO₂e / year (Sub1, Sub2, Sub3)")
    sub_col1, sub_col2, sub_col3 = st.columns(3)
    
    def update_sub_data(index):
        # Callback updates the list directly from the widget keys
        st.session_state['activity_data']['Subcontractors_tCO2e'][index] = st.session_state[f"Sub{index+1}_key"]
        
    with sub_col1:
        st.number_input("Sub1", value=st.session_state['activity_data']['Subcontractors_tCO2e'][0], min_value=0, label_visibility="collapsed", key="Sub1_key", on_change=update_sub_data, args=(0,))
    with sub_col2:
        st.number_input("Sub2", value=st.session_state['activity_data']['Subcontractors_tCO2e'][1], min_value=0, label_visibility="collapsed", key="Sub2_key", on_change=update_sub_data, args=(1,))
    with sub_col3:
        st.number_input("Sub3", value=st.session_state['activity_data']['Subcontractors_tCO2e'][2], min_value=0, label_visibility="collapsed", key="Sub3_key", on_change=update_sub_data, args=(2,))
        
    st.markdown("---")
    st.subheader("ADJUSTMENTS: SLIDERS")

    # Define optimization sliders (these only affect the 'Optimized' calculation)
    # The current slider values are stored in session state via keys adj_ev_share, etc.
    st.slider("EV Share for Cars (%)", 0, 100, key='adj_ev_share', label_visibility="visible")
    st.slider("KM Reduction for Cars (%)", 0, 100, key='adj_km_red', label_visibility="visible")
    st.slider("Plane Load Factor (%)", 0, 100, key='adj_load_factor', label_visibility="visible")


# --- DYNAMICALLY UPDATE ACTIVITY DATA FOR CALCULATIONS ---
# Create a fresh, combined dictionary using the latest values from the input widgets (which are stored in session_state)
current_activity_data = {
    'Cars_km': st.session_state.Cars_km,
    'Trucks_km': st.session_state.Trucks_km,
    'Buses_km': st.session_state.Buses_km,
    'Forklifts_hr': st.session_state.Forklifts_hr,
    'Planes_hr': st.session_state.Planes_hr,
    'Lighting_kWh': st.session_state.Lighting_kWh,
    'Heating_kWhth': st.session_state.Heating_kWhth,
    'Cooling_kWh': st.session_state.Cooling_kWh,
    'Computing_kWh': st.session_state.Computing_kWh,
    'Subcontractors_tCO2e': st.session_state['activity_data']['Subcontractors_tCO2e'] # This is updated via callback
}


# --- CALCULATIONS ---

# 1. Baseline Calculation (No adjustments applied, Load Factor defaults to 100)
baseline_adjustments = {
    'EV_Share': 0,
    'KM_Reduction': 0,
    'Load_Factor': 100
}
df_baseline = get_full_emission_dataframe(current_activity_data, baseline_adjustments)
total_baseline_co2 = df_baseline['Emissions (tCO2e)'].sum()

# 2. Optimized Calculation (Sliders applied)
optimized_adjustments = {
    'EV_Share': st.session_state['adj_ev_share'],
    'KM_Reduction': st.session_state['adj_km_red'],
    'Load_Factor': st.session_state['adj_load_factor']
}
df_optimized = get_full_emission_dataframe(current_activity_data, optimized_adjustments)
total_optimized_co2 = df_optimized['Emissions (tCO2e)'].sum()


# --- CHARTS AND VISUALIZATION COLUMN ---
with chart_col:
    # 1. Pie Chart (Emission Share by Category - Optimized)
    st.subheader("Emission Share by Category (Pie - Optimized)")
    
    # Filter out categories with zero emissions for a cleaner pie chart
    df_pie = df_optimized[df_optimized['Emissions (tCO2e)'] > 0.001].copy()
    
    if not df_pie.empty:
        # Use 'viridis' or 'plasma' for a visually distinct, dark-mode friendly palette
        fig_pie = px.pie(
            df_pie,
            values='Emissions (tCO2e)',
            names='Category',
            hole=0.4,
            height=450,
            color_discrete_sequence=px.colors.qualitative.Plotly
        )
        fig_pie.update_traces(
            textposition='inside', 
            textinfo='percent', 
            marker=dict(line=dict(color='#000000', width=1))
        )
        fig_pie.update_layout(showlegend=True, margin=dict(t=50, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No activity data entered to generate the pie chart.")


    # 2. Bar Chart (Total Emissions - Baseline vs Optimized)
    st.subheader("Total Emissions (tons CO₂e) — Baseline vs Optimized")

    df_bar = pd.DataFrame({
        'Scenario': ['Baseline', 'Optimized'],
        'Emissions': [total_baseline_co2, total_optimized_co2]
    })
    
    fig_bar = px.bar(
        df_bar,
        x='Scenario',
        y='Emissions',
        color='Scenario',
        text='Emissions',
        height=450,
        color_discrete_map={'Baseline': '#1f77b4', 'Optimized': '#1f77b4'} # Use the same color for the primary bar style
    )
    fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig_bar.update_layout(
        yaxis_title="Emissions (tons CO₂e)",
        xaxis_title="",
        showlegend=False,
        margin=dict(t=50, b=50, l=0, r=0)
    )
    st.plotly_chart(fig_bar, use_container_width=True)


# --- TOTALS AND ASSUMPTIONS FOOTER ---
footer_col1, footer_col2, footer_col3 = st.columns([1.5, 1, 3])

with footer_col1:
    st.markdown("---")
    # Display the totals exactly as seen in the screenshots
    st.markdown(f"""
    <div style="font-size: 24px; font-weight: bold; color: #1f77b4; padding: 10px 0;">
        {total_baseline_co2:,.2f}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="font-size: 24px; font-weight: bold; color: #1f77b4; padding: 10px 0;">
        {total_optimized_co2:,.2f}
    </div>
    """, unsafe_allow_html=True)

with footer_col2:
    st.markdown("---")
    st.markdown(" ") # Spacer
    st.markdown(" ") # Spacer
    
with footer_col3:
    st.markdown("---")
    st.subheader("Assumptions")
    st.caption("""
    - The Car EV Share adjustment assumes an aggressive 70% reduction factor for the portion of the fleet that is electric, as per the formula: `(1 - 0.7 * EV/100)`.
    - Baseline values for adjustable factors are 100% Load Factor (Planes) and 0% for EV Share/KM Reduction (Cars).
    - All emission factors and formulas are strictly derived from the provided competition problem table.
    - Tons CO₂e is calculated as $\\frac{kg~CO_{2}e}{1000}$.
    """)
