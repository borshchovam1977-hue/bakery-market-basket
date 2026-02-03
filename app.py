import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from itertools import combinations
from collections import Counter

# Page configuration
st.set_page_config(
    page_title="Bakery Market Basket Analysis",
    page_icon="🥐",
    layout="wide"
)

st.title("🥐 The Bread Basket - Market Basket Analysis")
st.markdown("Analysis of item associations by time of day")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('Bakery.csv')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    return df

@st.cache_data
def get_item_pairs(df, daypart_filter=None, items_filter=None):
    """Get pairs of items that are bought together"""
    filtered_df = df.copy()
    
    if daypart_filter and len(daypart_filter) > 0:
        filtered_df = filtered_df[filtered_df['Daypart'].isin(daypart_filter)]
    
    if items_filter and len(items_filter) > 0:
        filtered_df = filtered_df[filtered_df['Items'].isin(items_filter)]
    
    # Group by transaction
    transactions = filtered_df.groupby('TransactionNo')['Items'].apply(list)
    
    # Find item pairs
    pair_counter = Counter()
    for items in transactions:
        unique_items = list(set(items))
        if len(unique_items) >= 2:
            for pair in combinations(sorted(unique_items), 2):
                pair_counter[pair] += 1
    
    return pair_counter

@st.cache_data
def get_item_stats(df):
    """Item statistics"""
    return df['Items'].value_counts()

# Load data
df = load_data()

# Sidebar - filters
st.sidebar.header("🔍 Filters")

# Daypart filter
daypart_order = ['Morning', 'Afternoon', 'Evening', 'Night']
available_dayparts = df['Daypart'].unique().tolist()
daypart_filter = st.sidebar.multiselect(
    "Time of Day",
    options=daypart_order,
    default=daypart_order,
    help="Select time of day for analysis"
)

# Get top items for filter
top_items = df['Items'].value_counts().head(30).index.tolist()

# Items filter
items_filter = st.sidebar.multiselect(
    "Items (leave empty for all)",
    options=sorted(df['Items'].unique()),
    default=[],
    help="Select specific items or leave empty for all"
)

# Top N slider
top_n = st.sidebar.slider("Number of top pairs to display", 5, 30, 15)

# Main content
filtered_df = df.copy()
if daypart_filter:
    filtered_df = filtered_df[filtered_df['Daypart'].isin(daypart_filter)]
if items_filter:
    filtered_df = filtered_df[filtered_df['Items'].isin(items_filter)]

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Transactions", filtered_df['TransactionNo'].nunique())
with col2:
    st.metric("Total Records", len(filtered_df))
with col3:
    st.metric("Unique Items", filtered_df['Items'].nunique())
with col4:
    avg_basket = len(filtered_df) / max(filtered_df['TransactionNo'].nunique(), 1)
    st.metric("Avg Basket Size", f"{avg_basket:.2f}")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Item Frequency", "🔗 Item Pairs", "⏰ Daypart Analysis", "📈 Daypart Comparison"])

with tab1:
    st.subheader("Item Sales Frequency")
    
    item_counts = filtered_df['Items'].value_counts().head(top_n)
    
    fig = px.bar(
        x=item_counts.values,
        y=item_counts.index,
        orientation='h',
        labels={'x': 'Number of Sales', 'y': 'Item'},
        title=f'Top-{top_n} Best Selling Items',
        color=item_counts.values,
        color_continuous_scale='Blues'
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Items Frequently Bought Together")
    
    pair_counter = get_item_pairs(df, daypart_filter, items_filter if items_filter else None)
    
    if pair_counter:
        top_pairs = pair_counter.most_common(top_n)
        
        pairs_df = pd.DataFrame([
            {'Item 1': pair[0], 'Item 2': pair[1], 'Count': count}
            for pair, count in top_pairs
        ])
        
        pairs_df['Pair'] = pairs_df['Item 1'] + ' + ' + pairs_df['Item 2']
        
        fig = px.bar(
            pairs_df,
            x='Count',
            y='Pair',
            orientation='h',
            title=f'Top-{top_n} Item Pairs Bought Together',
            color='Count',
            color_continuous_scale='Oranges'
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Data table
        st.dataframe(pairs_df[['Item 1', 'Item 2', 'Count']], use_container_width=True)
    else:
        st.info("No item pairs found with selected filters")

with tab3:
    st.subheader("Sales Analysis by Time of Day")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Transaction distribution by daypart
        daypart_trans = df.groupby('Daypart')['TransactionNo'].nunique().reindex(daypart_order)
        
        fig = px.pie(
            values=daypart_trans.values,
            names=daypart_trans.index,
            title='Transaction Distribution by Time of Day',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Average basket size by daypart
        items_by_daypart = df.groupby('Daypart').size()
        trans_by_daypart = df.groupby('Daypart')['TransactionNo'].nunique()
        avg_basket_by_daypart = (items_by_daypart / trans_by_daypart).reindex(daypart_order)
        
        fig = px.bar(
            x=avg_basket_by_daypart.index,
            y=avg_basket_by_daypart.values,
            title='Average Basket Size by Time of Day',
            labels={'x': 'Time of Day', 'y': 'Avg Items'},
            color=avg_basket_by_daypart.values,
            color_continuous_scale='Greens'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top items by daypart
    st.subheader("Top-10 Items by Time of Day")
    
    for daypart in daypart_order:
        if daypart in df['Daypart'].values:
            daypart_data = df[df['Daypart'] == daypart]['Items'].value_counts().head(10)
            if len(daypart_data) > 0:
                with st.expander(f"🕐 {daypart}", expanded=(daypart == 'Morning')):
                    fig = px.bar(
                        x=daypart_data.values,
                        y=daypart_data.index,
                        orientation='h',
                        title=f'Top-10 Items - {daypart}',
                        color=daypart_data.values,
                        color_continuous_scale='Purples'
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'}, height=400)
                    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Item Pairs Comparison by Time of Day")
    
    # Create data for all dayparts
    daypart_pairs_data = []
    
    for daypart in daypart_order:
        pairs = get_item_pairs(df, [daypart], items_filter if items_filter else None)
        for pair, count in pairs.most_common(10):
            daypart_pairs_data.append({
                'Time of Day': daypart,
                'Pair': f"{pair[0]} + {pair[1]}",
                'Count': count
            })
    
    if daypart_pairs_data:
        pairs_comparison_df = pd.DataFrame(daypart_pairs_data)
        
        fig = px.bar(
            pairs_comparison_df,
            x='Count',
            y='Pair',
            color='Time of Day',
            orientation='h',
            title='Top-10 Item Pairs by Time of Day',
            barmode='group',
            height=700,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)
        
        # Heatmap
        st.subheader("Heatmap: Top Items by Time of Day")
        
        # Create pivot table
        top_items_list = df['Items'].value_counts().head(15).index.tolist()
        heatmap_data = df[df['Items'].isin(top_items_list)].groupby(['Daypart', 'Items']).size().unstack(fill_value=0)
        heatmap_data = heatmap_data.reindex(daypart_order)
        
        fig = px.imshow(
            heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            title='Sales Heatmap (Top-15 Items)',
            labels=dict(x="Item", y="Time of Day", color="Sales"),
            color_continuous_scale='YlOrRd',
            aspect='auto'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Not enough data for comparison")

# Footer
st.markdown("---")
st.markdown("""
### ℹ️ About
This app analyzes transaction data from "The Bread Basket" bakery in Edinburgh.
Data covers the period from 30.10.2016 to 09.04.2017.

**Features:**
- 📊 Item sales frequency analysis
- 🔗 Find items frequently bought together (Market Basket Analysis)
- ⏰ Sales analysis by time of day
- 📈 Compare popular combinations across different times of day
""")
