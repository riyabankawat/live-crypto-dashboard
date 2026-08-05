import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Live Market Tracker", page_icon="📈", layout="wide")

st.title("📈 Real-Time Crypto Pipeline & Analytics Dashboard")
st.caption("Powered by Python, CoinGecko REST API, SQLite, and Streamlit")

def load_data():
    conn = sqlite3.connect("crypto.db")
    df = pd.read_sql("SELECT * FROM crypto_history", conn)
    conn.close()
    return df

try:
    df = load_data()

    if df.empty:
        st.warning("Database is empty. Run `fetch_data.py` first.")
    else:
        # Sidebar Filter Controls
        st.sidebar.header("Dashboard Controls")
        selected_coin = st.sidebar.selectbox("Select Asset", df["name"].unique())
        
        if st.sidebar.button("🔄 Refresh Dashboard"):
            st.rerun()

        # Data filtering
        coin_df = df[df["name"] == selected_coin]
        latest_record = coin_df.iloc[-1]

        # Metric Cards
        st.subheader(f"Current Status: {selected_coin}")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Current Price", f"${latest_record['price_usd']:,.2f}")
        col2.metric("24h Change", f"{latest_record['change_24h']:.2f}%", delta=f"{latest_record['change_24h']:.2f}%")
        col3.metric("24h Volume", f"${latest_record['volume_24h']:,.0f}")
        col4.metric("Market Cap", f"${latest_record['market_cap']:,.0f}")

        st.markdown("---")

        # Interactive Chart
        st.subheader(f"Price Trend Over Time ({selected_coin})")
        fig = px.line(
            coin_df,
            x="timestamp",
            y="price_usd",
            markers=True,
            labels={"timestamp": "Logged Time", "price_usd": "Price (USD)"}
        )
        fig.update_layout(hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

        # Raw Table View
        with st.expander("🔍 View Raw Database History"):
            st.dataframe(df.sort_values(by="timestamp", ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error loading database: {e}")