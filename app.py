import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

# Set page config
st.set_page_config(
    page_title="Navedas CX Intelligence Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data
@st.cache_data
def load_data():
    tickets_df = pd.read_excel('navedas_cx_1000 (1).xlsx', sheet_name='Ticket Records', skiprows=1)
    monthly_df = pd.read_excel('navedas_cx_1000 (1).xlsx', sheet_name='Monthly Summary', skiprows=1)
    agents_df = pd.read_excel('navedas_cx_1000 (1).xlsx', sheet_name='Agent Performance', skiprows=1)
    signals_df = pd.read_excel('navedas_cx_1000 (1).xlsx', sheet_name='Issue Intelligence', skiprows=1)
    return tickets_df, monthly_df, agents_df, signals_df

# Load data
tickets_df, monthly_df, agents_df, signals_df = load_data()

# Title
st.title("🎯 Navedas CX Intelligence Hub")
st.markdown("*Live Dashboard with 1,000 Ticket Records*")

# Sidebar
st.sidebar.header("📋 Filters")
selected_category = st.sidebar.multiselect(
    "Category",
    options=tickets_df['Category'].unique(),
    default=tickets_df['Category'].unique()
)

selected_status = st.sidebar.multiselect(
    "Status",
    options=tickets_df['Status'].unique(),
    default=tickets_df['Status'].unique()
)

# Filter data
filtered_df = tickets_df[
    (tickets_df['Category'].isin(selected_category)) &
    (tickets_df['Status'].isin(selected_status))
]

# KPI Section
st.header("📊 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Tickets", len(filtered_df), "1,000 records")

with col2:
    avg_score = filtered_df['Score (1–100)'].mean()
    st.metric("Avg CSAT Score", f"{avg_score:.1f}%", "Live")

with col3:
    resolved = len(filtered_df[filtered_df['Status'] == 'Resolved'])
    st.metric("Resolved", resolved, f"{(resolved/len(filtered_df)*100):.1f}%")

with col4:
    churn_count = len(filtered_df[filtered_df['Category'] == 'Churn'])
    st.metric("Churn Issues", churn_count, f"{(churn_count/len(filtered_df)*100):.1f}%")

# Charts
st.header("📈 Analytics")
col1, col2 = st.columns(2)

with col1:
    # Category distribution
    cat_counts = filtered_df['Category'].value_counts()
    fig = px.pie(
        values=cat_counts.values,
        names=cat_counts.index,
        title="Tickets by Category",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Status distribution
    status_counts = filtered_df['Status'].value_counts()
    fig = px.bar(
        x=status_counts.index,
        y=status_counts.values,
        title="Tickets by Status",
        labels={'x': 'Status', 'y': 'Count'},
        color=status_counts.index,
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    st.plotly_chart(fig, use_container_width=True)

# Score distribution
st.subheader("Score Distribution")
fig = px.histogram(
    filtered_df,
    x='Score (1–100)',
    nbins=20,
    title="CSAT Score Distribution",
    color_discrete_sequence=['#7c3aed']
)
st.plotly_chart(fig, use_container_width=True)

# Monthly trends
st.subheader("Monthly Trends")
fig = px.line(
    monthly_df,
    x='Month',
    y=['Tickets', 'Resolved', 'Pending', 'Escalated'],
    title="Ticket Volume Trend",
    markers=True,
    labels={'value': 'Count', 'variable': 'Status'}
)
st.plotly_chart(fig, use_container_width=True)

# Agent Performance
st.header("👥 Agent Performance")
agents_display = agents_df[['Agent', 'Tickets', 'CSAT %', 'Escalation Rate']].head(10)
st.dataframe(agents_display, use_container_width=True)

# Detailed Table
st.header("📋 Detailed Ticket Data")

# Search
search_term = st.text_input("Search by Ticket ID, Agent, or Issue")
if search_term:
    filtered_df = filtered_df[
        filtered_df['Ticket ID'].str.contains(search_term, case=False, na=False) |
        filtered_df['Agent'].str.contains(search_term, case=False, na=False) |
        filtered_df['Sub-Issue'].str.contains(search_term, case=False, na=False)
    ]

st.dataframe(filtered_df, use_container_width=True, height=400)

# Download CSV
csv = filtered_df.to_csv(index=False)
st.download_button(
    label="📥 Download CSV",
    data=csv,
    file_name=f"tickets_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv"
)

# Footer
st.divider()
st.markdown("""
---
**Navedas CX Intelligence Hub** | Built with Streamlit | Real-time Data Analysis
""")
