import streamlit as st
from PIL import Image
import pandas as pd
import feedparser
import numpy as np
import requests
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy.signal import argrelextrema
from sklearn.metrics import mean_absolute_error
from crypto_plot import plot_crypto_prices, LossProfitPlot
from invest_advice import Invest_advice

# Supported cryptocurrencies
supported_coins = ['BTC', 'ETH', 'DOGE', 'LIT']
forecast_files = {
    'BTC': 'BTC_forecast.csv',
    'ETH': 'ETH_forecast.csv',
    'DOGE': 'DOGE_forecast.csv',
    'LIT': 'LIT_forecast.csv',
}
historical_files = {
    'BTC': 'BTC_historical_data.csv',
    'ETH': 'ETH_historical_data.csv',
    'DOGE': 'DOGE_historical_data.csv',
    'LIT': 'LIT_historical_data.csv',
}

# Load forecast and historical data
forecast_data = {coin: pd.read_csv(file) for coin, file in forecast_files.items()}
historical_data = {coin: pd.read_csv(file) for coin, file in historical_files.items()}

def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'ids': 'bitcoin,ethereum,dogecoin,litecoin,binancecoin,tether,solana,tron,polygon', # Add more coins as needed
        'order': 'market_cap_desc',
        'per_page': 10,
        'page': 1,
        'sparkline': False
    }
    response = requests.get(url, params=params)
    return response.json()

def plot_growth(crypto_data):
    growth_df = pd.DataFrame(crypto_data)
    growth_df = growth_df[['name', 'price_change_percentage_24h']]
    fig = px.bar(growth_df, x='name', y='price_change_percentage_24h', title='24h Growth Percentage')
    return fig

def plot_current_price_trends(coin_name, days=7):
    data = historical_data[coin_name].tail(days)
    fig = px.line(data, x='Date', y='Close', title=f'{coin_name} Price Trend (Last {days} Days)')
    return fig

def plot_market_cap_distribution(crypto_data):
    market_cap_df = pd.DataFrame(crypto_data)[['name', 'market_cap']]
    fig = px.pie(market_cap_df, values='market_cap', names='name', title='Market Cap Distribution')
    return fig

def plot_24h_volume(crypto_data):
    volume_df = pd.DataFrame(crypto_data)[['name', 'total_volume']]
    fig = px.bar(volume_df, x='name', y='total_volume', title='24-Hour Trading Volume')
    return fig

# Calculate correlations
def calculate_correlations(selected_coin):
    all_data = pd.DataFrame()
    for coin, data in historical_data.items():
        all_data[coin] = data['Close']
    correlations = all_data.corr()[selected_coin].sort_values()
    negative_correlations = correlations.head(10)
    positive_correlations = correlations.tail(10)
    return positive_correlations, negative_correlations

# Define your buy and sell strategy
def best_times_to_buy_sell(data):
    short_window = 10
    long_window = 50
    short_moving_avg = data.rolling(window=short_window).mean()
    long_moving_avg = data.rolling(window=long_window).mean()

    buy_points = [data.index[i] for i in range(1, len(data)) if short_moving_avg[i] > long_moving_avg[i] and short_moving_avg[i-1] <= long_moving_avg[i-1]]
    sell_points = [data.index[i] for i in range(1, len(data)) if short_moving_avg[i] < long_moving_avg[i] and short_moving_avg[i-1] >= long_moving_avg[i-1]]
    return buy_points, sell_points

# Plot moving average
def plot_moving_average(coin_name, window_size=7):
    data = historical_data[coin_name]['Close']
    moving_average = data.rolling(window=window_size).mean()
    fig = px.line(x=data.index, y=[data, moving_average], title=f'Moving Average ({window_size} Days) for {coin_name}')
    return fig

def plot_with_buy_sell(coin_name, predict_days):
    fig = plot_crypto_prices(coin_name, predict_days)
    data = historical_data[coin_name]['Close']  
    buy_points, sell_points = best_times_to_buy_sell(data)
    for bp in buy_points:
        fig.add_vline(x=bp, line_color="green")
    for sp in sell_points:
        fig.add_vline(x=sp, line_color="red")

    return fig


def display_crypto_news(search_query=None):
    rss_url = "https://feeds.feedburner.com/CoinDesk"
    feed = feedparser.parse(rss_url)
    search_results = []

    for entry in feed.entries:
        if search_query:
            title = entry.title.lower()
            content = entry.summary.lower()
            if search_query.lower() in title or search_query.lower() in content:
                search_results.append(entry)
        else:
            search_results.append(entry)

    for entry in search_results:
        st.markdown(f"### {entry.title}")
        content = entry.summary
        st.markdown(content, unsafe_allow_html=True)
        st.write("Published:", entry.published)
        st.write("Link:", entry.link)
        st.write("---")

def news():
    search_query = st.text_input('Search')
    if st.button('Search'):
        display_crypto_news(search_query)
               

def main():
    st.set_page_config(layout="wide")
    image = Image.open("logo s.png")
    st.image(image, use_column_width=True)

    selected_menu = st.sidebar.selectbox("Menu", ["Home", "Charts", "Investment", "Breaking News", "About"])

    if selected_menu == "Home":
        st.write("<h1 style='text-align: center; color: white;'>Welcome to the Intelligent Coin Trading (IST) Platform!</h1>", unsafe_allow_html=True)
        crypto_data = fetch_crypto_data()
        crypto_df = pd.DataFrame(crypto_data)
        #st.write(crypto_df.columns)
        selected_columns = [
         'name', 'symbol', 'current_price', 'market_cap', 'market_cap_rank',
         'total_volume', 'high_24h', 'low_24h', 'price_change_24h',
         'price_change_percentage_24h', 'market_cap_change_24h',
         'market_cap_change_percentage_24h'
        ]
        # Select only the columns that exist in the DataFrame
        existing_columns = [col for col in selected_columns if col in crypto_df.columns]
        crypto_df = crypto_df[existing_columns]
        st.table(crypto_df)
        
        # Create a subplot with 2 rows and 2 columns
        fig = make_subplots(rows=2, cols=2, subplot_titles=supported_coins)
        
        # Add the individual plots to the subplot
        for idx, coin_name in enumerate(supported_coins):
            row = (idx // 2) + 1
            col = (idx % 2) + 1
            fig.add_trace(go.Scatter(x=historical_data[coin_name]['Date'], y=historical_data[coin_name]['Close']), row=row, col=col)
            
             # Update the layout and display the subplot
        fig.update_layout(title='Price Trends (Last 7 Days)', showlegend=False)
        st.plotly_chart(fig)


         # Displaying the selected data as a table
        
        
        st.plotly_chart(plot_market_cap_distribution(crypto_data))
        st.plotly_chart(plot_24h_volume(crypto_data))
        fig_growth = plot_growth(crypto_data)
        st.plotly_chart(fig_growth)


    elif selected_menu == "Charts":
        coin_name = st.selectbox("Coin Symbol", supported_coins)
        predict_days = st.selectbox("Number of Prediction Days (1-30)", range(1, 31), index=0)
        
        # Display correlated cryptocurrencies
        positive_correlations, negative_correlations = calculate_correlations(coin_name)
        st.write("Positive Correlations:", positive_correlations)
        st.write("Negative Correlations:", negative_correlations)

        # Display moving average
        window_size = st.slider("Moving Average Window Size", 1, 30, 7)
        fig_moving_average = plot_moving_average(coin_name, window_size)
        st.plotly_chart(fig_moving_average)
        
        if st.button("Show Result"):
            fig_closing_price = plot_crypto_prices(coin_name, predict_days)
            fig_loss_profit = LossProfitPlot(coin_name, predict_days)
            st.plotly_chart(fig_closing_price)
            st.plotly_chart(fig_loss_profit)
            data = historical_data[coin_name]['Close']
            
            # Display buy and sell points
            data = historical_data[coin_name]['Close']
            buy_points, sell_points = best_times_to_buy_sell(data)
            for bp in buy_points:
                fig_closing_price.add_vline(x=bp, line_color="green")
            for sp in sell_points:
                fig_closing_price.add_vline(x=sp, line_color="red")
            st.plotly_chart(fig_closing_price)


    elif selected_menu == "Investment":
        selected_coin = st.selectbox("Select Coin", ['BTC', 'ETH', 'DOGE', 'LIT'])
        investment_amount = st.slider("Investment Amount ($)", 100, 10000, 1000)
        time_horizon = st.slider("Time Horizon (days)", 1, 365, 30)
        risk_tolerance = st.slider("Risk Tolerance (0-10)", 0, 10, 5)
        target_profit = st.slider("Amount of Profit ($)", 1, 10000, 1)
        
        if st.button("Show Result"):
            result = Invest_advice(selected_coin, time_horizon, target_profit, investment_amount, risk_tolerance)
            if result is None:
                st.write("The selected coin cannot reach the target profit.")
            else:
                st.write("Invest in {} for {} days to achieve ${} profit.".format(selected_coin, time_horizon, target_profit))

    elif selected_menu == "Breaking News":
        st.header("Breaking News")
        news()

    elif selected_menu == "About":
        st.write(""" Solent Intelligence (SOLiGence) is a leading multinational financial organization that specializes in stocks, shares, savings, and investments. 
                 Serving millions of subscribers, we offer unparalleled access to global markets through a user-centered design that caters to both newcomers and seasoned traders.
                 Our standout feature is the Intelligent Coin Trading (IST) platform, a state-of-the-art system that embodies our commitment to innovation. 
                 The IST platform enables intelligent cryptocurrency trading, providing predictive insights for opportune buying and selling. 
                 With SOLiGence, clients can target daily gains or long-term growth, guided by our integrity, expertise, and forward-thinking solutions""")
        st.header("Contact Us")
        st.write("Email: bodapatishashank1998@gmail.com")
        st.write("Address: Solent University, East Park Terrace, Southampton, SO14 0YN")

if __name__ == '__main__':
    main()