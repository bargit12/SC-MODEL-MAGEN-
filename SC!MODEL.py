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
    page_icon="🚚",
    layout="wide"
)

# --- UI Enhancement Start ---
st.markdown(
    """
    <head>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.2.0/css/all.min.css">
    </head>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
        html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
        .main-header-font { font-size: 36px !important; font-weight: 700; color: #1E3A5F; text-align: center; margin-bottom: 30px; padding-top: 20px; }
        .section-header-font { font-size: 26px !important; font-weight: 700; color: #2C3E50; margin-top: 30px; margin-bottom: 15px; border-bottom: 2px solid #3498DB; padding-bottom: 5px; }
        .sub-header-font { font-size: 20px !important; font-weight: 500; color: #34495E; margin-top: 15px; margin-bottom: 10px; }
        .input-card { background-color: #FFFFFF; padding: 25px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px; border: 1px solid #EAECEE; }
        .stExpander { border: 1px solid #EAECEE !important; border-radius: 8px !important; margin-bottom: 15px !important; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        .stExpander header { font-weight: 500; font-size: 18px; background-color: #F8F9F9; border-radius: 8px 8px 0 0 !important; padding: 10px 15px !important; }
        .stExpander header:hover { background-color: #E8F6F3; }
        .metric-card { background-color: #FFFFFF; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; border: 1px solid #EAECEE; }
        .metric-card .stMetric { background-color: transparent !important; border: none !important; padding: 0 !important; }
        .metric-card label { font-weight: 500; color: #566573; }
        .metric-card p { font-size: 24px !important; font-weight: 700; color: #1A5276; }
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #F0F2F6; border-radius: 8px 8px 0px 0px; gap: 1px; padding-top: 10px; padding-bottom: 10px; font-weight: 500; }
        .stTabs [aria-selected="true"] { background-color: #FFFFFF; color: #3498DB; font-weight: 700; border-bottom: 3px solid #3498DB; }
        .stButton>button { background-color: #3498DB; color: white; padding: 10px 20px; border-radius: 5px; border: none; font-weight: 500; transition: background-color 0.3s ease; }
        .stButton>button:hover { background-color: #2874A6; color: white; }
        .stButton>button:focus { box-shadow: 0 0 0 2px #AED6F1 !important; background-color: #2E86C1; color: white; }
        .icon { margin-right: 8px; color: #5D6D7E; }
        .widget-label { font-weight: 500; margin-bottom: -5px; color: #34495E; }
    </style>
    """,
    unsafe_allow_html=True
)
# --- UI Enhancement End ---

st.markdown("<p class='main-header-font'><i class='fas fa-cogs icon'></i>Supply Chain & Warehouse Network Optimization</p>", unsafe_allow_html=True)

# -------------------------
# Sidebar: Global Parameters
# -------------------------
with st.sidebar:
    st.markdown("## <i class='fas fa-globe icon'></i> Global Settings", unsafe_allow_html=True)
    st.divider()
    st.markdown("<p class='widget-label'><i class='fas fa-percentage icon'></i> Actual Interest Rate (%)</p>", unsafe_allow_html=True)
    interest_rate = st.number_input("", min_value=0.0, max_value=100.0, value=5.0, step=0.1, help="Enter the annual interest rate.", label_visibility="collapsed")
    st.markdown("<p class='widget-label'><i class='fas fa-shield-alt icon'></i> Required Service Level (0-1)</p>", unsafe_allow_html=True)
    service_level = st.slider("", min_value=0.0, max_value=1.0, value=0.95, help="Set desired service level.", label_visibility="collapsed")
    st.divider()
    st.markdown("<p class='widget-label'><i class='fas fa-warehouse icon'></i> Layout Type</p>", unsafe_allow_html=True)
    layout_type = st.radio("", options=["Central and Fronts", "Main Regionals"], help="Select network structure.", key="layout_type_radio", horizontal=True, label_visibility="collapsed")
    if layout_type == "Main Regionals":
        st.info("ℹ️ In 'Main Regionals', all warehouses act as MAIN.")
    else:
        st.info("ℹ️ In 'Central and Fronts', define one MAIN and any number of FRONT warehouses.")
    st.divider()
    st.markdown("### <i class='fas fa-box-open icon'></i> Container Capacity", unsafe_allow_html=True)
    container_capacity_40 = st.number_input("Capacity for 40ft HC (Units)", min_value=1, value=600, step=1, format="%d", help="Number of units fitting in a 40ft HC container.")

# Compute Z_value
if service_level >= 1.0:
    Z_value = 5
elif service_level <= 0.0:
    Z_value = -5
else:
    Z_value = norm.ppf(service_level)

# -------------------------
# Main App Tabs
# -------------------------
tab_setup, tab_calculations, tab_summary = st.tabs(["Setup Configuration", "Run Calculations", "Results Summary"])

# =====================================================
# TAB 1: Setup – Inputs for Brands, Rental, Markets & Warehouses
# =====================================================
with tab_setup:
    st.markdown("<p class='section-header-font'><i class='fas fa-edit icon'></i>Define Your Network Parameters</p>", unsafe_allow_html=True)
    col_setup_1, col_setup_2 = st.columns(2)
    with col_setup_1:
        with st.container(border=True):
             st.markdown("<p class='sub-header-font'><i class='fas fa-tags icon'></i>Brand Pricing</p>", unsafe_allow_html=True)
             BRANDS = ["Heliocol", "SunStar", "SunValue"]
             brand_unit_prices = {}
             brand_cols = st.columns(len(BRANDS))
             for idx, brand in enumerate(BRANDS):
                 with brand_cols[idx]:
                     brand_unit_prices[brand] = st.number_input(
                         f"Unit Price ({brand})",
                         min_value=0.0,
                         value=80.0,
                         step=1.0,
                         help=f"Price per unit (4 panels) for {brand}.",
                         key=f"{brand}_unit_price"
                     )
    with col_setup_2:
         with st.container(border=True):
            st.markdown("<p class='sub-header-font'><i class='fas fa-ruler-combined icon'></i>Rental Parameters</p>", unsafe_allow_html=True)
            rent_cols = st.columns(3)
            with rent_cols[0]:
                sq_ft_per_unit = st.number_input("Sq Ft per Unit", min_value=0.1, value=0.8, step=0.1, format="%.1f", help="Square feet required for one unit.")
            with rent_cols[1]:
                overhead_factor_main = st.number_input("Overhead (MAIN)", min_value=1.0, value=1.2, step=0.1, format="%.1f", help="Overhead factor for MAIN warehouses.")
            with rent_cols[2]:
                 overhead_factor_front = st.number_input("Overhead (FRONT)", min_value=1.0, value=1.5, step=0.1, format="%.1f", help="Overhead factor for FRONT warehouses.")
    st.markdown("<p class='section-header-font'><i class='fas fa-map-marker-alt icon'></i>Market Areas Setup</p>", unsafe_allow_html=True)
    with st.container(border=True):
        base_market_areas = ["FL", "CA_SOUTH", "CA_NORTH", "TX", "NJ"]
        st.write("Standard market areas:", ", ".join(base_market_areas))
        custom_market_areas_str = st.text_input("Enter additional market areas (comma separated)", value="", help="E.g., NY, PA, OH")
        custom_market_areas = [area.strip().upper() for area in custom_market_areas_str.split(",") if area.strip() != ""]
        all_market_areas = sorted(list(dict.fromkeys(base_market_areas + custom_market_areas)))
        selected_market_areas = st.multiselect("Select Market Areas to Include", options=all_market_areas, default=all_market_areas, help="Choose market areas to use.")
        market_area_data = {}
        if not selected_market_areas:
            st.warning("Please select at least one market area.")
        else:
            st.markdown("<p class='sub-header-font'>Configure Parameters for Selected Market Areas:</p>", unsafe_allow_html=True)
            for area in selected_market_areas:
                 with st.expander(f"Parameters for Market Area: {area}", expanded=False):
                    # Allow user to choose active brands in the area
                    active_brands = st.multiselect(f"Select Active Brands for {area}", options=BRANDS, default=BRANDS, key=f"{area}_active_brands")
                    brand_data = {}
                    for brand in active_brands:
                        st.markdown(f"**Brand: {brand}**")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            avg_order_size = st.number_input(f"Avg Order Size", min_value=0, value=100, step=1, format="%d", key=f"{area}_{brand}_avg_order_size", help=f"Typical order size for {brand} in {area}.")
                        with col2:
                            avg_daily_demand = st.number_input(f"Avg Daily Demand", min_value=0, value=50, step=1, format="%d", key=f"{area}_{brand}_avg_daily_demand", help=f"Average daily demand for {brand} in {area}.")
                        with col3:
                            std_daily_demand = st.number_input(f"Std Dev Daily Demand", min_value=0.0, value=10.0, step=1.0, key=f"{area}_{brand}_std_daily_demand", help=f"Demand volatility for {brand} in {area}.")
                        st.markdown(f"**12-Month Forecast Demand ({brand} - {area})**", unsafe_allow_html=True)
                        forecast = []
                        forecast_cols = st.columns(6)
                        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                        for m in range(12):
                            with forecast_cols[m % 6]:
                                val = st.number_input(f"{months[m]}", min_value=0, value=500, step=1, format="%d", key=f"{area}_{brand}_forecast_{m}", help=f"Forecast for {brand} in {area} for {months[m]}.")
                                forecast.append(val)
                        st.divider()
                        brand_data[brand] = {
                            "avg_order_size": avg_order_size,
                            "avg_daily_demand": avg_daily_demand,
                            "std_daily_demand": std_daily_demand,
                            "forecast_demand": forecast
                        }
                    market_area_data[area] = brand_data
    st.markdown("<p class='section-header-font'><i class='fas fa-industry icon'></i>Warehouse Setup</p>", unsafe_allow_html=True)
    with st.container(border=True):
        base_warehouse_locations = ["FL", "CA_SOUTH", "CA_NORTH", "TX", "NJ"]
        st.write("Standard potential warehouse locations:", ", ".join(base_market_areas))
        custom_warehouse_locations_str = st.text_input("Enter additional warehouse locations (comma separated)", value="", key="warehouse_locations_text", help="E.g., NY, PA")
        custom_warehouse_locations = [loc.strip().upper() for loc in custom_warehouse_locations_str.split(",") if loc.strip() != ""]
        all_warehouse_locations = sorted(list(dict.fromkeys(base_warehouse_locations + custom_warehouse_locations)))
        num_warehouses = st.number_input("Number of Warehouses to Configure", min_value=1, value=1, step=1, help="Enter total warehouses in this scenario.")
        warehouse_data = []
        temp_warehouse_configs = {}
        st.markdown("<p class='sub-header-font'>Configure Parameters for Each Warehouse:</p>", unsafe_allow_html=True)
        for i in range(int(num_warehouses)):
             with st.expander(f"Warehouse {i+1} Configuration", expanded=True if num_warehouses <= 2 else False):
                wh_config = {}
                col_loc, col_type = st.columns(2)
                with col_loc:
                    location = st.selectbox(f"Location (WH {i+1})", options=[""] + all_warehouse_locations, index=0, key=f"wh_location_{i}", help="Choose warehouse location.")
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
                             wh_type = st.radio(f"Type (WH {i+1})", options=options, key=f"wh_type_{i}", horizontal=True, help="Select MAIN or FRONT.")
                    wh_config["type"] = wh_type
                served_markets = st.multiselect(f"Market Areas Served by Warehouse {i+1}", options=selected_market_areas, key=f"wh_markets_{i}", help="Select served market areas.")
                wh_config["served_markets"] = served_markets
                if location and location not in served_markets:
                    st.error(f"Warehouse {i+1} location '{location}' must be included in its served market areas!")
                st.markdown("---")
                col_rent_method, col_rent_price = st.columns(2)
                with col_rent_method:
                    rent_pricing_method = st.radio(f"Rent Pricing Method (WH {i+1})", options=["Fixed Rent Price", "Square Foot Rent Price"], key=f"rent_method_{i}", horizontal=True, help="Choose pricing method.")
                with col_rent_price:
                    if rent_pricing_method == "Fixed Rent Price":
                        rent_price = st.number_input(f"Fixed Rent Price (WH {i+1}) ($/year)", min_value=0.0, value=50000.0, step=1000.0, format="%.0f", key=f"fixed_rent_{i}")
                    else:
                        rent_price = st.number_input(f"Rent Price per Sq Ft (WH {i+1}) ($/year)", min_value=0.0, value=10.0, step=1.0, format="%.0f", key=f"sqft_rent_{i}")
                wh_config["rent_pricing_method"] = rent_pricing_method
                wh_config["rent_price"] = rent_price
                st.markdown("---")
                col_emp_sal, col_emp_num = st.columns(2)
                with col_emp_sal:
                    avg_employee_salary = st.number_input(f"Avg Annual Salary/Employee (WH {i+1}) ($)", min_value=0, value=50000, step=1000, format="%d", key=f"employee_salary_{i}")
                with col_emp_num:
                     default_emp = 3 if wh_type == "MAIN" and len(served_markets) <= 1 else (4 if wh_type == "MAIN" else 2)
                     num_employees = st.number_input(f"Number of Employees (WH {i+1})", min_value=0, value=default_emp, step=1, key=f"num_employees_{i}")
                wh_config["avg_employee_salary"] = avg_employee_salary
                wh_config["num_employees"] = num_employees
                if wh_type == "MAIN":
                     st.markdown(f"<p class='sub-header-font' style='margin-top: 15px; color: #1A5276;'><i class='fas fa-ship icon'></i>International Shipping (WH {i+1})</p>", unsafe_allow_html=True)
                     ship_col1, ship_col2 = st.columns(2)
                     with ship_col1:
                         lt_shipping = st.number_input("Lead Time (days)", min_value=0, value=30, step=1, format="%d", key=f"lt_shipping_{i}", help="Ocean transit time.")
                     with ship_col2:
                         shipping_cost_40hc = st.number_input("Shipping Cost (per 40HC, $)", min_value=0.0, value=5000.0, step=100.0, format="%.0f", key=f"shipping_cost_40hc_{i}", help="Cost per 40ft container.")
                     wh_config["lt_shipping"] = lt_shipping
                     wh_config["shipping_cost_40hc"] = shipping_cost_40hc
                     if layout_type == "Main Regionals" and len(served_markets) > 1 and location:
                         st.markdown(f"<p class='sub-header-font' style='margin-top: 10px; color: #1A5276;'><i class='fas fa-truck icon'></i>Regional Land Shipping (WH {i+1})</p>", unsafe_allow_html=True)
                         land_shipping_data = {}
                         other_markets = [m for m in served_markets if m != location]
                         for add_area in other_markets:
                             land_cols = st.columns([2,3])
                             with land_cols[0]:
                                 distance_val = st.number_input(f"Distance to {add_area} (miles)", min_value=0.0, value=100.0, step=10.0, format="%.1f", key=f"dist_{i}_{add_area}")
                             with land_cols[1]:
                                 area_total_demand = sum(market_area_data[add_area][b]["avg_daily_demand"] for b in BRANDS if add_area in market_area_data and market_area_data[add_area][b]["avg_daily_demand"] > 0)
                                 if area_total_demand > 0:
                                     area_avg_order = sum(market_area_data[add_area][b]["avg_order_size"] * market_area_data[add_area][b]["avg_daily_demand"] for b in BRANDS if add_area in market_area_data) / area_total_demand
                                 else:
                                     area_avg_order = 0
                                 # Update the UI label to reflect per mile
                                 cost_val = st.number_input(f"Cost per Avg Order per Mile ({area_avg_order:.0f} units) to {add_area} ($)", min_value=0.0, value=50.0, step=1.0, format="%.2f", key=f"cost_{i}_{add_area}", help=f"Cost to ship an average order one mile to {add_area}.")
                             if cost_val == 0 and area_total_demand > 0:
                                 st.warning(f"Enter a non-zero shipping cost for {add_area}.")
                             land_shipping_data[add_area] = {
                                "distance": distance_val,
                                "cost_for_avg_order": cost_val,
                                "calculated_avg_order_size": area_avg_order
                             }
                         wh_config["land_shipping_data"] = land_shipping_data
                elif wh_type == "FRONT":
                     st.markdown(f"<p class='sub-header-font' style='margin-top: 15px; color: #1A5276;'><i class='fas fa-exchange-alt icon'></i>Transfer Shipping (WH {i+1})</p>", unsafe_allow_html=True)
                     main_wh_options = {f"WH {idx+1} ({w_conf['location']})": w_conf for idx, w_conf in temp_warehouse_configs.items() if w_conf.get("type") == "MAIN"}
                     if not main_wh_options:
                         st.error("No MAIN warehouse defined for this FRONT warehouse.")
                         wh_config["serving_central_wh_key"] = None
                     else:
                         serving_central_label = st.selectbox(f"Select Serving MAIN Warehouse", options=list(main_wh_options.keys()), key=f"serving_central_{i}", help="Choose the MAIN warehouse that supplies this FRONT warehouse.")
                         wh_config["serving_central_wh_key"] = serving_central_label
                     front_ship_col1, front_ship_col2 = st.columns(2)
                     with front_ship_col1:
                         front_shipping_cost_40 = st.number_input("Cost (per 40ft Truckload, $)", min_value=0.0, value=500.0, step=1.0, format="%.0f", key=f"front_shipping_cost_40_{i}", help="Cost for a 40ft truckload.")
                     with front_ship_col2:
                         front_shipping_cost_53 = st.number_input("Cost (per 53ft Truckload, $)", min_value=0.0, value=600.0, step=1.0, format="%.0f", key=f"front_shipping_cost_53_{i}", help="Cost for a 53ft truckload.")
                     wh_config["front_shipping_cost_40"] = front_shipping_cost_40
                     wh_config["front_shipping_cost_53"] = front_shipping_cost_53
                temp_warehouse_configs[i] = wh_config
        warehouse_data = list(temp_warehouse_configs.values())
        # Validate served markets consistency between FRONT and its serving MAIN warehouse
        for i, wh in enumerate(warehouse_data):
            if wh.get("type") == "FRONT":
                serving_main_label = wh.get("serving_central_wh_key")
                if serving_main_label:
                    main_wh = None
                    for candidate in warehouse_data:
                        candidate_label = f"WH {warehouse_data.index(candidate)+1} ({candidate.get('location')})"
                        if candidate_label == serving_main_label:
                            main_wh = candidate
                            break
                    if main_wh:
                        front_markets = set(wh.get("served_markets", []))
                        main_markets = set(main_wh.get("served_markets", []))
                        if not front_markets.issubset(main_markets):
                            st.error(f"Validation Error: FRONT Warehouse {i+1} ({wh.get('location')}) serves markets {front_markets} but its serving MAIN warehouse ({main_wh.get('location')}) serves {main_markets}. Please update the MAIN warehouse's served markets.")
        all_markets_served = set()
        config_complete = True
        final_warehouse_list_for_calc = []
        if layout_type == "Central and Fronts" and sum(1 for wh in warehouse_data if wh.get("type") == "MAIN") != 1:
             st.error("In 'Central and Fronts' layout, exactly one MAIN warehouse must be defined.")
             config_complete = False
        for i, wh in enumerate(warehouse_data):
            if not wh.get("location"):
                st.error(f"Location missing for Warehouse {i+1}.")
                config_complete = False
            if not wh.get("served_markets"):
                st.error(f"Served markets missing for Warehouse {i+1} ({wh.get('location', 'N/A')}).")
                config_complete = False
            if wh.get("type") == "FRONT" and not wh.get("serving_central_wh_key"):
                 st.error(f"Serving MAIN warehouse not selected for FRONT Warehouse {i+1} ({wh.get('location', 'N/A')}).")
                 config_complete = False
            all_markets_served.update(wh.get("served_markets", []))
            final_warehouse_list_for_calc.append(wh)
        unserved_markets = set(selected_market_areas) - all_markets_served
        if unserved_markets:
            st.error(f"The following market areas are not served by any warehouse: {', '.join(sorted(list(unserved_markets)))}")
            config_complete = False
        if config_complete:
            st.success("All warehouse configurations are complete and valid.")
            warehouse_data = final_warehouse_list_for_calc
        else:
            st.warning("Please review errors in warehouse configuration.")
            warehouse_data = []
    # --- UI Enhancement End ---

# =====================================================
# Helper Functions (Used in Calculations)
# =====================================================
def compute_annual_forecast_for_area(area, market_data):
    total = 0
    if area in market_data:
        for brand, params in market_data[area].items():
            total += sum(params.get("forecast_demand", [0]))
    return total

def compute_max_monthly_forecast_for_area(area, market_data):
    max_m = 0
    if area in market_data:
        for m in range(12):
            month_sum = sum(params.get("forecast_demand", [0])[m] for params in market_data[area].values())
            max_m = max(max_m, month_sum)
    return max_m

def compute_std_sum_for_area(area, market_data):
    total_std = 0
    if area in market_data:
        for params in market_data[area].values():
            total_std += params.get("std_daily_demand", 0)
    return total_std

def compute_daily_demand_sum_for_area(area, market_data):
    total = 0
    if area in market_data:
        for params in market_data[area].values():
            total += params.get("avg_daily_demand", 0)
    return total

def compute_max_monthly_forecast(warehouse, market_data):
    max_monthly = 0
    for area in warehouse.get("served_markets", []):
        area_max = compute_max_monthly_forecast_for_area(area, market_data)
        max_monthly = max(max_monthly, area_max)
    return max_monthly

def compute_daily_demand_sum(warehouse, market_data):
    total = 0
    for area in warehouse.get("served_markets", []):
        total += compute_daily_demand_sum_for_area(area, market_data)
    return total

def compute_annual_demand(warehouse, market_data):
    total = 0
    for area in warehouse.get("served_markets", []):
        total += compute_annual_forecast_for_area(area, market_data)
    return total

def compute_std_sum(warehouse, market_data):
    total = 0
    for area in warehouse.get("served_markets", []):
        total += compute_std_sum_for_area(area, market_data)
    return total

def compute_safety_stock_main(warehouse, market_data, Z_val, layout, all_warehouses):
    std_sum = compute_std_sum(warehouse, market_data)
    LT = warehouse.get("lt_shipping", 0)
    safety_stock_main = std_sum * sqrt(LT) * Z_val if LT > 0 else 0
    if layout == "Central and Fronts":
        try:
            warehouse_index = all_warehouses.index(warehouse)
            serving_label = f"WH {warehouse_index+1} ({warehouse.get('location')})"
            front_daily_demand = sum(
                compute_daily_demand_sum(front_wh, market_data)
                for front_wh in all_warehouses
                if front_wh.get("type") == "FRONT" and front_wh.get("serving_central_wh_key") == serving_label
            )
            transfer_lead_time = 12
            safety_stock_main += transfer_lead_time * front_daily_demand
        except ValueError:
            st.error("Internal error: MAIN warehouse not found during safety stock calculation.")
    return safety_stock_main

def compute_inventory_breakdown(warehouse, market_data, interest_rt, brand_prices, Z_val, layout, all_warehouses):
    LT = warehouse.get("lt_shipping", 0)
    breakdown = {brand: {"annual_forecast": 0, "std_sum": 0, "avg_daily_demand": 0} for brand in BRANDS}
    for area in warehouse.get("served_markets", []):
        if area in market_data:
            for brand, params in market_data[area].items():
                breakdown[brand]["annual_forecast"] += sum(params.get("forecast_demand", [0]))
                breakdown[brand]["std_sum"] += params.get("std_daily_demand", 0)
                breakdown[brand]["avg_daily_demand"] += params.get("avg_daily_demand", 0)
    front_contrib = {brand: 0 for brand in BRANDS}
    if layout == "Central and Fronts":
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
            st.error("Internal error during inventory breakdown calculation.")
    for brand in BRANDS:
        breakdown[brand]["front_contrib"] = 12 * front_contrib[brand] if layout == "Central and Fronts" else 0
    results = {}
    for brand in BRANDS:
        safety_stock = breakdown[brand]["std_sum"] * sqrt(LT) * Z_val + breakdown[brand]["front_contrib"]
        avg_inventory = (breakdown[brand]["annual_forecast"] / 12.0) + safety_stock
        unit_price = brand_prices.get(brand, 0)
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
    st.markdown("<p class='section-header-font'><i class='fas fa-cogs icon'></i>Calculate Network Costs</p>", unsafe_allow_html=True)
    st.info("Click the buttons below to calculate each cost component based on the setup data.")
    if not warehouse_data:
         st.error("Cannot perform calculations. Please complete the warehouse setup and resolve any errors.")
    else:
        calc_col1, calc_col2 = st.columns(2)
        with calc_col1:
             with st.container(border=True):
                 st.markdown("<p class='sub-header-font'><i class='fas fa-building icon'></i>Rental Costs</p>", unsafe_allow_html=True)
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
                            if rent_method == "Fixed Rent Price":
                                wh_rental_cost = rent_price
                                wh_area = "N/A (Fixed)"
                            else:
                                overhead = overhead_factor_main if wh_type == "MAIN" else overhead_factor_front
                                if sq_ft_per_unit <= 0 or rent_price <= 0:
                                    st.error(f"Invalid rental parameters for Warehouse {i+1}.")
                                    valid_input = False
                                    break
                                max_monthly = compute_max_monthly_forecast(wh, market_area_data)
                                if wh_type == "MAIN":
                                    safety_stock_main = compute_safety_stock_main(wh, market_area_data, Z_value, layout_type, warehouse_data)
                                    calculated_units = max_monthly + safety_stock_main
                                else:
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
             with st.container(border=True):
                 st.markdown("<p class='sub-header-font'><i class='fas fa-truck-loading icon'></i>Shipping Costs</p>", unsafe_allow_html=True)
                 if st.button("Calculate Shipping Costs", key="calc_shipping", type="primary"):
                     with st.spinner("Calculating Shipping Costs..."):
                        time.sleep(0.5)
                        shipping_details = []
                        total_sea_shipping_cost = 0.0
                        total_land_shipping_cost = 0.0
                        valid_input = True
                        if container_capacity_40 <= 0:
                             st.error("Container Capacity must be positive.")
                             valid_input = False
                        for i, wh in enumerate(warehouse_data):
                             if not valid_input:
                                  break
                             annual_demand_wh = compute_annual_demand(wh, market_area_data)
                             wh_shipping_cost = 0.0
                             shipment_type = "N/A"
                             if wh["type"] == "MAIN":
                                 cost_per_40hc = wh.get("shipping_cost_40hc", 0)
                                 if cost_per_40hc <= 0 and annual_demand_wh > 0:
                                     st.error(f"International Shipping Cost for WH {i+1} must be positive if demand exists.")
                                     valid_input = False
                                     break
                                 num_containers = ceil(annual_demand_wh / container_capacity_40)
                                 wh_shipping_cost = num_containers * cost_per_40hc
                                 shipment_type = f"{num_containers} x 40HC Int'l"
                                 if layout_type == "Main Regionals" and "land_shipping_data" in wh:
                                     regional_land_cost = 0
                                     for area, ship_data in wh["land_shipping_data"].items():
                                         area_annual_demand = compute_annual_forecast_for_area(area, market_area_data)
                                         area_avg_order_size = ship_data.get("calculated_avg_order_size", 1)
                                         cost_per_avg_order = ship_data.get("cost_for_avg_order", 0)
                                         distance_val = ship_data.get("distance", 0)  # Updated to include distance
                                         if area_avg_order_size > 0 and cost_per_avg_order > 0 and distance_val > 0:
                                             num_orders = ceil(area_annual_demand / area_avg_order_size)
                                             regional_land_cost += num_orders * cost_per_avg_order * distance_val
                                         elif area_annual_demand > 0 and cost_per_avg_order <= 0:
                                             st.warning(f"Missing regional shipping cost for {area} from {wh['location']}.")
                                     wh_shipping_cost += regional_land_cost
                                     shipment_type += f" + Regional ({regional_land_cost:,.0f}$)"
                             elif wh["type"] == "FRONT" and layout_type == "Central and Fronts":
                                 warehouse_land_cost = 0.0
                                 for m in range(12):
                                     monthly_forecast = 0
                                     for area in wh.get("served_markets", []):
                                         monthly_forecast += sum(market_area_data[area][brand]["forecast_demand"][m] for brand in market_area_data[area])
                                     weekly_demand = monthly_forecast / 4.0
                                     cost_40_unit = wh.get("front_shipping_cost_40", 0) / container_capacity_40
                                     cost_53_unit = wh.get("front_shipping_cost_53", 0) / (container_capacity_40 * 1.37)
                                     avg_cost_unit = (cost_40_unit + cost_53_unit) / 2.0
                                     normalized_cost = avg_cost_unit / 0.85
                                     weekly_shipping_cost = weekly_demand * normalized_cost
                                     warehouse_land_cost += weekly_shipping_cost * 4.0
                                 wh_shipping_cost = warehouse_land_cost
                                 shipment_type = "Calculated via avg. & normalization"
                             shipping_details.append({
                                "Warehouse": f"WH {i+1} ({wh.get('location')})",
                                "Type": wh["type"],
                                "Forcast Annual Demand (Units)": f"{annual_demand_wh:,.0f}",
                                "Est. Shipments": shipment_type,
                                "Annual Shipping Cost ($)": f"{wh_shipping_cost:,.0f}"
                             })
                             if wh["type"] == "MAIN":
                                 total_sea_shipping_cost += wh_shipping_cost
                             else:
                                 total_land_shipping_cost += wh_shipping_cost
                        if valid_input:
                            st.session_state.total_shipping_cost = total_sea_shipping_cost + total_land_shipping_cost
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
             with st.container(border=True):
                 st.markdown("<p class='sub-header-font'><i class='fas fa-coins icon'></i>Inventory Financing Costs</p>", unsafe_allow_html=True)
                 if st.button("Calculate Inventory Financing", key="calc_inventory", type="primary"):
                     with st.spinner("Calculating Inventory Financing..."):
                        time.sleep(0.5)
                        inventory_details = []
                        total_inventory_financing_cost = 0.0
                        total_avg_inventory_units = 0.0
                        total_safety_stock_units = 0.0
                        valid_input = True
                        if interest_rate < 0 or service_level < 0:
                             st.error("Interest Rate and Service Level must be non-negative.")
                             valid_input = False
                        if any(p <= 0 for p in brand_unit_prices.values()):
                             st.error("All Brand Unit Prices must be positive.")
                             valid_input = False
                        if layout_type == "Central and Fronts":
                            main_wh_list = [wh for wh in warehouse_data if wh["type"] == "MAIN"]
                            if len(main_wh_list) != 1:
                                st.error("Exactly one MAIN warehouse must be configured for 'Central and Fronts'.")
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
             with st.container(border=True):
                st.markdown("<p class='sub-header-font'><i class='fas fa-users icon'></i>Labor Costs</p>", unsafe_allow_html=True)
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
                                st.error(f"Employees and salary must be non-negative for Warehouse {i+1}.")
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
with tab_summary:
    st.markdown("<p class='section-header-font'><i class='fas fa-chart-pie icon'></i>Scenario Cost Summary</p>", unsafe_allow_html=True)
    all_calculated = (st.session_state.rental_costs_calculated and
                      st.session_state.inventory_costs_calculated and
                      st.session_state.shipping_costs_calculated and
                      st.session_state.labor_costs_calculated)
    if not all_calculated:
        st.warning("Please calculate all cost components in the 'Run Calculations' tab to see the full summary.")
    else:
        st.session_state.grand_total = (st.session_state.total_rental_cost +
                                         st.session_state.total_inventory_financing_cost +
                                         st.session_state.total_shipping_cost +
                                         st.session_state.total_labor_cost)
        st.markdown("### Total Estimated Annual Costs")
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
        st.markdown("---")
        st.markdown("<div style='text-align: center; margin-top: 20px;'>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='color: #1E3A5F;'>Grand Total Annual Cost: ${st.session_state.grand_total:,.0f}</h2>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
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
                             color_discrete_sequence=px.colors.sequential.Blues_r)
            fig_pie.update_traces(textposition='inside', textinfo='percent+label', hoverinfo='label+percent+value')
            fig_pie.update_layout(title_x=0.5, showlegend=True)
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No cost data to display in the chart.")
        st.markdown("### Summary per Warehouse (Combined Costs)")
        summary_list = []
        valid_wh_data_for_summary = warehouse_data
        for i, wh in enumerate(valid_wh_data_for_summary):
             wh_label = f"WH {i+1} ({wh.get('location', 'N/A')})"
             rental_cost = 0.0
             if not st.session_state.rental_details_df.empty:
                 rent_row = st.session_state.rental_details_df[st.session_state.rental_details_df['Warehouse'] == wh_label]
                 if not rent_row.empty:
                     try: rental_cost = float(rent_row.iloc[0]['Annual Rent ($)'].replace(',', ''))
                     except: pass
             inv_cost = 0.0
             if not st.session_state.inventory_details_df.empty:
                  inv_rows = st.session_state.inventory_details_df[st.session_state.inventory_details_df['Warehouse'] == wh_label]
                  if not inv_rows.empty:
                       try: inv_cost = inv_rows['Annual Financing Cost ($)'].str.replace('[$,]', '', regex=True).astype(float).sum()
                       except: pass
             ship_cost = 0.0
             if not st.session_state.shipping_details_df.empty:
                 ship_row = st.session_state.shipping_details_df[st.session_state.shipping_details_df['Warehouse'] == wh_label]
                 if not ship_row.empty:
                      try: ship_cost = float(ship_row.iloc[0]['Annual Shipping Cost ($)'].replace(',', ''))
                      except: pass
             labor_cost = 0.0
             if not st.session_state.labor_details_df.empty:
                 labor_row = st.session_state.labor_details_df[st.session_state.labor_details_df['Warehouse'] == wh_label]
                 if not labor_row.empty:
                      try: labor_cost = float(labor_row.iloc[0]['Annual Labor Cost ($)'].replace(',', ''))
                      except: pass
             total_cost = rental_cost + inv_cost + ship_cost + labor_cost
             summary_list.append({
                 "Warehouse": wh_label,
                 "Type": wh.get("type", "N/A"),
                 "Rental ($)": f"{rental_cost:,.0f}",
                 "Inventory ($)": f"{inv_cost:,.0f}",
                 "Shipping ($)": f"{ship_cost:,.0f}",
                 "Labor ($)": f"{labor_cost:,.0f}",
                 "Total ($)": f"{total_cost:,.0f}"
             })
        if summary_list:
             summary_df = pd.DataFrame(summary_list)
             st.dataframe(summary_df, hide_index=True, use_container_width=True)
        else:
             st.info("Warehouse summary data not available.")
# --- UI Enhancement End ---
