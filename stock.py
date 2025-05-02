import streamlit as st
import pandas as pd
import plotly.express as px
from alpha_vantage.timeseries import TimeSeries

# Set page config
st.set_page_config(page_title="Stock Price Visualizer", layout="wide")
st.title("📈 Stock Price Visualizer (Alpha Vantage)")

# Alpha Vantage API Key (pre-configured)
API_KEY = "LOU2NOYPT88FQNVR"  # Your key is hardcoded here

# Sidebar inputs
with st.sidebar:
    st.header("Input Parameters")
    ticker = st.text_input("Stock Ticker (e.g., AAPL)", "AAPL").upper()
    chart_type = st.selectbox("Chart Type", ["Line", "Candlestick"])
    show_volume = st.checkbox("Show Volume", True)
    moving_avg = st.checkbox("Show Moving Average", False)
    if moving_avg:
        ma_period = st.slider("Moving Average Period (days)", 5, 200, 50)

# Fetch data from Alpha Vantage
@st.cache_data
def load_data(ticker):
    try:
        ts = TimeSeries(key=API_KEY, output_format='pandas')
        data, meta_data = ts.get_daily(symbol=ticker, outputsize='compact')  # 'compact' for 100 days, 'full' for 20+ years
        data = data.sort_index()  # Ensure dates are in order
        data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']  # Rename columns
        return data
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Load data
df = load_data(ticker)

if not df.empty:
    # Display latest price and daily change
    latest_close = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2] if len(df) > 1 else latest_close
    price_change = latest_close - prev_close
    percent_change = (price_change / prev_close) * 100

    col1, col2 = st.columns(2)
    col1.metric(f"{ticker} Latest Close", f"${latest_close:.2f}")
    col2.metric("Daily Change", f"${price_change:.2f}", f"{percent_change:.2f}%")

    # Plotting
    if chart_type == "Line":
        fig = px.line(df, x=df.index, y='Close', title=f"{ticker} Daily Close Price")
        if moving_avg:
            df['MA'] = df['Close'].rolling(window=ma_period).mean()
            fig.add_scatter(x=df.index, y=df['MA'], name=f'{ma_period}-day MA')
    else:  # Candlestick
        fig = px.Figure(data=[px.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close']
        )])
        fig.update_layout(title=f"{ticker} Candlestick Chart")
    
    st.plotly_chart(fig, use_container_width=True)

    # Show volume if selected
    if show_volume:
        st.subheader("Trading Volume")
        fig_vol = px.bar(df, x=df.index, y='Volume')
        st.plotly_chart(fig_vol, use_container_width=True)

    # Raw data expander
    with st.expander("Show Raw Data"):
        st.dataframe(df.sort_index(ascending=False))
else:
    st.warning("No data found. Check your ticker symbol (e.g., AAPL, MSFT, TSLA).")