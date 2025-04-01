# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
import plotly.graph_objects as go
from math import sqrt, ceil
from scipy.stats import norm

# --- Session State Initialization ---
# Stores results of calculations to persist across interactions and tabs
if 'rental_costs_calculated' not in st.session_state:
    st.session_state.rental_costs_calculated = False
    st.session_state.total_rental_cost = 0.0
    st.session_state.rental_details_df = pd.DataFrame()

if 'inventory_costs_calculated' not in st.session_state:
    st.session_state.inventory_costs_calculated = False
    st.session_state.total_inventory_financing_cost = 0.0
    st.session_state.inventory_details_df = pd.DataFrame()
    st.session_state.aggregated_inventory_metrics = {}

if 'shipping_costs_calculated' not in st.session_state:
    st.session_state.shipping_costs_calculated = False
    st.session_state.total_shipping_cost = 0.0
    st.session_state.shipping_details_df = pd.DataFrame()

if 'labor_costs_calculated' not in st.session_state:
    st.session_state.labor_costs_calculated = False
    st.session_state.total_labor_cost = 0.0
    st.session_state.labor_details_df = pd.DataFrame()

if 'grand_total' not in st.session_state:
    st.session_state.grand_total = 0.0

# Flag to check overall setup validity, used across tabs
if 'config_complete' not in st.session_state:
    st.session_state.config_complete = False


# -----------------------------------------------------
# Page Configuration and Custom CSS
# -----------------------------------------------------
st.set_page_config(
    page_title="Supply Chain Optimization Dashboard",
    page_icon="🚚", # Standard emoji icon for browser tab
    layout="wide"
)

# Inject Font Awesome (for icons) and custom CSS styles
st.markdown(
    """
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
    </head>
    <style>
        /* Import Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

        /* Base font setting */
        html, body, [class*="css"] {
            font-family: 'Roboto', sans-serif;
        }

        /* Main Title */
        .main-header-font {
            font-size: 36px !important;
            font-weight: 700;
            color: #1E3A5F; /* Darker blue */
            text-align: center;
            margin-bottom: 30px;
            padding-top: 20px;
        }

        /* Section Headers (e.g., Define Your Network Parameters) */
        .section-header-font {
            font-size: 26px !important;
            font-weight: 700;
            color: #2C3E50; /* Dark Slate Gray */
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498DB; /* Blue underline */
            padding-bottom: 5px;
        }

        /* Sub-section Headers (e.g., Brand Pricing, Rental Parameters) */
        .sub-header-font {
            font-size: 20px !important;
            font-weight: 500;
            color: #34495E; /* Wet Asphalt */
            margin-top: 15px;
            margin-bottom: 10px;
        }

        /* Card styling for input groups */
        .input-card { /* Applied via st.container(border=True) */
            background-color: #FFFFFF;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border: 1px solid #EAECEE; /* Light border */
        }

        /* Expander Styling (for Market Areas, Warehouses) */
        .stExpander {
            border: 1px solid #EAECEE !important;
            border-radius: 8px !important;
            margin-bottom: 15px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stExpander header { /* Expander Title Bar */
            font-weight: 500;
            font-size: 18px;
            background-color: #F8F9F9; /* Light background */
            border-radius: 8px 8px 0 0 !important;
            padding: 10px 15px !important;
        }
        .stExpander header:hover {
             background-color: #E8F6F3; /* Light green on hover */
        }

        /* Metric Card Styling (for Summary tab) */
        .metric-card {
            background-color: #FFFFFF;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
            border: 1px solid #EAECEE;
            height: 100px; /* Ensure cards have same height */
            display: flex; /* Use flexbox for alignment */
            flex-direction: column;
            justify-content: center;
        }
        .metric-card .stMetric { /* Target Streamlit Metric component inside */
             background-color: transparent !important;
             border: none !important;
             padding: 0 !important;
             text-align: center; /* Center align metric text */
        }
        .metric-card label { /* Metric Label (e.g., "Rental Cost") */
            font-weight: 500;
            color: #566573; /* Grayish blue */
            font-size: 14px; /* Slightly smaller label */
        }
         .metric-card p { /* Metric Value (e.g., "$100,000") */
            font-size: 24px !important;
            font-weight: 700;
            color: #1A5276; /* Stronger blue */
        }

         /* Tab Styling */
        .stTabs [data-baseweb="tab-list"] {
                gap: 24px; /* Space between tabs */
        }
        .stTabs [data-baseweb="tab"] { /* Individual tab style */
            height: 50px;
            white-space: pre-wrap;
            background-color: #F0F2F6; /* Default background */
            border-radius: 8px 8px 0px 0px;
            gap: 1px;
            padding: 10px 15px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] { /* Selected tab style */
            background-color: #FFFFFF;
            color: #3498DB; /* Blue text */
            font-weight: 700;
            border-bottom: 3px solid #3498DB; /* Blue underline */
        }

        /* Button Styling */
        .stButton>button {
            background-color: #3498DB; /* Primary Blue */
            color: white;
            padding: 10px 20px;
            border-radius: 5px;
            border: none;
            font-weight: 500;
            transition: background-color 0.3s ease;
            width: 100%; /* Make buttons fill container width */
        }
        .stButton>button:hover {
            background-color: #2874A6; /* Darker Blue */
            color: white;
        }
         .stButton>button:focus { /* Accessibility focus style */
             box-shadow: 0 0 0 2px #AED6F1 !important;
             background-color: #2E86C1;
             color: white;
         }

        /* Icon styling */
        .icon {
            margin-right: 8px;
            color: #5D6D7E; /* Slightly muted icon color */
        }

        /* Style for markdown labels used above widgets */
        .widget-label {
            font-weight: 500;
            margin-bottom: -5px; /* Reduce space between label and widget */
            color: #34495E; /* Match sub-header color */
            font-size: 14px; /* Standard widget label size */
            padding-left: 2px; /* Slight indent */
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Main Application Header ---
st.markdown("<p class='main-header-font'><i class='fas fa-cogs icon'></i>Supply Chain & Warehouse Network Optimization</p>", unsafe_allow_html=True)

# -----------------------------------------------------
# Sidebar: Global Parameters
# -----------------------------------------------------
with st.sidebar:
    st.markdown("## <i class='fas fa-globe icon'></i> Global Settings", unsafe_allow_html=True)
    st.divider()

    # Interest Rate Input
    st.markdown("<p class='widget-label'><i class='fas fa-percentage icon'></i> Actual Interest Rate (%)</p>", unsafe_allow_html=True)
    interest_rate = st.number_input(
        label="", # Use markdown above for label
        min_value=0.0, max_value=100.0, value=5.0, step=0.1,
        help="Enter the annual interest rate used for inventory financing calculations.",
        label_visibility="collapsed" # Hide default label space
    )

    # Service Level Input
    st.markdown("<p class='widget-label'><i class='fas fa-shield-alt icon'></i> Required Service Level (0-1)</p>", unsafe_allow_html=True)
    service_level = st.slider(
        label="", # Use markdown above for label
        min_value=0.0, max_value=1.0, value=0.95,
        help="Set the desired probability of not stocking out (used for safety stock calculation). Higher value means more safety stock.",
        label_visibility="collapsed" # Hide default label space
    )

    st.divider()

    # Layout Type Input
    st.markdown("<p class='widget-label'><i class='fas fa-warehouse icon'></i> Layout Type</p>", unsafe_allow_html=True)
    layout_type = st.radio(
        label="", # Use markdown above for label
        options=["Central and Fronts", "Main Regionals"],
        help="Select the overall warehouse network structure.",
        key="layout_type_radio",
        horizontal=True,
        label_visibility="collapsed" # Hide default label space
    )
    # Display info message based on layout type
    if layout_type == "Main Regionals":
        st.info("ℹ️ With 'Main Regionals', all defined warehouses will function as MAIN type, receiving stock directly from the source and serving their assigned markets.")
    else:
         st.info("ℹ️ With 'Central and Fronts', define one MAIN warehouse as the central hub and potentially multiple FRONT warehouses supplied by the MAIN hub.")

    st.divider()

    # Container Capacity Input
    st.markdown("### <i class='fas fa-box-open icon'></i> Container Capacity", unsafe_allow_html=True)
    container_capacity_40 = st.number_input(
        "Capacity for 40ft HC (Units)", # Simple label is okay here
        min_value=1, value=600, step=1, format="%d",
        help="Define the typical number of saleable units (e.g., 4-panel sets) that fit into a standard 40ft High Cube container."
    )

# -----------------------------------------------------
# Z-Value Calculation (based on Service Level)
# -----------------------------------------------------
if service_level >= 1.0:
    Z_value = 5 # Use a high Z-score for near 100%
elif service_level <= 0.0:
    Z_value = -5 # Use a low Z-score for 0%
else:
    Z_value = norm.ppf(service_level) # Calculate Z-score for intermediate levels

# -----------------------------------------------------
# Main Application Tabs
# -----------------------------------------------------
# Use simple text labels for tabs as HTML rendering is unreliable here
tab_setup, tab_calculations, tab_summary = st.tabs([
    "Setup Configuration",
    "Run Calculations",
    "Results Summary"
])

# =====================================================
# TAB 1: Setup Configuration
# =====================================================
with tab_setup:
    st.markdown("<p class='section-header-font'><i class='fas fa-edit icon'></i>Define Your Network Parameters</p>", unsafe_allow_html=True)

    # --- Brand Pricing & Rental Parameters ---
    col_setup_1, col_setup_2 = st.columns(2)
    with col_setup_1:
        # Brand Pricing Card
        with st.container(border=True):
             st.markdown("<p class='sub-header-font'><i class='fas fa-tags icon'></i>Brand Pricing</p>", unsafe_allow_html=True)
             BRANDS = ["Heliocol", "SunStar", "SunValue"] # Global list of all possible brands
             brand_unit_prices = {}
             brand_cols = st.columns(len(BRANDS))
             for idx, brand in enumerate(BRANDS):
                 with brand_cols[idx]:
                     brand_unit_prices[brand] = st.number_input(
                         f"Unit Price ({brand})",
                         min_value=0.01, value=80.0, step=1.0, # Min price > 0
                         help=f"Enter the inventory valuation price (per unit, e.g., 4 panels in $) for {brand}.",
                         key=f"{brand}_unit_price"
                    )
    with col_setup_2:
         # Rental Parameters Card
         with st.container(border=True):
            st.markdown("<p class='sub-header-font'><i class='fas fa-ruler-combined icon'></i>Rental Parameters</p>", unsafe_allow_html=True)
            rent_cols = st.columns(3)
            with rent_cols[0]:
                sq_ft_per_unit = st.number_input(
                    "Sq Ft per Unit",
                    min_value=0.1, value=0.8, step=0.1, format="%.1f",
                    help="Square feet required to store one unit (e.g., 4 panels)."
                )
            with rent_cols[1]:
                overhead_factor_main = st.number_input(
                    "Overhead (MAIN)", min_value=1.0, value=1.2, step=0.1, format="%.1f",
                    help="Space multiplication factor for MAIN warehouses (aisles, offices, etc.). E.g., 1.2 means 20% overhead space."
                )
            with rent_cols[2]:
                 overhead_factor_front = st.number_input(
                    "Overhead (FRONT)", min_value=1.0, value=1.5, step=0.1, format="%.1f",
                    help="Space multiplication factor for FRONT warehouses."
                )

    # --- Market Areas Setup ---
    st.markdown("<p class='section-header-font'><i class='fas fa-map-marker-alt icon'></i>Market Areas Setup</p>", unsafe_allow_html=True)
    with st.container(border=True):
        # Define base and custom market areas
        base_market_areas = ["FL", "CA_SOUTH", "CA_NORTH", "TX", "NJ"]
        st.write("Standard market areas:", ", ".join(base_market_areas))
        custom_market_areas_str = st.text_input(
            "Enter additional market areas (comma separated)", value="",
            help="Define extra market regions if needed. E.g., NY, PA, OH"
        )
        custom_market_areas = [area.strip().upper() for area in custom_market_areas_str.split(",") if area.strip()]
        all_market_areas = sorted(list(dict.fromkeys(base_market_areas + custom_market_areas)))

        # Select market areas to include in this scenario
        selected_market_areas = st.multiselect(
            "Select Market Areas to Include", options=all_market_areas, default=all_market_areas,
            help="Choose which defined market areas to actively use in the calculations."
        )

        market_area_data = {} # Main dictionary to store data for selected brands in each area
        if not selected_market_areas:
            st.warning("Please select at least one market area.")
        else:
            st.markdown("<p class='sub-header-font'>Configure Parameters for Selected Market Areas:</p>", unsafe_allow_html=True)
            # Loop through each selected market area
            for area in selected_market_areas:
                 # Use an expander for each market area's inputs
                 with st.expander(f"Parameters for Market Area: {area}", expanded=False):

                    # --- Brand Selection for this Market Area ---
                    selected_brands_in_area = st.multiselect(
                        label=f"Select Active Brands in {area}",
                        options=BRANDS, default=BRANDS, # Default to all brands
                        key=f"{area}_active_brands",
                        help=f"Choose which brands are sold/relevant in the {area} market."
                    )

                    brand_data_for_area = {} # Temp dict for this area's brand data
                    if not selected_brands_in_area:
                        st.warning(f"No brands selected for {area}. Demand will be zero.")
                    else:
                        # Loop ONLY through the brands selected for this specific area
                        for brand in selected_brands_in_area:
                            st.markdown(f"<b><i class='fas fa-tag icon'></i>Parameters for Brand: {brand}</b>", unsafe_allow_html=True)
                            col1, col2, col3 = st.columns(3)
                            # Input fields for the selected brand
                            with col1:
                                avg_order_size = st.number_input(f"Avg Order Size", min_value=0, value=100, step=1, format="%d", key=f"{area}_{brand}_avg_order_size", help=f"Typical order size for {brand} in {area}.")
                            with col2:
                                avg_daily_demand = st.number_input(f"Avg Daily Demand", min_value=0, value=50, step=1, format="%d", key=f"{area}_{brand}_avg_daily_demand", help=f"Average daily sales/usage for {brand} in {area}.")
                            with col3:
                                std_daily_demand = st.number_input(f"Std Dev Daily Demand", min_value=0.0, value=10.0, step=1.0, key=f"{area}_{brand}_std_daily_demand", help=f"Volatility of daily demand for {brand} in {area}.")

                            # 12-Month Forecast Input
                            st.markdown(f"<b>12-Month Forecast Demand ({brand} - {area})</b>", unsafe_allow_html=True)
                            forecast = []
                            forecast_cols = st.columns(6) # Display 6 months per row
                            months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                            for m in range(12):
                                with forecast_cols[m % 6]:
                                    val = st.number_input(f"{months[m]}", min_value=0, value=500, step=10, format="%d", key=f"{area}_{brand}_forecast_{m}", help=f"Forecast demand for {brand} in {area} for month {m+1}.")
                                    forecast.append(val)
                            st.divider() # Separator between brands

                            # Store data for the selected brand
                            brand_data_for_area[brand] = {
                                "avg_order_size": avg_order_size,
                                "avg_daily_demand": avg_daily_demand,
                                "std_daily_demand": std_daily_demand,
                                "forecast_demand": forecast
                            }
                    # Assign the collected data (only for selected brands) to the main dictionary
                    market_area_data[area] = brand_data_for_area

    # --- Warehouse Setup ---
    st.markdown("<p class='section-header-font'><i class='fas fa-industry icon'></i>Warehouse Setup</p>", unsafe_allow_html=True)
    with st.container(border=True):
        # Define base and custom warehouse locations
        base_warehouse_locations = ["FL", "CA_SOUTH", "CA_NORTH", "TX", "NJ"]
        st.write("Standard potential warehouse locations:", ", ".join(base_warehouse_locations))
        custom_warehouse_locations_str = st.text_input(
            "Enter additional potential warehouse locations (comma separated)", value="", key="warehouse_locations_text",
            help="Define extra potential locations for warehouses. E.g., NY, PA"
        )
        custom_warehouse_locations = [loc.strip().upper() for loc in custom_warehouse_locations_str.split(",") if loc.strip()]
        all_warehouse_locations = sorted(list(dict.fromkeys(base_warehouse_locations + custom_warehouse_locations)))

        # Number of warehouses to configure
        num_warehouses = st.number_input(
            "Number of Warehouses to Configure", min_value=1, value=1, step=1,
            help="Enter the total number of warehouses in this scenario."
        )

        warehouse_data = [] # Final list to hold validated warehouse configs
        temp_warehouse_configs = {} # Temp storage during configuration loop
        st.session_state.config_complete = True # Assume valid initially, set to False on error

        st.markdown("<p class='sub-header-font'>Configure Parameters for Each Warehouse:</p>", unsafe_allow_html=True)
        # Loop to configure each warehouse
        for i in range(int(num_warehouses)):
             with st.expander(f"Warehouse {i+1} Configuration", expanded=True if num_warehouses <= 2 else False):
                wh_config = {} # Store config for this warehouse
                col_loc, col_type = st.columns(2)

                # Warehouse Location
                with col_loc:
                    location = st.selectbox(
                        f"Location (WH {i+1})", options=[""] + all_warehouse_locations, index=0, # Default empty
                        key=f"wh_location_{i}", help="Choose a location for this warehouse."
                    )
                    wh_config["location"] = location if location else None

                # Warehouse Type (depends on global layout setting)
                with col_type:
                    if layout_type == "Main Regionals":
                        wh_type = "MAIN" # Force MAIN type
                        st.text_input(f"Type (WH {i+1})", value="MAIN (Regional Layout)", disabled=True)
                    else: # Central and Fronts layout
                        options = ["MAIN", "FRONT"]
                        # Check if a MAIN warehouse already exists in this config session
                        has_main_already = any(w.get("type") == "MAIN" for w in temp_warehouse_configs.values())
                        if has_main_already: options = ["FRONT"] # Only allow FRONT if MAIN exists
                        if not options: # Should not happen if num_warehouses > 0
                             st.error("Configuration error: Cannot add more warehouses.") ; wh_type = None
                        else:
                             wh_type = st.radio(
                                f"Type (WH {i+1})", options=options, key=f"wh_type_{i}", horizontal=True,
                                help="MAIN = Central Hub, FRONT = Spoke Warehouse."
                            )
                    wh_config["type"] = wh_type

                # Markets Served by this Warehouse
                served_markets = st.multiselect(
                    f"Market Areas Served by Warehouse {i+1}", options=selected_market_areas, key=f"wh_markets_{i}",
                    help="Select all market areas this warehouse directly serves."
                )
                wh_config["served_markets"] = served_markets
                # Validation: Location must be within served markets
                if location and location not in served_markets:
                    st.error(f"❗ Warehouse {i+1} location '{location}' must be included in its served markets!")
                    st.session_state.config_complete = False

                st.markdown("---") # Divider

                # Rent Configuration
                col_rent_method, col_rent_price = st.columns(2)
                with col_rent_method:
                    rent_pricing_method = st.radio(
                        f"Rent Pricing Method (WH {i+1})", options=["Fixed Rent Price", "Square Foot Rent Price"],
                        key=f"rent_method_{i}", horizontal=True, help="Choose how rent is calculated."
                    )
                with col_rent_price:
                    if rent_pricing_method == "Fixed Rent Price":
                        rent_price = st.number_input(
                            f"Fixed Rent Price (WH {i+1}) ($/year)", min_value=0.0, value=50000.0, step=1000.0, format="%.0f",
                            key=f"fixed_rent_{i}"
                        )
                    else: # Square Foot Rent Price
                        rent_price = st.number_input(
                            f"Rent Price per Sq Ft (WH {i+1}) ($/year)", min_value=0.01, value=10.0, step=0.5, format="%.2f", # Min > 0
                            key=f"sqft_rent_{i}"
                        )
                wh_config["rent_pricing_method"] = rent_pricing_method
                wh_config["rent_price"] = rent_price

                st.markdown("---") # Divider

                # Labor Configuration
                col_emp_sal, col_emp_num = st.columns(2)
                with col_emp_sal:
                    avg_employee_salary = st.number_input(
                        f"Avg Annual Salary/Employee (WH {i+1}) ($)", min_value=0, value=50000, step=1000, format="%d",
                        key=f"employee_salary_{i}"
                    )
                with col_emp_num:
                     # Suggest default employee count based on type/markets
                     default_emp = 0
                     if wh_type == "MAIN": default_emp = 3 if len(served_markets) <= 1 else 4
                     elif wh_type == "FRONT": default_emp = 2
                     num_employees = st.number_input(
                        f"Number of Employees (WH {i+1})", min_value=0, value=default_emp, step=1,
                        key=f"num_employees_{i}"
                    )
                wh_config["avg_employee_salary"] = avg_employee_salary
                wh_config["num_employees"] = num_employees

                # --- Shipping Inputs (Conditional on Warehouse Type) ---
                if wh_type == "MAIN":
                     # International Shipping from Source to MAIN WH
                     st.markdown("<p class='sub-header-font' style='margin-top: 15px; color: #1A5276;'><i class='fas fa-ship icon'></i>International Shipping (to WH {i+1})</p>", unsafe_allow_html=True)
                     ship_col1, ship_col2 = st.columns(2)
                     with ship_col1:
                         lt_shipping = st.number_input(
                            "Lead Time (Source to WH, days)", min_value=0, value=30, step=1, format="%d",
                            key=f"lt_shipping_{i}", help="Average transit time from source (e.g., Israel) to this warehouse."
                        )
                     with ship_col2:
                         shipping_cost_40hc = st.number_input(
                            "Shipping Cost (per 40HC, $)", min_value=0.0, value=5000.0, step=100.0, format="%.0f",
                            key=f"shipping_cost_40hc_{i}", help="Cost to ship one 40ft container from source to this warehouse."
                        )
                     wh_config["lt_shipping"] = lt_shipping
                     wh_config["shipping_cost_40hc"] = shipping_cost_40hc

                     # Regional Land Shipping (Only for Main Regionals layout serving multiple areas)
                     if layout_type == "Main Regionals" and len(served_markets) > 1 and location:
                         st.markdown(f"<p class='sub-header-font' style='margin-top: 10px; color: #1A5276;'><i class='fas fa-truck icon'></i>Regional Land Shipping (from WH {i+1})</p>", unsafe_allow_html=True)
                         land_shipping_data = {}
                         other_markets = [m for m in served_markets if m != location] # Markets other than the WH location itself
                         for add_area in other_markets:
                             land_cols = st.columns([2,3]) # Adjust column widths
                             with land_cols[0]:
                                 distance_val = st.number_input(
                                    f"Distance to {add_area} (miles)", min_value=0.0, value=100.0, step=10.0, format="%.1f",
                                    key=f"dist_{i}_{add_area}"
                                )
                             with land_cols[1]:
                                 # Calculate weighted avg order size for the destination area based on selected brands
                                 area_brands_data = market_area_data.get(add_area, {})
                                 area_total_demand = sum(params.get("avg_daily_demand", 0) for params in area_brands_data.values() if params.get("avg_daily_demand", 0) > 0)
                                 if area_total_demand > 0:
                                     area_avg_order = sum(params.get("avg_order_size", 0) * params.get("avg_daily_demand", 0) for params in area_brands_data.values()) / area_total_demand
                                 else: area_avg_order = 0

                                 cost_val = st.number_input(
                                    f"Cost per Avg Order ({area_avg_order:.0f} units) to {add_area} ($)", min_value=0.0, value=50.0, step=1.0, format="%.2f",
                                    key=f"cost_{i}_{add_area}", help=f"Land freight cost to ship an average order from {location} to {add_area}."
                                )
                                 if cost_val <= 0 and area_total_demand > 0: # Check cost > 0 if demand exists
                                     st.warning(f"❗ Enter a positive shipping cost for {add_area} if demand exists.")
                             land_shipping_data[add_area] = {
                                "distance": distance_val,
                                "cost_for_avg_order": cost_val,
                                "calculated_avg_order_size": area_avg_order # Store for calculation reference
                            }
                         wh_config["land_shipping_data"] = land_shipping_data

                elif wh_type == "FRONT":
                     # Transfer Shipping from MAIN to FRONT WH
                     st.markdown("<p class='sub-header-font' style='margin-top: 15px; color: #1A5276;'><i class='fas fa-exchange-alt icon'></i>Transfer Shipping (to WH {i+1})</p>", unsafe_allow_html=True)
                     # Find MAIN warehouses defined earlier in this loop
                     main_wh_options = {f"WH {idx+1} ({w_conf['location']})": w_conf for idx, w_conf in temp_warehouse_configs.items() if w_conf.get("type") == "MAIN"}

                     if not main_wh_options:
                         st.error("❗ Cannot configure FRONT: No MAIN warehouse defined yet. Define a MAIN warehouse first.")
                         wh_config["serving_central_wh_key"] = None
                         st.session_state.config_complete = False # Invalidate config
                     else:
                         serving_central_label = st.selectbox(
                            f"Select Serving MAIN Warehouse", options=list(main_wh_options.keys()),
                            key=f"serving_central_{i}", help="Choose the MAIN hub supplying this FRONT warehouse."
                        )
                         # Find the actual config dict using the selected label
                         serving_central_wh_config = main_wh_options[serving_central_label]
                         wh_config["serving_central_wh_key"] = serving_central_label # Store the label/key for reference

                         # Optional: Check if MAIN serves at least one common market (user awareness)
                         # main_wh_served = serving_central_wh_config.get("served_markets", [])
                         # common_markets = set(main_wh_served).intersection(set(served_markets))
                         # if not common_markets: st.warning(f"Selected MAIN warehouse doesn't serve common markets with this FRONT WH.")

                     # Costs for transferring stock (e.g., by truckload)
                     front_ship_col1, front_ship_col2 = st.columns(2)
                     with front_ship_col1:
                         front_shipping_cost_40 = st.number_input(
                            "Cost (per 40ft Truckload, $)", min_value=0.0, value=500.0, step=10.0, format="%.0f",
                            key=f"front_shipping_cost_40_{i}", help="Estimated cost for a 40ft truckload from MAIN."
                         )
                     with front_ship_col2:
                         front_shipping_cost_53 = st.number_input(
                            "Cost (per 53ft Truckload, $)", min_value=0.0, value=600.0, step=10.0, format="%.0f",
                            key=f"front_shipping_cost_53_{i}", help="Estimated cost for a 53ft truckload from MAIN."
                         )
                     wh_config["front_shipping_cost_40"] = front_shipping_cost_40
                     wh_config["front_shipping_cost_53"] = front_shipping_cost_53

                # Store the configuration for this warehouse temporarily
                temp_warehouse_configs[i] = wh_config

        # --- Final Processing & Validation after loop ---
        warehouse_data = list(temp_warehouse_configs.values()) # Convert temp dict to final list

        # Re-run validation checks on the complete configuration
        all_markets_served_final = set()

        # Check for exactly one MAIN warehouse if using Central/Fronts layout
        if layout_type == "Central and Fronts" and sum(1 for wh in warehouse_data if wh.get("type") == "MAIN") != 1:
             st.error("❌ Validation Error: In 'Central and Fronts' layout, exactly one MAIN warehouse must be defined.")
             st.session_state.config_complete = False

        # Check individual warehouse details
        for i, wh in enumerate(warehouse_data):
            if not wh.get("location"):
                st.error(f"❌ Validation Error: Location is missing for Warehouse {i+1}.")
                st.session_state.config_complete = False
            if not wh.get("served_markets"):
                st.error(f"❌ Validation Error: Served markets are missing for Warehouse {i+1} ({wh.get('location', 'N/A')}).")
                st.session_state.config_complete = False
            # Check FRONT warehouse assignment only if config hasn't already failed
            if st.session_state.config_complete and wh.get("type") == "FRONT" and not wh.get("serving_central_wh_key"):
                 st.error(f"❌ Validation Error: Serving MAIN warehouse not selected/available for FRONT WH {i+1}.")
                 st.session_state.config_complete = False
            # Aggregate all markets served by the configured warehouses
            all_markets_served_final.update(wh.get("served_markets", []))

        # Check if all selected market areas are covered
        unserved_markets = set(selected_market_areas) - all_markets_served_final
        if unserved_markets:
            st.error(f"❌ Validation Error: The following markets are selected but not served by any warehouse: {', '.join(sorted(list(unserved_markets)))}")
            st.session_state.config_complete = False

        # Display final status message
        if st.session_state.config_complete:
            st.success("✅ Setup configuration appears complete and valid.")
        else:
             st.warning("⚠️ Please review the errors above in the Warehouse Setup section before proceeding.")
             warehouse_data = [] # Clear data if invalid to prevent calculation errors


# =====================================================
# Helper Functions (Core Logic - Unchanged)
# =====================================================
# These functions now naturally operate on the potentially filtered market_area_data
# (i.e., only includes data for brands selected in each market area)

def compute_annual_forecast_for_area(area, market_data):
    """Calculates total annual forecast demand for a specific market area."""
    total = 0
    # Safely get data for the area, defaults to empty dict if area/brands not selected
    if area_data := market_data.get(area, {}):
        for brand, params in area_data.items():
            total += sum(params.get("forecast_demand", [0]))
    return total

def compute_max_monthly_forecast_for_area(area, market_data):
    """Calculates peak monthly forecast demand across selected brands for a market area."""
    max_m = 0
    if area_data := market_data.get(area, {}):
        if not area_data: return 0 # No brands selected for area

        forecast_lengths = [len(params.get("forecast_demand", [])) for params in area_data.values()]
        if all(length == 12 for length in forecast_lengths): # Check forecasts are complete
            for m in range(12):
                month_sum = sum(params["forecast_demand"][m] for params in area_data.values())
                max_m = max(max_m, month_sum)
        else: # Fallback if forecast data is somehow incomplete
             max_per_brand = [max(params.get("forecast_demand", [0])) for params in area_data.values()]
             max_m = sum(max_per_brand)
    return max_m

def compute_std_sum_for_area(area, market_data):
    """Calculates sum of standard deviations of daily demand for selected brands in an area."""
    total_std = 0
    if area_data := market_data.get(area, {}):
        for params in area_data.values():
            total_std += params.get("std_daily_demand", 0)
    return total_std

def compute_daily_demand_sum_for_area(area, market_data):
    """Calculates sum of average daily demand for selected brands in an area."""
    total = 0
    if area_data := market_data.get(area, {}):
        for params in area_data.values():
            total += params.get("avg_daily_demand", 0)
    return total

# --- Warehouse Level Helper Functions ---
def compute_max_monthly_forecast(warehouse, market_data):
    """Calculates peak monthly forecast across all markets served by a warehouse."""
    max_monthly = 0
    for area in warehouse.get("served_markets", []):
        area_max = compute_max_monthly_forecast_for_area(area, market_data)
        max_monthly = max(max_monthly, area_max)
    return max_monthly

def compute_daily_demand_sum(warehouse, market_data):
    """Calculates total average daily demand across all markets served by a warehouse."""
    total = 0
    for area in warehouse.get("served_markets", []):
        total += compute_daily_demand_sum_for_area(area, market_data)
    return total

def compute_annual_demand(warehouse, market_data):
    """Calculates total annual forecast demand across all markets served by a warehouse."""
    total = 0
    for area in warehouse.get("served_markets", []):
        total += compute_annual_forecast_for_area(area, market_data)
    return total

def compute_std_sum(warehouse, market_data):
    """Calculates total standard deviation across all markets served by a warehouse."""
    total = 0
    for area in warehouse.get("served_markets", []):
        total += compute_std_sum_for_area(area, market_data)
    return total

# --- Safety Stock and Inventory Breakdown ---
def compute_safety_stock_main(warehouse, market_data, Z_val, layout, all_warehouses):
    """Calculates safety stock for a MAIN warehouse."""
    std_sum = compute_std_sum(warehouse, market_data) # Uses filtered market data
    LT = warehouse.get("lt_shipping", 0)
    safety_stock_main = std_sum * sqrt(LT) * Z_val if LT > 0 else 0

    # Add demand during transfer lead time for FRONT warehouses it serves
    if layout == "Central and Fronts":
        try:
            warehouse_index = all_warehouses.index(warehouse)
            serving_label = f"WH {warehouse_index+1} ({warehouse.get('location')})"
            front_daily_demand = sum(
                compute_daily_demand_sum(front_wh, market_data) # Uses filtered market data
                for front_wh in all_warehouses
                if front_wh.get("type") == "FRONT" and front_wh.get("serving_central_wh_key") == serving_label
            )
            transfer_lead_time = 12 # Assumed transfer lead time
            safety_stock_main += transfer_lead_time * front_daily_demand
        except ValueError:
             st.error("Internal error: Cannot find MAIN warehouse in list (Safety Stock).")
    return safety_stock_main

def compute_inventory_breakdown(warehouse, market_data, interest_rt, brand_prices, Z_val, layout, all_warehouses):
    """Calculates inventory metrics (safety stock, avg inventory, financing cost) by brand for a MAIN warehouse."""
    LT = warehouse.get("lt_shipping", 0)
    # Initialize for ALL potential brands
    breakdown = {brand: {"annual_forecast": 0, "std_sum": 0, "avg_daily_demand": 0} for brand in BRANDS}

    # Aggregate from directly served markets (only selected brands contribute)
    for area in warehouse.get("served_markets", []):
        if area_data := market_data.get(area, {}):
            for brand, params in area_data.items():
                 if brand in breakdown: # Ensure it's a globally recognized brand
                     breakdown[brand]["annual_forecast"] += sum(params.get("forecast_demand", [0]))
                     breakdown[brand]["std_sum"] += params.get("std_daily_demand", 0)
                     breakdown[brand]["avg_daily_demand"] += params.get("avg_daily_demand", 0)

    # Add demand from served FRONT warehouses (only selected brands contribute)
    front_contrib = {brand: 0 for brand in BRANDS}
    if layout == "Central and Fronts":
         try:
             warehouse_index = all_warehouses.index(warehouse)
             serving_label = f"WH {warehouse_index+1} ({warehouse.get('location')})"
             for front_wh in all_warehouses:
                 if front_wh.get("type") == "FRONT" and front_wh.get("serving_central_wh_key") == serving_label:
                     for area in front_wh.get("served_markets", []):
                         if area_data := market_data.get(area, {}):
                             for brand, params in area_data.items():
                                  if brand in front_contrib:
                                      front_contrib[brand] += params.get("avg_daily_demand", 0)
         except ValueError:
            st.error("Internal error: Cannot find MAIN warehouse in list (Inventory Breakdown).")

    # Calculate final metrics for all global brands
    results = {}
    for brand in BRANDS:
        b_data = breakdown[brand]
        f_contrib = front_contrib[brand]
        transfer_lead_time = 12 # Assumed
        safety_stock = (b_data["std_sum"] * sqrt(LT) * Z_val if LT > 0 else 0) + (transfer_lead_time * f_contrib)
        avg_monthly_demand = b_data["annual_forecast"] / 12.0 if b_data["annual_forecast"] > 0 else 0
        avg_inventory = avg_monthly_demand + safety_stock
        unit_price = brand_prices.get(brand, 0)
        financing_cost = avg_inventory * 1.08 * (interest_rt / 100.0) * unit_price # 1.08 factor for overhead/insurance

        results[brand] = {
            "annual_forecast": b_data["annual_forecast"], "safety_stock": safety_stock,
            "avg_inventory": avg_inventory, "financing_cost": financing_cost
        }
    return results


# =====================================================
# TAB 2: Run Calculations
# =====================================================
with tab_calculations:
    st.markdown("<p class='section-header-font'><i class='fas fa-cogs icon'></i>Calculate Network Costs</p>", unsafe_allow_html=True)
    st.info("ℹ️ Click the buttons below to calculate each cost component based on the completed setup. Results are stored for the summary.")

    # Check if setup is complete and valid before allowing calculations
    if not st.session_state.config_complete:
         st.error("❌ Cannot perform calculations. Please complete the setup in the 'Setup Configuration' tab and resolve any validation errors.")
    elif not market_area_data and selected_market_areas: # Check if markets were selected but data is missing (e.g., no brands chosen)
         st.warning("⚠️ Market area data seems incomplete (perhaps no brands were selected for active markets?). Calculations might yield zero results. Please check Setup.")
         # Allow calculation but with a warning
         can_calculate = True
    elif not selected_market_areas:
        st.error("❌ Cannot perform calculations. No market areas selected in Setup.")
        can_calculate = False
    else:
        can_calculate = True # Setup looks okay

    if can_calculate:
        # Layout for calculation sections
        calc_col1, calc_col2 = st.columns(2)

        with calc_col1:
             # --- Rental Cost Calculation ---
             with st.container(border=True):
                 st.markdown("<p class='sub-header-font'><i class='fas fa-building icon'></i>Rental Costs</p>", unsafe_allow_html=True)
                 if st.button("Calculate Rental Costs", key="calc_rental", type="primary"):
                     with st.spinner("Calculating Rental Costs..."): time.sleep(0.5)
                     rental_details = [] ; total_rental_cost = 0.0 ; valid_calc_input = True
                     for i, wh in enumerate(warehouse_data):
                         rent_method = wh["rent_pricing_method"] ; rent_price = wh["rent_price"] ; wh_type = wh["type"]
                         wh_area = 0.0 ; wh_rental_cost = 0.0 ; calculated_units = 0.0
                         if rent_method == "Fixed Rent Price":
                             wh_rental_cost = rent_price ; wh_area = "N/A (Fixed)"
                         else: # Square Foot based
                             overhead = overhead_factor_main if wh_type == "MAIN" else overhead_factor_front
                             if sq_ft_per_unit <= 0: st.error("Sq Ft/Unit must > 0."); valid_calc_input = False; break
                             if rent_price <= 0: st.error(f"Sq Ft Rent Price must > 0 for WH {i+1}."); valid_calc_input = False; break
                             max_monthly = compute_max_monthly_forecast(wh, market_area_data)
                             if wh_type == "MAIN":
                                 safety_stock_main = compute_safety_stock_main(wh, market_area_data, Z_value, layout_type, warehouse_data)
                                 calculated_units = max_monthly + safety_stock_main
                             else: # FRONT
                                 daily_sum = compute_daily_demand_sum(wh, market_area_data)
                                 calculated_units = (max_monthly / 4.0) + (daily_sum * 12.0) # e.g., 1 wk peak + 12d avg
                             wh_area = sq_ft_per_unit * overhead * calculated_units
                             wh_rental_cost = rent_price * wh_area
                         rental_details.append({"Warehouse": f"WH {i+1} ({wh.get('location')})", "Type": wh_type, "Pricing": rent_method, "Est. Sq Ft": f"{wh_area:.0f}" if isinstance(wh_area, (int, float)) else wh_area, "Annual Rent ($)": f"{wh_rental_cost:,.0f}"})
                         total_rental_cost += wh_rental_cost
                     if valid_calc_input:
                         st.session_state.total_rental_cost = total_rental_cost
                         st.session_state.rental_details_df = pd.DataFrame(rental_details)
                         st.session_state.rental_costs_calculated = True ; st.success("✅ Rental Costs Calculated!")
                     else: st.session_state.rental_costs_calculated = False
                 # Display Rental Results
                 if st.session_state.rental_costs_calculated:
                     st.metric("Total Annual Rental Cost", f"${st.session_state.total_rental_cost:,.0f}")
                     # Adjust columns for better display
                     st.dataframe(st.session_state.rental_details_df, use_container_width=True, hide_index=True,
                                  column_config={"Annual Rent ($)": st.column_config.NumberColumn(format="$ %d"),
                                                 "Est. Sq Ft": st.column_config.NumberColumn(format="%d sq ft") if "Est. Sq Ft" in st.session_state.rental_details_df else None}
                                 )
                 else: st.info("Rental cost results appear here.")

             st.divider() # Separator

             # --- Shipping Cost Calculation ---
             with st.container(border=True):
                 st.markdown("<p class='sub-header-font'><i class='fas fa-truck-loading icon'></i>Shipping Costs</p>", unsafe_allow_html=True)
                 if st.button("Calculate Shipping Costs", key="calc_shipping", type="primary"):
                     with st.spinner("Calculating Shipping Costs..."): time.sleep(0.5)
                     shipping_details = [] ; total_shipping_cost = 0.0 ; valid_calc_input = True
                     if container_capacity_40 <= 0: st.error("Container Capacity must > 0."); valid_calc_input = False
                     for i, wh in enumerate(warehouse_data):
                          if not valid_calc_input: break
                          annual_demand_wh = compute_annual_demand(wh, market_area_data)
                          wh_shipping_cost = 0.0 ; shipment_type = "N/A"
                          if wh["type"] == "MAIN":
                              cost_per_40hc = wh.get("shipping_cost_40hc", 0)
                              if cost_per_40hc <= 0 and annual_demand_wh > 0: st.error(f"Int'l Ship Cost for WH {i+1} must > 0."); valid_calc_input = False; break
                              num_containers = ceil(annual_demand_wh / container_capacity_40) if container_capacity_40 > 0 else 0
                              wh_shipping_cost = num_containers * cost_per_40hc
                              shipment_type = f"{num_containers} x 40HC Int'l"
                              if layout_type == "Main Regionals" and "land_shipping_data" in wh:
                                  regional_land_cost = 0
                                  for area, ship_data in wh["land_shipping_data"].items():
                                      area_annual_demand = compute_annual_forecast_for_area(area, market_area_data)
                                      area_avg_order_size = ship_data.get("calculated_avg_order_size", 1)
                                      cost_per_avg_order = ship_data.get("cost_for_avg_order", 0)
                                      if area_avg_order_size > 0 and cost_per_avg_order > 0:
                                          num_orders = ceil(area_annual_demand / area_avg_order_size)
                                          regional_land_cost += num_orders * cost_per_avg_order
                                      elif area_annual_demand > 0 and cost_per_avg_order <= 0: st.warning(f"Missing regional ship cost for {area} from {wh['location']}.")
                                  wh_shipping_cost += regional_land_cost
                                  shipment_type += f" + Reg. Land" # Keep label shorter
                          elif wh["type"] == "FRONT":
                              cost_per_53ft = wh.get("front_shipping_cost_53", 600) # Default if missing? Better to error check
                              if cost_per_53ft <= 0 and annual_demand_wh > 0: st.error(f"Transfer Ship Cost for WH {i+1} must > 0."); valid_calc_input = False; break
                              truck_capacity = container_capacity_40 * 1.3 # Approx. 53ft capacity
                              num_trucks = ceil(annual_demand_wh / truck_capacity) if truck_capacity > 0 else 0
                              wh_shipping_cost = num_trucks * cost_per_53ft
                              shipment_type = f"{num_trucks} x 53ft Transfer"
                          shipping_details.append({"Warehouse": f"WH {i+1} ({wh.get('location')})", "Type": wh["type"], "Demand": f"{annual_demand_wh:,.0f}", "Shipments": shipment_type, "Annual Cost ($)": f"{wh_shipping_cost:,.0f}"})
                          total_shipping_cost += wh_shipping_cost
                     if valid_calc_input:
                         st.session_state.total_shipping_cost = total_shipping_cost
                         st.session_state.shipping_details_df = pd.DataFrame(shipping_details)
                         st.session_state.shipping_costs_calculated = True ; st.success("✅ Shipping Costs Calculated!")
                     else: st.session_state.shipping_costs_calculated = False
                 # Display Shipping Results
                 if st.session_state.shipping_costs_calculated:
                     st.metric("Total Annual Shipping Cost", f"${st.session_state.total_shipping_cost:,.0f}")
                     st.dataframe(st.session_state.shipping_details_df, use_container_width=True, hide_index=True,
                                  column_config={"Annual Cost ($)": st.column_config.NumberColumn(format="$ %d"),
                                                 "Demand": st.column_config.NumberColumn(format="%d Units")})
                 else: st.info("Shipping cost results appear here.")

        with calc_col2:
             # --- Inventory Financing Calculation ---
             with st.container(border=True):
                 st.markdown("<p class='sub-header-font'><i class='fas fa-coins icon'></i>Inventory Financing Costs</p>", unsafe_allow_html=True)
                 if st.button("Calculate Inventory Financing", key="calc_inventory", type="primary"):
                     with st.spinner("Calculating Inventory Financing..."): time.sleep(0.5)
                     inventory_details = [] ; total_inv_fin_cost = 0.0
                     total_avg_inv_units = 0.0 ; total_ss_units = 0.0 ; valid_calc_input = True
                     if interest_rate < 0 or service_level < 0: st.error("Interest Rate/Service Level invalid."); valid_calc_input = False
                     if any(p <= 0 for p in brand_unit_prices.values()): st.error("Brand Prices must > 0."); valid_calc_input = False

                     if layout_type == "Central and Fronts":
                         main_wh_list = [wh for wh in warehouse_data if wh["type"] == "MAIN"]
                         if len(main_wh_list) != 1: st.error("Exactly one MAIN WH needed."); valid_calc_input = False
                         elif valid_calc_input:
                             main_wh = main_wh_list[0]
                             breakdown = compute_inventory_breakdown(main_wh, market_area_data, interest_rate, brand_unit_prices, Z_value, layout_type, warehouse_data)
                             for brand, bdata in breakdown.items():
                                  inventory_details.append({"WH": f"WH {warehouse_data.index(main_wh)+1}", "Brand": brand, "SS (Units)": f"{bdata['safety_stock']:.0f}", "Avg Inv (Units)": f"{bdata['avg_inventory']:.0f}", "Fin. Cost ($)": f"{bdata['financing_cost']:.0f}"})
                                  total_inv_fin_cost += bdata['financing_cost'] ; total_avg_inv_units += bdata['avg_inventory'] ; total_ss_units += bdata['safety_stock']
                     elif layout_type == "Main Regionals":
                          for i, wh in enumerate(warehouse_data):
                              if wh["type"] == "MAIN" and valid_calc_input:
                                  breakdown = compute_inventory_breakdown(wh, market_area_data, interest_rate, brand_unit_prices, Z_value, layout_type, warehouse_data)
                                  for brand, bdata in breakdown.items():
                                      inventory_details.append({"WH": f"WH {i+1}", "Brand": brand, "SS (Units)": f"{bdata['safety_stock']:.0f}", "Avg Inv (Units)": f"{bdata['avg_inventory']:.0f}", "Fin. Cost ($)": f"{bdata['financing_cost']:.0f}"})
                                      total_inv_fin_cost += bdata['financing_cost'] ; total_avg_inv_units += bdata['avg_inventory'] ; total_ss_units += bdata['safety_stock']

                     if valid_calc_input:
                          st.session_state.total_inventory_financing_cost = total_inv_fin_cost
                          st.session_state.inventory_details_df = pd.DataFrame(inventory_details)
                          st.session_state.aggregated_inventory_metrics = {"Avg Inv Units": total_avg_inv_units, "SS Units": total_ss_units}
                          st.session_state.inventory_costs_calculated = True ; st.success("✅ Inventory Financing Costs Calculated!")
                     else: st.session_state.inventory_costs_calculated = False
                 # Display Inventory Results
                 if st.session_state.inventory_costs_calculated:
                      col_inv1, col_inv2, col_inv3 = st.columns(3)
                      with col_inv1: st.metric("Total Annual Financing Cost", f"${st.session_state.total_inventory_financing_cost:,.0f}")
                      with col_inv2: st.metric("Total Avg Inventory", f"{st.session_state.aggregated_inventory_metrics['Avg Inv Units']:,.0f} U")
                      with col_inv3: st.metric("Total Safety Stock", f"{st.session_state.aggregated_inventory_metrics['SS Units']:,.0f} U")
                      st.dataframe(st.session_state.inventory_details_df, use_container_width=True, hide_index=True,
                                   column_config={"Fin. Cost ($)": st.column_config.NumberColumn(format="$ %d"),
                                                  "SS (Units)": st.column_config.NumberColumn(format="%d"),
                                                  "Avg Inv (Units)": st.column_config.NumberColumn(format="%d")})
                      # Bar chart for costs per brand
                      if not st.session_state.inventory_details_df.empty:
                           df_inv_chart = st.session_state.inventory_details_df.copy()
                           df_inv_chart['Fin. Cost ($)'] = df_inv_chart['Fin. Cost ($)'].str.replace('[$,]', '', regex=True).astype(float)
                           df_inv_chart = df_inv_chart[df_inv_chart['Fin. Cost ($)'] > 0] # Filter zero costs
                           if not df_inv_chart.empty:
                                brand_costs_agg = df_inv_chart.groupby('Brand')['Fin. Cost ($)'].sum().reset_index()
                                fig_inv_bar = px.bar(brand_costs_agg, x='Brand', y='Fin. Cost ($)', title="Annual Inventory Financing Cost by Brand", text_auto='.2s', labels={'Fin. Cost ($)': 'Financing Cost ($)'})
                                fig_inv_bar.update_layout(yaxis_title="Financing Cost ($)", xaxis_title="Brand", title_x=0.5) ; fig_inv_bar.update_traces(textposition='outside')
                                st.plotly_chart(fig_inv_bar, use_container_width=True)
                           else: st.info("No non-zero inventory financing costs to plot.")
                 else: st.info("Inventory financing results appear here.")

             st.divider() # Separator

             # --- Labor Cost Calculation ---
             with st.container(border=True):
                st.markdown("<p class='sub-header-font'><i class='fas fa-users icon'></i>Labor Costs</p>", unsafe_allow_html=True)
                if st.button("Calculate Labor Costs", key="calc_labor", type="primary"):
                    with st.spinner("Calculating Labor Costs..."): time.sleep(0.5)
                    labor_details = [] ; total_labor_cost = 0.0 ; valid_calc_input = True
                    for i, wh in enumerate(warehouse_data):
                        num_emp = wh.get("num_employees", 0) ; salary = wh.get("avg_employee_salary", 0)
                        if num_emp < 0 or salary < 0: st.error(f"Employees/Salary must be >= 0 for WH {i+1}."); valid_calc_input = False; break
                        wh_labor_cost = num_emp * salary
                        labor_details.append({"Warehouse": f"WH {i+1} ({wh.get('location')})", "Type": wh["type"], "# Emp": num_emp, "Avg Salary ($)": f"{salary:,.0f}", "Annual Cost ($)": f"{wh_labor_cost:,.0f}"})
                        total_labor_cost += wh_labor_cost
                    if valid_calc_input:
                        st.session_state.total_labor_cost = total_labor_cost
                        st.session_state.labor_details_df = pd.DataFrame(labor_details)
                        st.session_state.labor_costs_calculated = True ; st.success("✅ Labor Costs Calculated!")
                    else: st.session_state.labor_costs_calculated = False
                # Display Labor Results
                if st.session_state.labor_costs_calculated:
                    st.metric("Total Annual Labor Cost", f"${st.session_state.total_labor_cost:,.0f}")
                    st.dataframe(st.session_state.labor_details_df, use_container_width=True, hide_index=True,
                                 column_config={"Annual Cost ($)": st.column_config.NumberColumn(format="$ %d"),
                                                "Avg Salary ($)": st.column_config.NumberColumn(format="$ %d")})
                else: st.info("Labor cost results appear here.")


# =====================================================
# TAB 3: Results Summary
# =====================================================
with tab_summary:
    st.markdown("<p class='section-header-font'><i class='fas fa-chart-pie icon'></i>Scenario Cost Summary</p>", unsafe_allow_html=True)

    # Check if all cost components have been successfully calculated
    all_calculated = (st.session_state.rental_costs_calculated and
                      st.session_state.inventory_costs_calculated and
                      st.session_state.shipping_costs_calculated and
                      st.session_state.labor_costs_calculated)

    if not st.session_state.config_complete:
         st.error("❌ Cannot show summary. Setup configuration is incomplete or invalid. Please check the 'Setup Configuration' tab.")
    elif not all_calculated:
        st.warning("⚠️ Please calculate all cost components in the 'Run Calculations' tab to see the full summary.")
    else:
        # --- Calculate and Display Grand Total ---
        st.session_state.grand_total = (st.session_state.total_rental_cost +
                                         st.session_state.total_inventory_financing_cost +
                                         st.session_state.total_shipping_cost +
                                         st.session_state.total_labor_cost)

        st.markdown("### Total Estimated Annual Costs")
        # Display Key Metrics using styled cards
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        with metric_col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Rental Cost", f"${st.session_state.total_rental_cost:,.0f}")
            st.markdown("</div>", unsafe_allow_html=True)
        with metric_col2:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Inventory Financing", f"${st.session_state.total_inventory_financing_cost:,.0f}")
            st.markdown("</div>", unsafe_allow_html=True)
        with metric_col3:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Shipping Cost", f"${st.session_state.total_shipping_cost:,.0f}")
            st.markdown("</div>", unsafe_allow_html=True)
        with metric_col4:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Labor Cost", f"${st.session_state.total_labor_cost:,.0f}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---") # Divider
        # Grand Total Display (centered)
        st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: #1E3A5F;'>Grand Total Annual Cost: ${st.session_state.grand_total:,.0f}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---") # Divider

        # --- Cost Breakdown Visualization ---
        st.markdown("### Cost Component Breakdown")
        cost_data = {
            'Cost Component': ['Rental', 'Inventory Financing', 'Shipping', 'Labor'],
            'Cost ($)': [st.session_state.total_rental_cost,
                         st.session_state.total_inventory_financing_cost,
                         st.session_state.total_shipping_cost,
                         st.session_state.total_labor_cost]
        }
        cost_df_pie = pd.DataFrame(cost_data)
        cost_df_pie = cost_df_pie[cost_df_pie['Cost ($)'] > 0] # Exclude zero costs from pie chart

        if not cost_df_pie.empty:
            fig_pie = px.pie(cost_df_pie, values='Cost ($)', names='Cost Component',
                             title='Distribution of Annual Costs', hole=0.3, # Donut chart
                             color_discrete_sequence=px.colors.Sequential.Blues_r) # Blue color theme
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent+value')
            fig_pie.update_layout(title_x=0.5, showlegend=True, legend_title_text='Cost Components')
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No non-zero cost data to display in the breakdown chart.")

        # --- Warehouse Level Summary Table ---
        st.markdown("### Summary per Warehouse (Combined Costs)")
        summary_list = []
        # Use the validated warehouse_data list from the setup tab
        valid_wh_data_for_summary = warehouse_data

        for i, wh in enumerate(valid_wh_data_for_summary):
             wh_label = f"WH {i+1} ({wh.get('location')})"
             wh_summary = {"Warehouse": wh_label, "Type": wh.get("type")}
             rental_cost, inv_cost, ship_cost, labor_cost = 0.0, 0.0, 0.0, 0.0 # Initialize

             # Safely retrieve costs from stored DataFrames
             if not st.session_state.rental_details_df.empty:
                 rent_row = st.session_state.rental_details_df[st.session_state.rental_details_df['Warehouse'] == wh_label]
                 if not rent_row.empty: try: rental_cost = float(rent_row.iloc[0]['Annual Rent ($)'].replace(',', '')) ; except: pass
             if not st.session_state.inventory_details_df.empty:
                  inv_rows = st.session_state.inventory_details_df[st.session_state.inventory_details_df['WH'] == f"WH {i+1}"] # Match WH number
                  if not inv_rows.empty: try: inv_cost = inv_rows['Fin. Cost ($)'].str.replace('[$,]', '', regex=True).astype(float).sum(); except: pass
             if not st.session_state.shipping_details_df.empty:
                 ship_row = st.session_state.shipping_details_df[st.session_state.shipping_details_df['Warehouse'] == wh_label]
                 if not ship_row.empty: try: ship_cost = float(ship_row.iloc[0]['Annual Cost ($)'].replace(',', '')); except: pass
             if not st.session_state.labor_details_df.empty:
                 labor_row = st.session_state.labor_details_df[st.session_state.labor_details_df['Warehouse'] == wh_label]
                 if not labor_row.empty: try: labor_cost = float(labor_row.iloc[0]['Annual Cost ($)'].replace(',', '')); except: pass

             wh_summary["Rental ($)"] = rental_cost
             wh_summary["Inventory ($)"] = inv_cost
             wh_summary["Shipping ($)"] = ship_cost
             wh_summary["Labor ($)"] = labor_cost
             wh_summary["Total ($)"] = rental_cost + inv_cost + ship_cost + labor_cost
             summary_list.append(wh_summary)

        if summary_list:
             summary_df = pd.DataFrame(summary_list)
             # Display summary table with formatting
             st.dataframe(summary_df, hide_index=True, use_container_width=True,
                          column_config={ # Apply number formatting to cost columns
                              "Rental ($)": st.column_config.NumberColumn(format="$ %d"),
                              "Inventory ($)": st.column_config.NumberColumn(format="$ %d"),
                              "Shipping ($)": st.column_config.NumberColumn(format="$ %d"),
                              "Labor ($)": st.column_config.NumberColumn(format="$ %d"),
                              "Total ($)": st.column_config.NumberColumn(format="$ %d"),
                          })
        else:
             st.info("Warehouse summary data could not be generated (check calculations).")

        # --- Placeholder for Submission/Export Action ---
        st.markdown("---")
        st.markdown("### Actions")
        if st.button("Generate Report / Submit Scenario", type="primary", key="submit_button"):
            st.success("✅ Scenario data processed! (Report generation/submission not implemented in this example)")
            # Example placeholder for export:
            # if 'summary_df' in locals() and not summary_df.empty:
            #      csv = summary_df.to_csv(index=False).encode('utf-8')
            #      st.download_button(label="Download Summary as CSV", data=csv, file_name='scenario_summary.csv', mime='text/csv')