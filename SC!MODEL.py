# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.express as px
import plotly.graph_objects as go
from math import sqrt, ceil
from scipy.stats import norm

# --- UI Enhancement Start ---
# Initialize session state variables for storing results
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
# --- UI Enhancement End ---

# -----------------------------------------------------
# Page Configuration and Enhanced Custom CSS
# -----------------------------------------------------
st.set_page_config(
    page_title="Supply Chain Optimization Dashboard",
    page_icon="🚚", # Standard emoji icon
    layout="wide"
)

# --- UI Enhancement Start ---
# Inject Font Awesome and refined CSS
st.markdown(
    """
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
    </head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');

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

        /* Section Headers */
        .section-header-font {
            font-size: 26px !important;
            font-weight: 700;
            color: #2C3E50; /* Dark Slate Gray */
            margin-top: 30px;
            margin-bottom: 15px;
            border-bottom: 2px solid #3498DB; /* Blue underline */
            padding-bottom: 5px;
        }

        /* Sub-section Headers */
        .sub-header-font {
            font-size: 20px !important;
            font-weight: 500;
            color: #34495E; /* Wet Asphalt */
            margin-top: 15px;
            margin-bottom: 10px;
        }

        /* Input Card Container */
        .input-card {
            background-color: #FFFFFF;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border: 1px solid #EAECEE; /* Light border */
        }

        /* Expander Styling */
        .stExpander {
            border: 1px solid #EAECEE !important;
            border-radius: 8px !important;
            margin-bottom: 15px !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stExpander header {
            font-weight: 500;
            font-size: 18px; /* Larger expander header */
            background-color: #F8F9F9; /* Light background for header */
            border-radius: 8px 8px 0 0 !important;
            padding: 10px 15px !important;
        }
        .stExpander header:hover {
             background-color: #E8F6F3; /* Light green on hover */
        }

        /* Metric Card Styling */
        .metric-card {
            background-color: #FFFFFF;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            text-align: center;
            border: 1px solid #EAECEE;
        }
        .metric-card .stMetric { /* Target metric inside the card */
             background-color: transparent !important; /* Override default */
             border: none !important;
             padding: 0 !important;
        }
        .metric-card label { /* Metric Label */
            font-weight: 500;
            color: #566573; /* Grayish blue */
        }
         .metric-card p { /* Metric Value */
            font-size: 24px !important;
            font-weight: 700;
            color: #1A5276; /* Stronger blue */
        }

         /* Tab Styling - Use simple text labels for tabs now */
        .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            white-space: pre-wrap;
            background-color: #F0F2F6;
            border-radius: 8px 8px 0px 0px;
            gap: 1px;
            padding-top: 10px;
            padding-bottom: 10px;
            font-weight: 500;
        }
        .stTabs [aria-selected="true"] {
            background-color: #FFFFFF; /* White background for selected tab */
            color: #3498DB; /* Blue text for selected tab */
            font-weight: 700;
            border-bottom: 3px solid #3498DB;
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
        }
        .stButton>button:hover {
            background-color: #2874A6; /* Darker Blue */
            color: white;
        }
         .stButton>button:focus {
             box-shadow: 0 0 0 2px #AED6F1 !important; /* Light blue focus ring */
             background-color: #2E86C1;
             color: white;
         }


        /* Icon styling */
        .icon {
            margin-right: 8px;
            color: #5D6D7E; /* Slightly muted icon color */
        }
        /* Style for markdown labels used with widgets */
        .widget-label {
            font-weight: 500;
            margin-bottom: -5px; /* Adjust spacing between markdown label and widget */
            color: #34495E;
        }

    </style>
    """,
    unsafe_allow_html=True
)
# --- UI Enhancement End ---

# --- Header using markdown for icon rendering ---
st.markdown("<p class='main-header-font'><i class='fas fa-cogs icon'></i>Supply Chain & Warehouse Network Optimization</p>", unsafe_allow_html=True)

# -------------------------
# Sidebar: Global Parameters (with icons and dividers)
# -------------------------
with st.sidebar:
    # --- UI Enhancement Start ---
    st.markdown("## <i class='fas fa-globe icon'></i> Global Settings", unsafe_allow_html=True)
    st.divider()

    # --- Fix: Use markdown for label ---
    st.markdown("<p class='widget-label'><i class='fas fa-percentage icon'></i> Actual Interest Rate (%)</p>", unsafe_allow_html=True)
    interest_rate = st.number_input(
        label="", # Use empty label for the widget itself
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=0.1,
        help="Enter the annual interest rate used for inventory financing calculations.",
        label_visibility="collapsed" # Hide the empty label space
    )

    # --- Fix: Use markdown for label ---
    st.markdown("<p class='widget-label'><i class='fas fa-shield-alt icon'></i> Required Service Level (0-1)</p>", unsafe_allow_html=True)
    service_level = st.slider(
        label="", # Use empty label for the widget itself
        min_value=0.0,
        max_value=1.0,
        value=0.95,
        help="Set the desired probability of not stocking out (used for safety stock calculation).",
        label_visibility="collapsed" # Hide the empty label space
    )

    st.divider()

    # --- Fix: Use markdown for label ---
    st.markdown("<p class='widget-label'><i class='fas fa-warehouse icon'></i> Layout Type</p>", unsafe_allow_html=True)
    layout_type = st.radio(
        label="", # Use empty label for the widget itself
        options=["Central and Fronts", "Main Regionals"],
        help="Select the overall warehouse network structure: Central Hub with Fronts or multiple independent Main Regional warehouses.",
        key="layout_type_radio", # Add a key to avoid potential state issues
        horizontal=True, # Keep horizontal layout if desired
        label_visibility="collapsed" # Hide the empty label space
    )
    # Info messages remain the same
    if layout_type == "Main Regionals":
        st.info("ℹ️ With 'Main Regionals', all defined warehouses will function as MAIN type, serving their assigned markets directly from the central source.")
    else:
         st.info("ℹ️ With 'Central and Fronts', define one MAIN warehouse and potentially multiple FRONT warehouses served by the MAIN warehouse.")

    st.divider()
    st.markdown("### <i class='fas fa-box-open icon'></i> Container Capacity", unsafe_allow_html=True)
    container_capacity_40 = st.number_input(
        "Capacity for 40ft HC (Units)", # Keep simple label here or use markdown above as well
        min_value=1, # Cannot be 0
        value=600,
        step=1,
        format="%d",
        help="Define the typical number of saleable units (e.g., 4-panel sets) that fit into a standard 40ft High Cube container."
    )
    # --- UI Enhancement End ---

# Calculate Z_value: if service_level == 1.0, set to a high value; otherwise, compute using the norm
if service_level >= 1.0: # Handle potential floating point issues >= 1
    Z_value = 5 # Use a high Z-score for near 100% service level
elif service_level <= 0.0:
    Z_value = -5 # Use a low Z-score for 0% service level (though practically unlikely)
else:
    Z_value = norm.ppf(service_level)

# -------------------------
# Main App Tabs
# -------------------------
# --- UI Enhancement Start ---
# --- Fix: Use simple text labels for tabs ---
tab_setup, tab_calculations, tab_summary = st.tabs([
    "Setup Configuration",
    "Run Calculations",
    "Results Summary"
])
# --- UI Enhancement End ---

# =====================================================
# TAB 1: Setup – Inputs for Brands, Rental, Markets & Warehouses
# =====================================================
with tab_setup:
    # --- Headers using markdown for icon rendering (already correct) ---
    st.markdown("<p class='section-header-font'><i class='fas fa-edit icon'></i>Define Your Network Parameters</p>", unsafe_allow_html=True)

    # --- UI Enhancement Start ---
    col_setup_1, col_setup_2 = st.columns(2)

    with col_setup_1:
        with st.container(border=True): # Use border argument for simple card
             # --- Headers using markdown (already correct) ---
             st.markdown("<p class='sub-header-font'><i class='fas fa-tags icon'></i>Brand Pricing</p>", unsafe_allow_html=True)
             BRANDS = ["Heliocol", "SunStar", "SunValue"]
             brand_unit_prices = {}
             brand_cols = st.columns(len(BRANDS))
             for idx, brand in enumerate(BRANDS):
                 with brand_cols[idx]:
                     # Input labels are simple text - okay
                     brand_unit_prices[brand] = st.number_input(
                         f"Unit Price ({brand})",
                         min_value=0.0,
                         value=80.0,
                         step=1.0,
                         help=f"Enter the selling price or inventory valuation price (per 4 panels in $) for {brand}.",
                         key=f"{brand}_unit_price"
                     )

    with col_setup_2:
         with st.container(border=True): # Use border argument
            # --- Headers using markdown (already correct) ---
            st.markdown("<p class='sub-header-font'><i class='fas fa-ruler-combined icon'></i>Rental Parameters</p>", unsafe_allow_html=True)
            rent_cols = st.columns(3)
            with rent_cols[0]:
                # Input labels are simple text - okay
                sq_ft_per_unit = st.number_input(
                    "Sq Ft per Unit",
                    min_value=0.1, # Min value > 0
                    value=0.8,
                    step=0.1,
                    format="%.1f",
                    help="Square feet required to store one unit (e.g., 4 panels)."
                )
            with rent_cols[1]:
                 # Input labels are simple text - okay
                overhead_factor_main = st.number_input(
                    "Overhead (MAIN)",
                    min_value=1.0,
                    value=1.2,
                    step=0.1,
                    format="%.1f",
                    help="Space multiplication factor for MAIN warehouses (aisles, offices, etc.). E.g., 1.2 means 20% overhead space."
                )
            with rent_cols[2]:
                 # Input labels are simple text - okay
                 overhead_factor_front = st.number_input(
                    "Overhead (FRONT)",
                    min_value=1.0,
                    value=1.5,
                    step=0.1,
                    format="%.1f",
                    help="Space multiplication factor for FRONT warehouses (often need more relative overhead)."
                )
    # --- UI Enhancement End ---

    # --- Headers using markdown (already correct) ---
    st.markdown("<p class='section-header-font'><i class='fas fa-map-marker-alt icon'></i>Market Areas Setup</p>", unsafe_allow_html=True)
    # --- UI Enhancement Start ---
    with st.container(border=True):
        base_market_areas = ["FL", "CA_SOUTH", "CA_NORTH", "TX", "NJ"]
        st.write("Standard market areas:", ", ".join(base_market_areas))
         # Input labels are simple text - okay
        custom_market_areas_str = st.text_input(
            "Enter additional market areas (comma separated)",
            value="",
            help="Define extra market regions if needed. E.g., NY, PA, OH"
        )
        custom_market_areas = [area.strip().upper() for area in custom_market_areas_str.split(",") if area.strip() != ""] # Standardize to upper
        all_market_areas = sorted(list(dict.fromkeys(base_market_areas + custom_market_areas))) # Sort alphabetically

        # Input labels are simple text - okay
        selected_market_areas = st.multiselect(
            "Select Market Areas to Include in this Scenario",
            options=all_market_areas,
            default=all_market_areas, # Select all by default
            help="Choose which defined market areas to actively use in the calculations."
        )

        market_area_data = {}
        if not selected_market_areas:
            st.warning("Please select at least one market area.")
        else:
            st.markdown("<p class='sub-header-font'>Configure Parameters for Selected Market Areas:</p>", unsafe_allow_html=True)
            # Use expanders for each market area
            for area in selected_market_areas:
                 # Expander title is simple text - okay
                 with st.expander(f"Parameters for Market Area: {area}", expanded=False):
                    brand_data = {}
                    for brand in BRANDS:
                        # --- Headers using markdown (already correct) ---
                        st.markdown(f"<b><i class='fas fa-tag icon'></i>Brand: {brand}</b>", unsafe_allow_html=True)
                        col1, col2, col3 = st.columns(3)
                        with col1:
                             # Input labels are simple text - okay
                            avg_order_size = st.number_input(
                                f"Avg Order Size",
                                min_value=0, value=100, step=1, format="%d",
                                key=f"{area}_{brand}_avg_order_size",
                                help=f"Typical order size for {brand} in {area}."
                            )
                        with col2:
                             # Input labels are simple text - okay
                            avg_daily_demand = st.number_input(
                                f"Avg Daily Demand",
                                min_value=0, value=50, step=1, format="%d",
                                key=f"{area}_{brand}_avg_daily_demand",
                                help=f"Average daily sales/usage for {brand} in {area}."
                            )
                        with col3:
                            # Input labels are simple text - okay
                            std_daily_demand = st.number_input(
                                f"Std Dev Daily Demand",
                                min_value=0.0, value=10.0, step=1.0,
                                key=f"{area}_{brand}_std_daily_demand",
                                help=f"Standard deviation (volatility) of daily demand for {brand} in {area}."
                            )

                        st.markdown(f"<b>12-Month Forecast Demand ({brand} - {area})</b>", unsafe_allow_html=True)
                        forecast = []
                        forecast_cols = st.columns(6)
                        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                        for m in range(12):
                            with forecast_cols[m % 6]:
                                # Input labels are simple text - okay
                                val = st.number_input(
                                    f"{months[m]}",
                                    min_value=0, value=500, step=1, format="%d", # Added default value
                                    key=f"{area}_{brand}_forecast_{m}",
                                    help=f"Forecast demand for {brand} in {area} for month {m+1}."
                                )
                                forecast.append(val)
                        st.divider()
                        brand_data[brand] = {
                            "avg_order_size": avg_order_size,
                            "avg_daily_demand": avg_daily_demand,
                            "std_daily_demand": std_daily_demand,
                            "forecast_demand": forecast
                        }
                    market_area_data[area] = brand_data
    # --- UI Enhancement End ---

    # --- Headers using markdown (already correct) ---
    st.markdown("<p class='section-header-font'><i class='fas fa-industry icon'></i>Warehouse Setup</p>", unsafe_allow_html=True)
    # --- UI Enhancement Start ---
    with st.container(border=True):
        base_warehouse_locations = ["FL", "CA_SOUTH", "CA_NORTH", "TX", "NJ"]
        st.write("Standard potential warehouse locations:", ", ".join(base_warehouse_locations))
        # Input labels are simple text - okay
        custom_warehouse_locations_str = st.text_input(
            "Enter additional potential warehouse locations (comma separated)",
            value="",
            key="warehouse_locations_text",
            help="Define extra potential locations for warehouses. E.g., NY, PA"
        )
        custom_warehouse_locations = [loc.strip().upper() for loc in custom_warehouse_locations_str.split(",") if loc.strip() != ""] # Standardize to upper
        all_warehouse_locations = sorted(list(dict.fromkeys(base_warehouse_locations + custom_warehouse_locations)))

        # Input labels are simple text - okay
        num_warehouses = st.number_input(
            "Number of Warehouses to Configure",
            min_value=1, value=1, step=1,
            help="Enter the total number of warehouses in this scenario."
        )

        warehouse_data = []
        temp_warehouse_configs = {}

        st.markdown("<p class='sub-header-font'>Configure Parameters for Each Warehouse:</p>", unsafe_allow_html=True)
        # Use expanders for each warehouse
        for i in range(int(num_warehouses)):
             # Expander title is simple text - okay
             with st.expander(f"Warehouse {i+1} Configuration", expanded=True if num_warehouses <= 2 else False):
                wh_config = {}
                col_loc, col_type = st.columns(2)
                with col_loc:
                    # Input labels are simple text - okay
                    location = st.selectbox(
                        f"Location (WH {i+1})",
                        options=[""] + all_warehouse_locations,
                        index=0,
                        key=f"wh_location_{i}",
                        help="Choose a location for this warehouse from the defined list."
                    )
                    wh_config["location"] = location if location else None

                with col_type:
                    if layout_type == "Main Regionals":
                        wh_type = "MAIN"
                        st.text_input(f"Type (WH {i+1})", value="MAIN (Regional Layout)", disabled=True)
                    else:
                        options = ["MAIN", "FRONT"]
                        has_main_already = any(w.get("type") == "MAIN" for w in temp_warehouse_configs.values())
                        if has_main_already:
                             options = ["FRONT"]

                        if not options:
                             st.error("Configuration error: Cannot add more warehouses.")
                             wh_type = None
                        else:
                             # Input labels are simple text - okay
                             wh_type = st.radio(
                                f"Type (WH {i+1})",
                                options=options,
                                key=f"wh_type_{i}",
                                horizontal=True,
                                help="Select warehouse type (MAIN hub or FRONT spoke)."
                            )
                    wh_config["type"] = wh_type

                # Input labels are simple text - okay
                served_markets = st.multiselect(
                    f"Market Areas Served by Warehouse {i+1}",
                    options=selected_market_areas,
                    key=f"wh_markets_{i}",
                    help="Select all market areas that this warehouse will directly serve."
                )
                wh_config["served_markets"] = served_markets

                if location and location not in served_markets:
                    st.error(f"Warehouse {i+1} location '{location}' must be included in its served market areas!")

                st.markdown("---")
                col_rent_method, col_rent_price = st.columns(2)
                with col_rent_method:
                    # Input labels are simple text - okay
                    rent_pricing_method = st.radio(
                        f"Rent Pricing Method (WH {i+1})",
                        options=["Fixed Rent Price", "Square Foot Rent Price"],
                        key=f"rent_method_{i}",
                        horizontal=True,
                        help="Choose how rent is calculated: a flat annual fee or based on calculated square footage."
                    )
                with col_rent_price:
                    if rent_pricing_method == "Fixed Rent Price":
                         # Input labels are simple text - okay
                        rent_price = st.number_input(
                            f"Fixed Rent Price (WH {i+1}) ($/year)",
                            min_value=0.0, value=50000.0, step=1000.0, format="%.0f",
                            key=f"fixed_rent_{i}"
                        )
                    else:
                         # Input labels are simple text - okay
                        rent_price = st.number_input(
                            f"Rent Price per Sq Ft (WH {i+1}) ($/year)",
                            min_value=0.0, value=10.0, step=0.5, format="%.1f",
                            key=f"sqft_rent_{i}"
                        )
                wh_config["rent_pricing_method"] = rent_pricing_method
                wh_config["rent_price"] = rent_price

                st.markdown("---")
                col_emp_sal, col_emp_num = st.columns(2)
                with col_emp_sal:
                     # Input labels are simple text - okay
                    avg_employee_salary = st.number_input(
                        f"Avg Annual Salary/Employee (WH {i+1}) ($)",
                        min_value=0, value=50000, step=1000, format="%d",
                        key=f"employee_salary_{i}"
                    )
                with col_emp_num:
                     default_emp = 0
                     if wh_type == "MAIN":
                        default_emp = 3 if len(served_markets) <= 1 else 4
                     elif wh_type == "FRONT":
                        default_emp = 2
                     # Input labels are simple text - okay
                     num_employees = st.number_input(
                        f"Number of Employees (WH {i+1})",
                        min_value=0, value=default_emp, step=1,
                        key=f"num_employees_{i}"
                    )
                wh_config["avg_employee_salary"] = avg_employee_salary
                wh_config["num_employees"] = num_employees

                # Shipping Inputs
                if wh_type == "MAIN":
                     # --- Headers using markdown (already correct) ---
                     st.markdown("<p class='sub-header-font' style='margin-top: 15px; color: #1A5276;'><i class='fas fa-ship icon'></i>International Shipping (MAIN WH {i+1})</p>", unsafe_allow_html=True)
                     ship_col1, ship_col2 = st.columns(2)
                     with ship_col1:
                          # Input labels are simple text - okay
                         lt_shipping = st.number_input(
                            "Lead Time (Israel to WH, days)",
                            min_value=0, value=30, step=1, format="%d",
                            key=f"lt_shipping_{i}",
                            help="Average transit time for ocean freight from source to this warehouse."
                        )
                     with ship_col2:
                          # Input labels are simple text - okay
                         shipping_cost_40hc = st.number_input(
                            "Shipping Cost (per 40HC, $)",
                            min_value=0.0, value=5000.0, step=100.0, format="%.0f",
                            key=f"shipping_cost_40hc_{i}",
                            help="Cost to ship one 40ft High Cube container from source to this warehouse."
                        )
                     wh_config["lt_shipping"] = lt_shipping
                     wh_config["shipping_cost_40hc"] = shipping_cost_40hc

                     if layout_type == "Main Regionals" and len(served_markets) > 1 and location:
                          # --- Headers using markdown (already correct) ---
                         st.markdown(f"<p class='sub-header-font' style='margin-top: 10px; color: #1A5276;'><i class='fas fa-truck icon'></i>Regional Land Shipping (WH {i+1} to other served areas)</p>", unsafe_allow_html=True)
                         land_shipping_data = {}
                         other_markets = [m for m in served_markets if m != location]
                         for add_area in other_markets:
                             land_cols = st.columns([2,3])
                             with land_cols[0]:
                                  # Input labels are simple text - okay
                                 distance_val = st.number_input(
                                    f"Distance to {add_area} (miles)",
                                    min_value=0.0, value=100.0, step=10.0, format="%.1f",
                                    key=f"dist_{i}_{add_area}"
                                )
                             with land_cols[1]:
                                 area_total_demand = sum(market_area_data[add_area][b]["avg_daily_demand"] for b in BRANDS if add_area in market_area_data and market_area_data[add_area][b]["avg_daily_demand"] > 0)
                                 if area_total_demand > 0:
                                     area_avg_order = sum(market_area_data[add_area][b]["avg_order_size"] * market_area_data[add_area][b]["avg_daily_demand"] for b in BRANDS if add_area in market_area_data) / area_total_demand
                                 else:
                                     area_avg_order = 0
                                 # Input labels are simple text - okay
                                 cost_val = st.number_input(
                                    f"Cost per Avg Order ({area_avg_order:.0f} units) to {add_area} ($)",
                                    min_value=0.0, value=50.0, step=1.0, format="%.2f",
                                    key=f"cost_{i}_{add_area}",
                                    help=f"Estimated land freight cost to ship an average order ({area_avg_order:.0f} units) from {location} to {add_area}."
                                )
                                 if cost_val == 0 and area_total_demand > 0:
                                     st.warning(f"Enter a non-zero shipping cost for {add_area} if there is demand.")
                             land_shipping_data[add_area] = {
                                "distance": distance_val,
                                "cost_for_avg_order": cost_val,
                                "calculated_avg_order_size": area_avg_order
                            }
                         wh_config["land_shipping_data"] = land_shipping_data

                elif wh_type == "FRONT":
                     # --- Headers using markdown (already correct) ---
                     st.markdown("<p class='sub-header-font' style='margin-top: 15px; color: #1A5276;'><i class='fas fa-exchange-alt icon'></i>Transfer Shipping (MAIN to FRONT WH {i+1})</p>", unsafe_allow_html=True)
                     main_wh_options = {f"WH {idx+1} ({w_conf['location']})": w_conf for idx, w_conf in temp_warehouse_configs.items() if w_conf.get("type") == "MAIN"}

                     if not main_wh_options:
                         st.error("Cannot configure FRONT warehouse: No MAIN warehouse has been defined yet in this session. Define a MAIN warehouse first.")
                         wh_config["serving_central_wh_key"] = None
                     else:
                          # Input labels are simple text - okay
                         serving_central_label = st.selectbox(
                            f"Select Serving MAIN Warehouse",
                            options=list(main_wh_options.keys()),
                            key=f"serving_central_{i}",
                            help="Choose the MAIN warehouse that supplies this FRONT warehouse."
                        )
                         serving_central_wh_key = main_wh_options[serving_central_label]
                         wh_config["serving_central_wh_key"] = serving_central_label

                         main_wh_served = serving_central_wh_key.get("served_markets", [])
                         front_wh_served = served_markets
                         common_markets = set(main_wh_served).intersection(set(front_wh_served))


                     front_ship_col1, front_ship_col2 = st.columns(2)
                     with front_ship_col1:
                          # Input labels are simple text - okay
                         front_shipping_cost_40 = st.number_input(
                            "Cost (per 40ft Truckload, $)",
                            min_value=0.0, value=500.0, step=1.0, format="%.0f",
                            key=f"front_shipping_cost_40_{i}",
                            help="Estimated cost to ship a 40ft truckload from the selected MAIN warehouse."
                         )
                     with front_ship_col2:
                          # Input labels are simple text - okay
                         front_shipping_cost_53 = st.number_input(
                            "Cost (per 53ft Truckload, $)",
                            min_value=0.0, value=600.0, step=1.0, format="%.0f",
                            key=f"front_shipping_cost_53_{i}",
                            help="Estimated cost to ship a 53ft truckload from the selected MAIN warehouse."
                         )
                     wh_config["front_shipping_cost_40"] = front_shipping_cost_40
                     wh_config["front_shipping_cost_53"] = front_shipping_cost_53


                temp_warehouse_configs[i] = wh_config

        warehouse_data = list(temp_warehouse_configs.values())

        # --- Validation section ---
        all_markets_served = set()
        config_complete = True
        final_warehouse_list_for_calc = []

        if layout_type == "Central and Fronts" and sum(1 for wh in warehouse_data if wh.get("type") == "MAIN") != 1:
             st.error("❌ Validation Error: In 'Central and Fronts' layout, exactly one MAIN warehouse must be defined.")
             config_complete = False

        for i, wh in enumerate(warehouse_data):
            if not wh.get("location"):
                st.error(f"❌ Validation Error: Location is missing for Warehouse {i+1}.")
                config_complete = False
            if not wh.get("served_markets"):
                st.error(f"❌ Validation Error: Served markets are missing for Warehouse {i+1} ({wh.get('location', 'N/A')}).")
                config_complete = False
            if wh.get("type") == "FRONT" and not wh.get("serving_central_wh_key"):
                 st.error(f"❌ Validation Error: Serving MAIN warehouse is not selected for FRONT Warehouse {i+1} ({wh.get('location', 'N/A')}).")
                 config_complete = False

            all_markets_served.update(wh.get("served_markets", []))
            final_warehouse_list_for_calc.append(wh)

        unserved_markets = set(selected_market_areas) - all_markets_served
        if unserved_markets:
            st.error(f"❌ Validation Error: The following selected market areas are not served by any warehouse: {', '.join(sorted(list(unserved_markets)))}")
            config_complete = False

        if config_complete:
            st.success("✅ All warehouse configurations seem complete and valid based on initial checks.")
            warehouse_data = final_warehouse_list_for_calc
        else:
             st.warning("⚠️ Please review the errors above before proceeding to calculations.")
             warehouse_data = []
    # --- UI Enhancement End ---


# =====================================================
# Helper Functions (Global – Used in Calculations)
# - No logic changes made here as requested -
# =====================================================
# (Helper functions remain unchanged from the previous version)
def compute_annual_forecast_for_area(area, market_data):
    """Calculates total annual forecast demand for a specific market area."""
    total = 0
    if area in market_data:
        for brand, params in market_data[area].items():
            total += sum(params.get("forecast_demand", [0])) # Use .get for safety
    return total

def compute_max_monthly_forecast_for_area(area, market_data):
    """Calculates the peak monthly forecast demand across all brands for a specific market area."""
    max_m = 0
    if area in market_data:
        # Ensure forecast data exists and has 12 months for all brands
        min_len = min(len(params.get("forecast_demand", [])) for params in market_data[area].values())
        if min_len == 12:
            for m in range(12):
                month_sum = sum(params["forecast_demand"][m] for params in market_data[area].values())
                max_m = max(max_m, month_sum)
        else: # Handle case where forecast might be incomplete (though UI should prevent this)
             # Find the max value across all available forecasts as a fallback
             max_per_brand = [max(params.get("forecast_demand", [0])) for params in market_data[area].values()]
             max_m = sum(max_per_brand) # Sum of peaks is a rough upper bound
             # st.warning(f"Incomplete forecast data for area {area}. Max monthly calculation might be inaccurate.")
    return max_m


def compute_std_sum_for_area(area, market_data):
    """Calculates the sum of standard deviations of daily demand for a specific market area."""
    total_std = 0
    if area in market_data:
        for params in market_data[area].values():
            total_std += params.get("std_daily_demand", 0)
    return total_std

def compute_daily_demand_sum_for_area(area, market_data):
    """Calculates the sum of average daily demand across all brands for a specific market area."""
    total = 0
    if area in market_data:
        for params in market_data[area].values():
            total += params.get("avg_daily_demand", 0)
    return total

def compute_max_monthly_forecast(warehouse, market_data):
    """Calculates the peak monthly forecast demand across all markets served by a warehouse."""
    max_monthly = 0
    for area in warehouse.get("served_markets", []):
        area_max = compute_max_monthly_forecast_for_area(area, market_data)
        max_monthly = max(max_monthly, area_max)
    return max_monthly

def compute_daily_demand_sum(warehouse, market_data):
    """Calculates the total average daily demand across all markets served by a warehouse."""
    total = 0
    for area in warehouse.get("served_markets", []):
        total += compute_daily_demand_sum_for_area(area, market_data)
    return total

def compute_annual_demand(warehouse, market_data):
    """Calculates the total annual forecast demand across all markets served by a warehouse."""
    total = 0
    for area in warehouse.get("served_markets", []):
        total += compute_annual_forecast_for_area(area, market_data)
    return total

def compute_std_sum(warehouse, market_data):
    """Calculates the total standard deviation of daily demand across all markets served by a warehouse."""
    total = 0
    for area in warehouse.get("served_markets", []):
        total += compute_std_sum_for_area(area, market_data)
    return total

def compute_safety_stock_main(warehouse, market_data, Z_val, layout, all_warehouses):
    """Calculates safety stock for a MAIN warehouse."""
    std_sum = compute_std_sum(warehouse, market_data)
    LT = warehouse.get("lt_shipping", 0) # Lead time from source
    safety_stock_main = std_sum * sqrt(LT) * Z_val if LT > 0 else 0 # Avoid sqrt(0)

    # Add demand during transfer lead time for FRONT warehouses it serves
    if layout == "Central and Fronts":
        # Find FRONT warehouses served by *this* MAIN warehouse
        # Need to reconstruct the link based on the stored label
        # Ensure warehouse is in all_warehouses before trying index
        try:
            warehouse_index = all_warehouses.index(warehouse)
            serving_label = f"WH {warehouse_index+1} ({warehouse.get('location')})" # Recreate the label this MAIN WH would have
            front_daily_demand = sum(
                compute_daily_demand_sum(front_wh, market_data)
                for front_wh in all_warehouses
                if front_wh.get("type") == "FRONT" and front_wh.get("serving_central_wh_key") == serving_label
            )
            # Assuming a fixed transfer lead time (e.g., 12 days - could be made configurable)
            transfer_lead_time = 12
            safety_stock_main += transfer_lead_time * front_daily_demand
        except ValueError:
            # This MAIN warehouse somehow isn't in the list passed, should not happen in normal flow
             st.error("Internal error: Could not find MAIN warehouse in list during safety stock calculation.")


    return safety_stock_main

def compute_inventory_breakdown(warehouse, market_data, interest_rt, brand_prices, Z_val, layout, all_warehouses):
    """Calculates inventory metrics (safety stock, avg inventory, financing cost) broken down by brand for a MAIN warehouse."""
    LT = warehouse.get("lt_shipping", 0)
    breakdown = {brand: {"annual_forecast": 0, "std_sum": 0, "avg_daily_demand": 0} for brand in BRANDS}

    # Aggregate base demand from directly served markets
    for area in warehouse.get("served_markets", []):
        if area in market_data:
            for brand, params in market_data[area].items():
                breakdown[brand]["annual_forecast"] += sum(params.get("forecast_demand", [0]))
                breakdown[brand]["std_sum"] += params.get("std_daily_demand", 0)
                breakdown[brand]["avg_daily_demand"] += params.get("avg_daily_demand", 0)

    # Add demand from served FRONT warehouses (only for Central and Fronts layout)
    front_contrib = {brand: 0 for brand in BRANDS}
    if layout == "Central and Fronts":
         # Find FRONT warehouses served by *this* MAIN warehouse
        try:
             warehouse_index = all_warehouses.index(warehouse)
             serving_label = f"WH {warehouse_index+1} ({warehouse.get('location')})"
             for front_wh in all_warehouses:
                 if front_wh.get("type") == "FRONT" and front_wh.get("serving_central_wh_key") == serving_label:
                     for area in front_wh.get("served_markets", []):
                         if area in market_data:
                             for brand, params in market_data[area].items():
                                 front_contrib[brand] += params.get("avg_daily_demand", 0)
        except ValueError:
            st.error("Internal error: Could not find MAIN warehouse in list during inventory breakdown calculation.")


    # Calculate metrics for each brand
    results = {}
    for brand in BRANDS:
        # Safety Stock = Z * sqrt(LT) * StDev + (TransferLT * DailyDemand_Fronts)
        transfer_lead_time = 12 # Assumed, could be parameter
        safety_stock = (breakdown[brand]["std_sum"] * sqrt(LT) * Z_val if LT > 0 else 0) + \
                       (transfer_lead_time * front_contrib[brand])

        # Average Inventory = Cycle Stock (Avg Monthly Demand or EOQ based) + Safety Stock
        # Using Avg Monthly Demand as proxy for Cycle Stock for simplicity here
        avg_monthly_demand = breakdown[brand]["annual_forecast"] / 12.0 if breakdown[brand]["annual_forecast"] else 0
        avg_inventory = avg_monthly_demand + safety_stock

        unit_price = brand_prices.get(brand, 0)
        # Financing Cost = Avg Inventory Value * Interest Rate * Overhead Factor (e.g., 1.08)
        financing_cost = avg_inventory * 1.08 * (interest_rt / 100.0) * unit_price

        results[brand] = {
            "annual_forecast": breakdown[brand]["annual_forecast"],
            "safety_stock": safety_stock,
            "avg_inventory": avg_inventory,
            "financing_cost": financing_cost
        }
    return results


# =====================================================
# TAB 2: Calculations – Rental, Inventory, Shipping & Labor
# =====================================================
with tab_calculations:
    # --- Headers using markdown (already correct) ---
    st.markdown("<p class='section-header-font'><i class='fas fa-cogs icon'></i>Calculate Network Costs</p>", unsafe_allow_html=True)
    st.info("ℹ️ Click the buttons below to calculate each cost component based on the setup data. Results will be stored and summarized.")

    if not warehouse_data:
         st.error("❌ Cannot perform calculations. Please complete the warehouse setup in the 'Setup Configuration' tab and resolve any validation errors.")
    else:
        # --- UI Enhancement Start ---
        calc_col1, calc_col2 = st.columns(2)

        with calc_col1:
             # --- Rental Cost Calculation ---
             with st.container(border=True):
                 # --- Headers using markdown (already correct) ---
                 st.markdown("<p class='sub-header-font'><i class='fas fa-building icon'></i>Rental Costs</p>", unsafe_allow_html=True)
                 # --- Button label is simple text - okay ---
                 if st.button("Calculate Rental Costs", key="calc_rental", type="primary"):
                     with st.spinner("Calculating Rental Costs..."):
                        time.sleep(0.5)
                        rental_details = []
                        total_rental_cost = 0.0
                        valid_input = True
                        for i, wh in enumerate(warehouse_data):
                            rent_method = wh["rent_pricing_method"]
                            rent_price = wh["rent_price"]
                            wh_type = wh["type"]
                            wh_area = 0.0
                            wh_rental_cost = 0.0
                            calculated_units = 0.0

                            if rent_method == "Fixed Rent Price":
                                wh_rental_cost = rent_price
                                wh_area = "N/A (Fixed)"
                            else:
                                overhead = overhead_factor_main if wh_type == "MAIN" else overhead_factor_front
                                if sq_ft_per_unit <= 0:
                                     st.error(f"Sq Ft per Unit must be positive. Check Rental Parameters.")
                                     valid_input = False
                                     break
                                if rent_price <= 0:
                                     st.error(f"Sq Ft Rent Price must be positive for Warehouse {i+1} ({wh.get('location')}).")
                                     valid_input = False
                                     break

                                max_monthly = compute_max_monthly_forecast(wh, market_area_data)

                                if wh_type == "MAIN":
                                    safety_stock_main = compute_safety_stock_main(wh, market_area_data, Z_value, layout_type, warehouse_data)
                                    calculated_units = max_monthly + safety_stock_main
                                else: # FRONT
                                    daily_sum = compute_daily_demand_sum(wh, market_area_data)
                                    calculated_units = (max_monthly / 4.0) + (daily_sum * 12.0)

                                wh_area = sq_ft_per_unit * overhead * calculated_units
                                wh_rental_cost = rent_price * wh_area

                            rental_details.append({
                                "Warehouse": f"WH {i+1} ({wh.get('location')})",
                                "Type": wh_type,
                                "Pricing Method": rent_method,
                                "Est. Sq Ft": f"{wh_area:.0f}" if isinstance(wh_area, (int, float)) else wh_area,
                                "Annual Rent ($)": f"{wh_rental_cost:.0f}"
                            })
                            total_rental_cost += wh_rental_cost

                        if valid_input:
                            st.session_state.total_rental_cost = total_rental_cost
                            st.session_state.rental_details_df = pd.DataFrame(rental_details)
                            st.session_state.rental_costs_calculated = True
                            st.success("Rental Costs Calculated!")
                        else:
                             st.session_state.rental_costs_calculated = False

                 if st.session_state.rental_costs_calculated:
                     st.metric("Total Annual Rental Cost", f"${st.session_state.total_rental_cost:,.0f}")
                     st.dataframe(st.session_state.rental_details_df, use_container_width=True, hide_index=True)
                 else:
                      st.info("Rental cost results will appear here after calculation.")


             st.divider()
             # --- Shipping Cost Calculation ---
             with st.container(border=True):
                 # --- Headers using markdown (already correct) ---
                 st.markdown("<p class='sub-header-font'><i class='fas fa-truck-loading icon'></i>Shipping Costs</p>", unsafe_allow_html=True)
                 # --- Button label is simple text - okay ---
                 if st.button("Calculate Shipping Costs", key="calc_shipping", type="primary"):
                     with st.spinner("Calculating Shipping Costs..."):
                        time.sleep(0.5)
                        shipping_details = []
                        total_shipping_cost = 0.0
                        valid_input = True

                        if container_capacity_40 <= 0:
                             st.error("Container Capacity (40ft HC) must be positive. Check Global Settings.")
                             valid_input = False

                        for i, wh in enumerate(warehouse_data):
                             if not valid_input: break # Stop loop if error
                             annual_demand_wh = compute_annual_demand(wh, market_area_data)
                             wh_shipping_cost = 0.0
                             shipment_type = "N/A"

                             if wh["type"] == "MAIN":
                                 cost_per_40hc = wh.get("shipping_cost_40hc", 0)
                                 if cost_per_40hc <= 0 and annual_demand_wh > 0: # Only require cost if there's demand
                                     st.error(f"International Shipping Cost for WH {i+1} ({wh['location']}) must be positive if demand exists.")
                                     valid_input = False
                                     break
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
                                         elif area_annual_demand > 0 and cost_per_avg_order <= 0:
                                             st.warning(f"Missing or zero regional shipping cost for {area} from {wh['location']}. Calculation may be incomplete.")

                                     wh_shipping_cost += regional_land_cost
                                     shipment_type += f" + Regional ({regional_land_cost:,.0f}$)"


                             elif wh["type"] == "FRONT":
                                 cost_per_53ft = wh.get("front_shipping_cost_53", 0)
                                 truck_capacity = container_capacity_40 * 1.3
                                 if cost_per_53ft <= 0 and annual_demand_wh > 0:
                                     st.error(f"Transfer Shipping Cost (53ft) for WH {i+1} ({wh['location']}) must be positive if demand exists.")
                                     valid_input = False
                                     break
                                 num_trucks = ceil(annual_demand_wh / truck_capacity) if truck_capacity > 0 else 0
                                 wh_shipping_cost = num_trucks * cost_per_53ft
                                 shipment_type = f"{num_trucks} x 53ft Transfer"

                             shipping_details.append({
                                "Warehouse": f"WH {i+1} ({wh.get('location')})",
                                "Type": wh["type"],
                                "Annual Demand (Units)": f"{annual_demand_wh:,.0f}",
                                "Est. Shipments": shipment_type,
                                "Annual Shipping Cost ($)": f"{wh_shipping_cost:,.0f}"
                             })
                             total_shipping_cost += wh_shipping_cost

                        if valid_input:
                            st.session_state.total_shipping_cost = total_shipping_cost
                            st.session_state.shipping_details_df = pd.DataFrame(shipping_details)
                            st.session_state.shipping_costs_calculated = True
                            st.success("Shipping Costs Calculated!")
                        else:
                             st.session_state.shipping_costs_calculated = False

                 if st.session_state.shipping_costs_calculated:
                     st.metric("Total Annual Shipping Cost", f"${st.session_state.total_shipping_cost:,.0f}")
                     st.dataframe(st.session_state.shipping_details_df, use_container_width=True, hide_index=True)
                 else:
                     st.info("Shipping cost results will appear here after calculation.")

        with calc_col2:
             # --- Inventory Financing Calculation ---
             with st.container(border=True):
                 # --- Headers using markdown (already correct) ---
                 st.markdown("<p class='sub-header-font'><i class='fas fa-coins icon'></i>Inventory Financing Costs</p>", unsafe_allow_html=True)
                 # --- Button label is simple text - okay ---
                 if st.button("Calculate Inventory Financing", key="calc_inventory", type="primary"):
                     with st.spinner("Calculating Inventory Financing..."):
                        time.sleep(0.5)
                        inventory_details = []
                        total_inventory_financing_cost = 0.0
                        total_avg_inventory_units = 0.0
                        total_safety_stock_units = 0.0
                        valid_input = True

                        if interest_rate < 0 or service_level < 0:
                             st.error("Interest Rate and Service Level must be non-negative. Check Global Settings.")
                             valid_input = False
                        if any(p <= 0 for p in brand_unit_prices.values()):
                             st.error("All Brand Unit Prices must be positive. Check Setup Tab.")
                             valid_input = False

                        if layout_type == "Central and Fronts":
                            main_wh_list = [wh for wh in warehouse_data if wh["type"] == "MAIN"]
                            if len(main_wh_list) != 1: # Check exactly one MAIN WH exists
                                st.error("Exactly one MAIN warehouse must be configured for 'Central and Fronts' layout. Check Setup.")
                                valid_input = False
                            elif valid_input:
                                main_wh = main_wh_list[0]
                                breakdown = compute_inventory_breakdown(main_wh, market_area_data, interest_rate, brand_unit_prices, Z_value, layout_type, warehouse_data)
                                for brand, bdata in breakdown.items():
                                     inventory_details.append({
                                        "Warehouse": f"WH {warehouse_data.index(main_wh)+1} ({main_wh.get('location')})",
                                        "Brand": brand,
                                        "Safety Stock (Units)": f"{bdata['safety_stock']:.0f}",
                                        "Avg Inventory (Units)": f"{bdata['avg_inventory']:.0f}",
                                        "Annual Financing Cost ($)": f"{bdata['financing_cost']:.0f}"
                                    })
                                     total_inventory_financing_cost += bdata['financing_cost']
                                     total_avg_inventory_units += bdata['avg_inventory']
                                     total_safety_stock_units += bdata['safety_stock']

                        elif layout_type == "Main Regionals":
                             for i, wh in enumerate(warehouse_data):
                                 if wh["type"] == "MAIN" and valid_input:
                                     breakdown = compute_inventory_breakdown(wh, market_area_data, interest_rate, brand_unit_prices, Z_value, layout_type, warehouse_data)
                                     for brand, bdata in breakdown.items():
                                         inventory_details.append({
                                            "Warehouse": f"WH {i+1} ({wh.get('location')})",
                                            "Brand": brand,
                                            "Safety Stock (Units)": f"{bdata['safety_stock']:.0f}",
                                            "Avg Inventory (Units)": f"{bdata['avg_inventory']:.0f}",
                                            "Annual Financing Cost ($)": f"{bdata['financing_cost']:.0f}"
                                        })
                                         total_inventory_financing_cost += bdata['financing_cost']
                                         total_avg_inventory_units += bdata['avg_inventory']
                                         total_safety_stock_units += bdata['safety_stock']

                        if valid_input:
                             st.session_state.total_inventory_financing_cost = total_inventory_financing_cost
                             st.session_state.inventory_details_df = pd.DataFrame(inventory_details)
                             st.session_state.aggregated_inventory_metrics = {
                                 "Total Avg Inventory (Units)": total_avg_inventory_units,
                                 "Total Safety Stock (Units)": total_safety_stock_units
                             }
                             st.session_state.inventory_costs_calculated = True
                             st.success("Inventory Financing Costs Calculated!")
                        else:
                             st.session_state.inventory_costs_calculated = False


                 if st.session_state.inventory_costs_calculated:
                      col_inv1, col_inv2, col_inv3 = st.columns(3)
                      with col_inv1:
                          st.metric("Total Annual Financing Cost", f"${st.session_state.total_inventory_financing_cost:,.0f}")
                      with col_inv2:
                          st.metric("Total Avg Inventory", f"{st.session_state.aggregated_inventory_metrics['Total Avg Inventory (Units)']:,.0f} Units")
                      with col_inv3:
                          st.metric("Total Safety Stock", f"{st.session_state.aggregated_inventory_metrics['Total Safety Stock (Units)']:,.0f} Units")

                      st.dataframe(st.session_state.inventory_details_df, use_container_width=True, hide_index=True)

                      if not st.session_state.inventory_details_df.empty:
                           df_chart = st.session_state.inventory_details_df.copy()
                           df_chart['Annual Financing Cost ($)'] = df_chart['Annual Financing Cost ($)'].str.replace('[$,]', '', regex=True).astype(float)
                           brand_costs = df_chart.groupby('Brand')['Annual Financing Cost ($)'].sum().reset_index()

                           fig_inv = px.bar(brand_costs, x='Brand', y='Annual Financing Cost ($)',
                                          title="Annual Inventory Financing Cost by Brand",
                                          text_auto='.2s',
                                          labels={'Annual Financing Cost ($)': 'Annual Financing Cost ($)'})
                           fig_inv.update_layout(yaxis_title="Annual Financing Cost ($)", xaxis_title="Brand", title_x=0.5)
                           fig_inv.update_traces(textposition='outside')
                           st.plotly_chart(fig_inv, use_container_width=True)

                 else:
                     st.info("Inventory financing results will appear here after calculation.")

             st.divider()
             # --- Labor Cost Calculation ---
             with st.container(border=True):
                # --- Headers using markdown (already correct) ---
                st.markdown("<p class='sub-header-font'><i class='fas fa-users icon'></i>Labor Costs</p>", unsafe_allow_html=True)
                # --- Button label is simple text - okay ---
                if st.button("Calculate Labor Costs", key="calc_labor", type="primary"):
                    with st.spinner("Calculating Labor Costs..."):
                        time.sleep(0.5)
                        labor_details = []
                        total_labor_cost = 0.0
                        valid_input = True

                        for i, wh in enumerate(warehouse_data):
                            num_emp = wh.get("num_employees", 0)
                            salary = wh.get("avg_employee_salary", 0)

                            if num_emp < 0 or salary < 0:
                                st.error(f"Number of employees and salary must be non-negative for Warehouse {i+1} ({wh.get('location')}).")
                                valid_input = False
                                break

                            wh_labor_cost = num_emp * salary
                            labor_details.append({
                                "Warehouse": f"WH {i+1} ({wh.get('location')})",
                                "Type": wh["type"],
                                "# Employees": num_emp,
                                "Avg Salary ($)": f"{salary:,.0f}",
                                "Annual Labor Cost ($)": f"{wh_labor_cost:,.0f}"
                            })
                            total_labor_cost += wh_labor_cost

                        if valid_input:
                            st.session_state.total_labor_cost = total_labor_cost
                            st.session_state.labor_details_df = pd.DataFrame(labor_details)
                            st.session_state.labor_costs_calculated = True
                            st.success("Labor Costs Calculated!")
                        else:
                            st.session_state.labor_costs_calculated = False

                if st.session_state.labor_costs_calculated:
                    st.metric("Total Annual Labor Cost", f"${st.session_state.total_labor_cost:,.0f}")
                    st.dataframe(st.session_state.labor_details_df, use_container_width=True, hide_index=True)
                else:
                     st.info("Labor cost results will appear here after calculation.")
        # --- UI Enhancement End ---

# =====================================================
# TAB 3: Submission / Summary - Changed to Summary
# =====================================================
# --- UI Enhancement Start ---
with tab_summary:
    # --- Headers using markdown (already correct) ---
    st.markdown("<p class='section-header-font'><i class='fas fa-chart-pie icon'></i>Scenario Cost Summary</p>", unsafe_allow_html=True)

    all_calculated = (st.session_state.rental_costs_calculated and
                      st.session_state.inventory_costs_calculated and
                      st.session_state.shipping_costs_calculated and
                      st.session_state.labor_costs_calculated)

    if not all_calculated:
        st.warning("⚠️ Please calculate all cost components in the 'Run Calculations' tab to see the full summary.")
    else:
        st.session_state.grand_total = (st.session_state.total_rental_cost +
                                         st.session_state.total_inventory_financing_cost +
                                         st.session_state.total_shipping_cost +
                                         st.session_state.total_labor_cost)

        st.markdown("### Total Estimated Annual Costs")
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        # Metric labels are simple text - okay
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

        st.markdown("---")
        st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
        # --- Headers using markdown (already correct) ---
        st.markdown(f"<h2 style='color: #1E3A5F;'>Grand Total Annual Cost: ${st.session_state.grand_total:,.0f}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")


        # --- Cost Breakdown Visualization ---
        st.markdown("### Cost Component Breakdown")
        cost_data = {
            'Cost Component': ['Rental', 'Inventory Financing', 'Shipping', 'Labor'],
            'Cost ($)': [st.session_state.total_rental_cost,
                         st.session_state.total_inventory_financing_cost,
                         st.session_state.total_shipping_cost,
                         st.session_state.total_labor_cost]
        }
        cost_df = pd.DataFrame(cost_data)
        cost_df = cost_df[cost_df['Cost ($)'] > 0]

        if not cost_df.empty:
            fig_pie = px.pie(cost_df, values='Cost ($)', names='Cost Component',
                             title='Distribution of Annual Costs', hole=0.3,
                             color_discrete_sequence=px.colors.Sequential.Blues_r)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent+value')
            fig_pie.update_layout(title_x=0.5, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No cost data to display in the chart.")


        # --- Warehouse Level Summary ---
        st.markdown("### Summary per Warehouse (Combined Costs)")
        summary_list = []
        # Need valid warehouse_data list from setup tab for this section
        valid_wh_data_for_summary = warehouse_data if config_complete else [] # Use the validated list

        for i, wh in enumerate(valid_wh_data_for_summary):
             wh_label = f"WH {i+1} ({wh.get('location')})"
             wh_summary = {"Warehouse": wh_label, "Type": wh.get("type")} # Use 'type' from original config

             rental_cost = 0.0
             if not st.session_state.rental_details_df.empty:
                 rent_row = st.session_state.rental_details_df[st.session_state.rental_details_df['Warehouse'] == wh_label]
                 if not rent_row.empty:
                     try: rental_cost = float(rent_row.iloc[0]['Annual Rent ($)'].replace(',', ''))
                     except: pass # Keep 0 if conversion fails
             wh_summary["Rental ($)"] = f"{rental_cost:,.0f}"

             inv_cost = 0.0
             if not st.session_state.inventory_details_df.empty:
                  inv_rows = st.session_state.inventory_details_df[st.session_state.inventory_details_df['Warehouse'] == wh_label]
                  if not inv_rows.empty:
                       try: inv_cost = inv_rows['Annual Financing Cost ($)'].str.replace('[$,]', '', regex=True).astype(float).sum()
                       except: pass
             wh_summary["Inventory ($)"] = f"{inv_cost:,.0f}"

             ship_cost = 0.0
             if not st.session_state.shipping_details_df.empty:
                 ship_row = st.session_state.shipping_details_df[st.session_state.shipping_details_df['Warehouse'] == wh_label]
                 if not ship_row.empty:
                      try: ship_cost = float(ship_row.iloc[0]['Annual Shipping Cost ($)'].replace(',', ''))
                      except: pass
             wh_summary["Shipping ($)"] = f"{ship_cost:,.0f}"

             labor_cost = 0.0
             if not st.session_state.labor_details_df.empty:
                 labor_row = st.session_state.labor_details_df[st.session_state.labor_details_df['Warehouse'] == wh_label]
                 if not labor_row.empty:
                      try: labor_cost = float(labor_row.iloc[0]['Annual Labor Cost ($)'].replace(',', ''))
                      except: pass
             wh_summary["Labor ($)"] = f"{labor_cost:,.0f}"

             wh_summary["Total ($)"] = f"{(rental_cost + inv_cost + ship_cost + labor_cost):,.0f}"
             summary_list.append(wh_summary)

        if summary_list:
             summary_df = pd.DataFrame(summary_list)
             st.dataframe(summary_df, hide_index=True, use_container_width=True)
        elif config_complete: # Only show info if config was valid but table empty
             st.info("Warehouse summary data not available (costs might be zero or calculation needed).")


        # --- Placeholder for Submission/Export ---
        st.markdown("---")
        st.markdown("### Actions")
        # --- Fix: Use markdown for button icon ---
        # Button labels generally don't render HTML well. Keep it simple or use markdown above.
        # st.markdown("<p class='widget-label'><i class='fas fa-file-export icon'></i> Generate Report / Submit Scenario</p>", unsafe_allow_html=True) # Optional markdown label
        if st.button("Generate Report / Submit Scenario", type="primary"):
            st.success("Scenario data processed! (Report generation/submission functionality not implemented in this demo)")
            # Example: Export summary_df.to_csv("scenario_summary.csv")
            # if 'summary_df' in locals():
            #      st.dataframe(summary_df) # Display summary df again or export

# --- UI Enhancement End ---