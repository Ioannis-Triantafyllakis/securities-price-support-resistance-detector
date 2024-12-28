from twelvedata import TDClient
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd


class StockFetcher:
    def __init__(self, api_key: str):
        """
        Initialize the StockFetcher with the provided API key.

        Args:
            api_key (str): Your Twelve Data API key.
        """
        self.api_key: str = api_key
        self.td_client: TDClient = TDClient(apikey=self.api_key)

    def fetch_stocks(self) -> List[Dict[str, str]]:
        """
        Fetch stocks from the USA and UK, returning relevant fields as a list of dictionaries.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing stock data with fields
                                   symbol, name, currency, and exchange.
                                   If an error occurs, returns a list with an error message.
        """
        try:
            usa_stocks: List[Dict[str, Any]] = self.td_client.get_stocks_list(
                country="USA"
            ).as_json()
            uk_stocks: List[Dict[str, Any]] = self.td_client.get_stocks_list(
                country="United Kingdom"
            ).as_json()

            combined_stocks: List[Dict[str, Any]] = usa_stocks + uk_stocks

            filtered_stocks: List[Dict[str, str]] = [
                {
                    "symbol": stock["symbol"],
                    "name": stock["name"],
                    "currency": stock["currency"],
                    "exchange": stock["exchange"],
                }
                for stock in combined_stocks
            ]

            return filtered_stocks

        except Exception as e:
            return [{"error": "An unexpected error occurred: " + str(e)}]


class getStockTimeSeries:
    """
    A class to fetch and process time series data from the TDClient API.
    """

    def __init__(self, apikey: str, symbol: str, interval: str, outputsize: int):
        """
        Initialize the getStockTimeSeries object.

        Parameters:
            apikey: API key for the TDClient.
            symbol: Stock symbol to fetch data for.
            interval: Time interval for the data (e.g., '1day').
            outputsize: Number of data points to fetch.
        """
        self.apikey = apikey
        self.symbol = symbol
        self.interval = interval
        self.outputsize = outputsize

    def fetch_data(self) -> Optional[List[dict]]:
        """
        Fetch time series data from the TDClient API.

        Returns:
            Optional[list]: A list of dictionaries containing raw time series data.

        Raises:
            RuntimeError: If a TwelveDataError occurs, indicating no more minute API tokens are available.
        """
        try:
            td = TDClient(apikey=self.apikey)
            ts = td.time_series(
                symbol=self.symbol,
                interval=self.interval,
                outputsize=self.outputsize,
            )
            return ts.as_json()
        except Exception as e:
            raise RuntimeError(f"No more minute API tokens are available, or {e}.")

    def _convert_prices_to_numeric(self, raw_data: List[dict]) -> List[dict]:
        """
        Convert all price-related fields to numeric values in the dataset.

        Parameters:
            raw_data: The raw data fetched from the API.

        Returns:
            list: A list of dictionaries with numeric prices and additional fields.
        """
        execution_timestamp = datetime.now().isoformat()
        for entry in raw_data:
            entry["execution_timestamp"] = execution_timestamp
            entry["ticker"] = self.symbol
            for key, value in entry.items():
                if key != "datetime":
                    try:
                        entry[key] = float(value)
                    except ValueError:
                        try:
                            entry[key] = int(value)
                        except ValueError:
                            pass
        return raw_data

    def _check_for_empty_data(self, raw_data: List[dict]) -> None:
        """
        Check if any entry in the raw data contains empty values.

        Parameters:
            raw_data: The raw data fetched from the API.

        Raises:
            ValueError: If empty data is found.
        """
        for entry in raw_data:
            if any(value == "" or value is None for value in entry.values()):
                raise ValueError("Empty data found in the dataset.")

    def get_processed_data(self) -> List[dict]:
        """
        Fetch, validate, and convert the time series data.

        Returns:
            list: A list of dictionaries containing the processed data.
        """
        raw_data = self.fetch_data()

        if raw_data is None or len(raw_data) == 0:
            raise ValueError("No data fetched from the API.")

        self._check_for_empty_data(raw_data)

        return self._convert_prices_to_numeric(raw_data)

    def create_candlestick_chart(self) -> go.Figure:
        """
        Create a candlestick chart using Plotly from processed stock data.

        Returns:
            go.Figure: A Plotly figure object representing the candlestick chart.
        """

        processed_data = self.get_processed_data()
        df = pd.DataFrame(processed_data)
        df["datetime"] = pd.to_datetime(df["datetime"])
        execution_timestamp = processed_data[-1]["execution_timestamp"]

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df["datetime"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    increasing_line_color="green",
                    decreasing_line_color="red",
                    opacity=0.7,
                )
            ]
        )

        fig.update_layout(
            title=f"Candlestick Chart for {self.symbol}    (Execution Time: {execution_timestamp})",
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=True,
        )

        return fig


class stockPriceSupportResistance(getStockTimeSeries):
    """
    A class to find support and resistance levels from time series data.
    """

    def __init__(self, apikey: str, symbol: str, interval: str, outputsize: int):
        """
        Initialize the stockPriceSupportResistance object.

        Parameters:
            apikey: API key for the TDClient.
            symbol: Stock symbol to fetch data for.
            interval: Time interval for the data (e.g., '1day').
            outputsize: Number of data points to fetch.
        """
        getStockTimeSeries.__init__(self, apikey, symbol, interval, outputsize)

    def find_support_levels(
        self, global_only: bool = False
    ) -> Optional[List[List[Tuple[float, str]]]]:
        """
        Find support levels in the time series data.

        Parameters:
            global_only: If True, return only the lowest support level.

        Returns:
            List of lists containing support levels as [price, datetime] or None if global_only is True and no levels are found.
        """
        processed_data = self.get_processed_data()
        support_levels = []

        for i in range(2, len(processed_data) - 2):
            if (
                processed_data[i]["low"] < processed_data[i - 1]["low"]
                and processed_data[i]["low"] < processed_data[i - 2]["low"]
                and processed_data[i]["low"] < processed_data[i + 1]["low"]
                and processed_data[i]["low"] < processed_data[i + 2]["low"]
            ):
                support_levels.append(
                    [processed_data[i]["low"], processed_data[i]["datetime"]]
                )

        if global_only:
            return min(support_levels) if support_levels else None

        return support_levels

    def find_resistance_levels(
        self, global_only: bool = False
    ) -> Optional[List[List[Tuple[float, str]]]]:
        """
        Find resistance levels in the time series data.

        Parameters:
            global_only: If True, return only the highest resistance level.

        Returns:
            List of lists containing resistance levels as [price, datetime] or None if global_only is True and no levels are found.
        """
        processed_data = self.get_processed_data()
        resistance_levels = []

        for i in range(2, len(processed_data) - 2):
            if (
                processed_data[i]["high"] > processed_data[i - 1]["high"]
                and processed_data[i]["high"] > processed_data[i - 2]["high"]
                and processed_data[i]["high"] > processed_data[i + 1]["high"]
                and processed_data[i]["high"] > processed_data[i + 2]["high"]
            ):
                resistance_levels.append(
                    [processed_data[i]["high"], processed_data[i]["datetime"]]
                )

        if global_only:
            return max(resistance_levels) if resistance_levels else None

        return resistance_levels

    def create_candlestick_chart_with_support_resistance(
        self, global_only: bool = False
    ) -> go.Figure:
        """
        Create a candlestick chart with support and resistance lines.

        Parameters:
            global_only: If True, plot only the global support and resistance levels.

        Returns:
            go.Figure: A Plotly figure object representing the candlestick chart with support and resistance.
        """
        processed_data = self.get_processed_data()
        df = pd.DataFrame(processed_data)
        df["datetime"] = pd.to_datetime(df["datetime"])

        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=df["datetime"],
                    open=df["open"],
                    high=df["high"],
                    low=df["low"],
                    close=df["close"],
                    increasing_line_color="green",
                    decreasing_line_color="red",
                    opacity=0.7,
                )
            ]
        )

        support_levels = self.find_support_levels(global_only=global_only)
        resistance_levels = self.find_resistance_levels(global_only=global_only)

        if support_levels:
            if global_only:
                index = df[df["low"] == support_levels[0]].index[0]
                fig.add_shape(
                    type="line",
                    x0=df["datetime"].iloc[index],
                    y0=support_levels[0],
                    x1=df["datetime"].iloc[0],
                    y1=support_levels[0],
                    line=dict(color="blue", width=2),
                )
            else:
                for level in support_levels:
                    index = df[df["low"] == level[0]].index[0]
                    fig.add_shape(
                        type="line",
                        x0=df["datetime"].iloc[index],
                        y0=level[0],
                        x1=df["datetime"].iloc[0],
                        y1=level[0],
                        line=dict(color="blue", width=2),
                    )

        if resistance_levels:
            if global_only:
                index = df[df["high"] == resistance_levels[0]].index[0]
                fig.add_shape(
                    type="line",
                    x0=df["datetime"].iloc[index],
                    y0=resistance_levels[0],
                    x1=df["datetime"].iloc[0],
                    y1=resistance_levels[0],
                    line=dict(color="orange", width=2),
                )
            else:
                for level in resistance_levels:
                    index = df[df["high"] == level[0]].index[0]
                    fig.add_shape(
                        type="line",
                        x0=df["datetime"].iloc[index],
                        y0=level[0],
                        x1=df["datetime"].iloc[0],
                        y1=level[0],
                        line=dict(color="orange", width=2),
                    )

        execution_timestamp = processed_data[-1]["execution_timestamp"]

        fig.update_layout(
            title=f"Candlestick Chart for {self.symbol} (Execution Time: {execution_timestamp})",
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=True,
        )

        return fig
