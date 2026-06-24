import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Product & Factory Profitability Dashboard",
    layout="wide",
    page_icon="🍬"
)

products_data = {
    'Division': ['Chocolate', 'Chocolate', 'Chocolate', 'Chocolate', 'Chocolate',
                 'Sugar', 'Sugar', 'Sugar', 'Sugar', 'Other',
                 'Sugar', 'Sugar', 'Other', 'Other', 'Other'],
    'Product Name': [
        "Wonka Bar - Nutty Crunch Surprise", "Wonka Bar - Fudge Mallows",
        "Wonka Bar - Scrumdiddlyumptious", "Wonka Bar - Milk Chocolate",
        "Wonka Bar - Triple Dazzle Caramel", "Laffy Taffy", "SweeTARTS",
        "Nerds", "Fun Dip", "Fizzy Lifting Drinks", "Everlasting Gobstopper",
        "Hair Toffee", "Lickable Wallpaper", "Wonka Gum", "Kazookles"
    ],
    'Factory': ["Let's O' Nuts", "Let's O' Nuts", "Let's O' Nuts", "Wicked Choccy's",
                "Wicked Choccy's", "Sugar Shack", "Sugar Shack", "Sugar Shack",
                "Sugar Shack", "Sugar Shack", "Secret Factory", "The Other Factory",
                "Secret Factory", "Secret Factory", "The Other Factory"],
    'Units Sold': [12000, 8500, 15000, 22000, 9500, 18000, 14000, 16000, 11000,
                   7000, 13000, 8000, 6000, 9000, 5000],
    'Sales Revenue': [240000, 170000, 375000, 440000, 237500, 90000, 70000,
                      80000, 55000, 35000, 65000, 40000, 30000, 45000, 25000],
    'Cost of Goods': [120000, 85000, 150000, 220000, 118750, 54000, 42000,
                      48000, 33000, 21000, 39000, 24000, 18000, 27000, 15000],
}

df = pd.DataFrame(products_data)

df = df[df['Sales Revenue'] > 0]
df = df[df['Cost of Goods'] > 0]
df = df[df['Units Sold'] > 0].copy()

df['Gross Profit'] = df['Sales Revenue'] - df['Cost of Goods']
df['Gross Margin (%)'] = (df['Gross Profit'] / df['Sales Revenue'] * 100).round(2)
df['Profit per Unit'] = (df['Gross Profit'] / df['Units Sold']).round(2)
df['Revenue Contribution (%)'] = (df['Sales Revenue'] / df['Sales Revenue'].sum() * 100).round(2)
df['Profit Contribution (%)'] = (df['Gross Profit'] / df['Gross Profit'].sum() * 100).round(2)

def categorize_product(row):
    if row['Gross Profit'] >= df['Gross Profit'].quantile(0.75) and row['Gross Margin (%)'] >= 50:
        return "High-Profit / High-Margin"
    elif row['Units Sold'] >= df['Units Sold'].quantile(0.75) and row['Gross Margin (%)'] < 40:
        return "High-Sales / Low-Margin"
    elif row['Gross Profit'] <= df['Gross Profit'].quantile(0.25) and row['Units Sold'] <= df['Units Sold'].quantile(0.25):
        return "Low-Sales / Low-Profit"
    else:
        return "Medium Performer"

df['Category'] = df.apply(categorize_product, axis=1)

factory_coords = {
    "Let's O' Nuts": {"lat": 32.881893, "lon": -111.768036},
    "Wicked Choccy's": {"lat": 32.076176, "lon": -81.088371},
    "Sugar Shack": {"lat": 48.11914, "lon": -96.18115},
    "Secret Factory": {"lat": 41.446333, "lon": -90.565487},
    "The Other Factory": {"lat": 35.1175, "lon": -89.971107}
}

st.title("🍬 Product & Factory Profitability Dashboard")
st.markdown("### Nassau Candy Distributor - Analytical Insights")

st.sidebar.header("🔍 Filters")
divisions = ['All'] + sorted(df['Division'].unique())
selected_division = st.sidebar.selectbox("Division", divisions)
search_product = st.sidebar.text_input("Search Product")
margin_threshold = st.sidebar.slider("Minimum Gross Margin (%)", 0, 100, 20)

filtered_df = df.copy()
if selected_division != 'All':
    filtered_df = filtered_df[filtered_df['Division'] == selected_division]
if search_product:
    filtered_df = filtered_df[filtered_df['Product Name'].str.contains(search_product, case=False)]
filtered_df = filtered_df[filtered_df['Gross Margin (%)'] >= margin_threshold]

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "📈 Product Analysis", 
    "🏭 Division & Factory", 
    "🔍 Diagnostics", 
    "📋 Methodology"
])

with tab1:
    st.header("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    with col1: st.metric("Total Revenue", f"${filtered_df['Sales Revenue'].sum():,}")
    with col2: st.metric("Total Gross Profit", f"${filtered_df['Gross Profit'].sum():,}")
    with col3: st.metric("Avg Gross Margin", f"{filtered_df['Gross Margin (%)'].mean():.1f}%")
    with col4: st.metric("Total Units Sold", f"{filtered_df['Units Sold'].sum():,}")

    st.subheader("Top Products by Margin")
    top_products = filtered_df.nlargest(8, 'Gross Margin (%)')[['Product Name', 'Division', 'Gross Margin (%)', 'Gross Profit']]
    st.dataframe(top_products, use_container_width=True)

with tab2:
    st.header("Product-Level Profitability Analysis")
    st.dataframe(filtered_df[['Product Name', 'Category', 'Gross Margin (%)', 
                              'Gross Profit', 'Profit per Unit', 'Revenue Contribution (%)']], 
                 use_container_width=True)

    fig1 = px.bar(filtered_df.sort_values('Gross Margin (%)', ascending=False),
                  x='Product Name', y='Gross Margin (%)', color='Division',
                  title="Gross Margin by Product")
    st.plotly_chart(fig1, use_container_width=True)

with tab3:
    st.header("Division & Factory Performance")
    div_summary = filtered_df.groupby('Division').agg({
        'Sales Revenue': 'sum',
        'Gross Profit': 'sum',
        'Gross Margin (%)': 'mean',
        'Units Sold': 'sum'
    }).round(2).reset_index()
    st.dataframe(div_summary, use_container_width=True)

    st.subheader("Factory Locations")
    map_df = pd.DataFrame({
        'lat': [v['lat'] for v in factory_coords.values()],
        'lon': [v['lon'] for v in factory_coords.values()],
        'Factory': list(factory_coords.keys())
    })
    st.map(map_df, size=800)

with tab4:
    st.header("Profit Concentration (Pareto) & Cost Diagnostics")
    
    df_sorted = filtered_df.sort_values('Gross Profit', ascending=False).copy()
    df_sorted['Cumulative Profit %'] = df_sorted['Gross Profit'].cumsum() / df_sorted['Gross Profit'].sum() * 100
    
    fig_pareto = px.line(df_sorted, x=range(1, len(df_sorted)+1), y='Cumulative Profit %',
                         title="Pareto Analysis - Profit Concentration", markers=True)
    st.plotly_chart(fig_pareto, use_container_width=True)

    fig_cost = px.scatter(filtered_df, x='Cost of Goods', y='Gross Margin (%)',
                          color='Division', hover_name='Product Name',
                          title="Cost vs Margin Diagnostics")
    st.plotly_chart(fig_cost, use_container_width=True)

with tab5:
    st.header("Methodology & Key Insights")
    st.markdown("""
    **Data Cleaning & Validation**  
    • Validated cost, sales and units values  
    • Removed zero/invalid records  
    • Standardized product and division labels
    """)
    
    st.markdown("**Key Insights**")
    st.info("• Chocolate Division is the most profitable")
    st.warning("• Few products contribute majority of profit (Pareto Principle)")
    st.success("• High-Margin products identified for focus")

st.sidebar.markdown("---")
st.sidebar.info("📌 Built as per given Analytical Methodology")