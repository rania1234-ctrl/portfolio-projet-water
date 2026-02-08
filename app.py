import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Set page configuration
st.set_page_config(
    page_title="Les ressources hydriques en Tunisie",
    page_icon="💧",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('water_data.csv')
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    return df

df = load_data()

# Sidebar
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Regional Analysis", "Water Stress Map"])

# Main content
st.title("💧 Water Resource Management in Tunisia")

if page == "Dashboard":
    st.header("National Water Resource Overview")
    
    # Year selector
    selected_year = st.selectbox("Select Year", sorted(df['year'].unique()))
    
    # Filter data for selected year
    yearly_data = df[df['year'] == selected_year]
    
    # Calculate national metrics
    total_consumption = yearly_data['consumption_m3'].sum()
    total_availability = yearly_data['availability_m3'].sum()
    water_stress = (total_consumption / total_availability) * 100 if total_availability > 0 else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Consumption", f"{total_consumption:,.0f} m³")
    with col2:
        st.metric("Total Availability", f"{total_availability:,.0f} m³")
    with col3:
        st.metric("Water Stress Level", f"{water_stress:.1f}%")
    
    # National trends
    st.subheader("National Water Resource Trends")
    
    # Calculate yearly trends
    yearly_trends = df.groupby('year').agg({
        'consumption_m3': 'sum',
        'availability_m3': 'sum'
    }).reset_index()
    
    yearly_trends['water_stress'] = (yearly_trends['consumption_m3'] / yearly_trends['availability_m3']) * 100
    
    # Plot trends
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=yearly_trends['year'], y=yearly_trends['consumption_m3'],
                            name='Consumption', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=yearly_trends['year'], y=yearly_trends['availability_m3'],
                            name='Availability', line=dict(color='blue')))
    fig.update_layout(title='National Water Resource Trends',
                     xaxis_title='Year',
                     yaxis_title='Volume (m³)',
                     hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Water stress trend
    fig_stress = px.line(yearly_trends, x='year', y='water_stress',
                        title='National Water Stress Trend',
                        labels={'water_stress': 'Water Stress (%)', 'year': 'Year'})
    fig_stress.update_traces(line_color='orange')
    st.plotly_chart(fig_stress, use_container_width=True)

elif page == "Regional Analysis":
    st.header("Regional Water Resource Analysis")
    
    # Region selector
    selected_region = st.selectbox("Select Region", sorted(df['region'].unique()))
    
    # Filter data for selected region
    region_data = df[df['region'] == selected_region]
    
    # Regional metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Average Consumption", f"{region_data['consumption_m3'].mean():,.0f} m³")
    with col2:
        st.metric("Average Availability", f"{region_data['availability_m3'].mean():,.0f} m³")
    with col3:
        stress = (region_data['consumption_m3'].mean() / region_data['availability_m3'].mean()) * 100
        st.metric("Average Water Stress", f"{stress:.1f}%")
    
    # Regional trends
    st.subheader(f"Water Resource Trends in {selected_region}")
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=region_data['year'], y=region_data['consumption_m3'],
                            name='Consumption', line=dict(color='red')))
    fig.add_trace(go.Scatter(x=region_data['year'], y=region_data['availability_m3'],
                            name='Availability', line=dict(color='blue')))
    fig.update_layout(title=f'Water Resource Trends in {selected_region}',
                     xaxis_title='Year',
                     yaxis_title='Volume (m³)',
                     hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    
    # Regional comparison
    st.subheader("Regional Comparison")
    selected_year = st.selectbox("Select Year for Comparison", sorted(df['year'].unique()))
    
    year_data = df[df['year'] == selected_year]
    fig_comparison = px.bar(year_data, x='region', y=['consumption_m3', 'availability_m3'],
                          title=f'Regional Water Resources Comparison ({selected_year})',
                          barmode='group')
    st.plotly_chart(fig_comparison, use_container_width=True)

elif page == "Water Stress Map":
    st.header("Regional Water Stress Map")
    
    # Calculate water stress for each region
    latest_year = df['year'].max()
    latest_data = df[df['year'] == latest_year]
    
    # Create map
    fig_map = px.scatter_mapbox(latest_data,
                              lat="latitude",
                              lon="longitude",
                              size="consumption_m3",
                              color="consumption_m3",
                              hover_name="region",
                              hover_data=["consumption_m3", "availability_m3"],
                              zoom=5,
                              title="Regional Water Consumption Map")
    
    fig_map.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig_map, use_container_width=True)
    
    # Water stress indicators
    st.subheader("Water Stress Indicators by Region")
    latest_data['water_stress'] = (latest_data['consumption_m3'] / latest_data['availability_m3']) * 100
    
    fig_stress = px.bar(latest_data, x='region', y='water_stress',
                       title='Water Stress by Region',
                       labels={'water_stress': 'Water Stress (%)'})
    st.plotly_chart(fig_stress, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Data source: Tunisian Ministry of Agriculture, Water Resources and Fisheries") 