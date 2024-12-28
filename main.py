import streamlit as st
from classes.classes import StockFetcher, stockPriceSupportResistance

api_key = st.secrets["twelve_data_api_key"]

all_tickers = StockFetcher(api_key)
all_tickers_dict = all_tickers.fetch_stocks()

st.set_page_config(layout="wide")

st.sidebar.header("Choose a Stock")
selected_stock = st.sidebar.selectbox(
    "Select a stock to analyze:",
    [
        f'{d["name"]} ({d["symbol"]})'
        for d in all_tickers_dict
        if "name" in d and "symbol" in d
    ],
)
time_interval = st.sidebar.selectbox(
    "Select time interval:", ["1day", "1week", "1month"]
)
periods = st.sidebar.number_input(
    "Select number of periods:", min_value=5, max_value=200, value=40
)
global_only = st.sidebar.checkbox(
    "Get only global support/resistance levels:", value=True
)

ticker = (
    selected_stock[selected_stock.find("(") + 1 : selected_stock.find(")")].strip()
    if "(" in selected_stock and ")" in selected_stock
    else ""
)

if st.sidebar.button("Analyze"):
    try:
        support_resistance = stockPriceSupportResistance(
            api_key, ticker, time_interval, periods
        )

        st.title("Securities' price support & resistance levels")
        st.write(selected_stock)
        plot = support_resistance.create_candlestick_chart_with_support_resistance(
            global_only=global_only
        )
        st.plotly_chart(plot, use_container_width=True)

    except RuntimeError:
        st.warning(
            "You can fetch stock data for 8 stocks per minute maximum. Wait for the next minute to fetch data again."
        )
