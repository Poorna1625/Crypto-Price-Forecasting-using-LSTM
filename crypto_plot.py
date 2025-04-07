import plotly.express as px
import pandas as pd
# Function for plotting crypto prices
def plot_crypto_prices(coin_name, forecast_days):
    historical_data_files = {
        'BTC': 'BTC_historical_data.csv',
        'ETH': 'ETH_historical_data.csv',
        'LIT': 'LIT_historical_data.csv',
        'DOGE': 'DOGE_historical_data.csv'
    }
    forecast_data_files = {
        'BTC': 'BTC_forecast.csv',
        'ETH': 'ETH_forecast.csv',
        'LIT': 'LIT_forecast.csv',
        'DOGE': 'DOGE_forecast.csv'
    }

    # Read the historical data
    historical_data = pd.read_csv(historical_data_files[coin_name])
    historical_data['Date'] = pd.to_datetime(historical_data['Date'])

    # Read the forecasted data
    forecast_data = pd.read_csv(forecast_data_files[coin_name])

    # Create a Plotly figure object
    fig = px.line()

    # Add the actual prices
    fig.add_scatter(x=historical_data['Date'], y=historical_data['Close'], name='Actual Prices', line_color='blue')

    # Create dates for predicted prices
    forecast_dates = pd.date_range(start=historical_data['Date'].iloc[-1], periods=forecast_days+1)[1:]

    # Add the predicted prices
    fig.add_scatter(x=forecast_dates, y=forecast_data['Predicted_Price'], name='Predicted Prices', line_color='orange')

    # Set plot labels and title
    fig.update_layout(xaxis_title='Date', yaxis_title='Price', title=f'{coin_name} Actual and Predicted Prices')

    return fig

# Function for LossProfitPlot goes here
def LossProfitPlot(coin_name, forecast_days):
    forecast_data_files = {
        'BTC': 'BTC_forecast.csv',
        'ETH': 'ETH_forecast.csv',
        'LIT': 'LIT_forecast.csv',
        'DOGE': 'DOGE_forecast.csv'
    }

    # Read the forecasted data
    forecast_data = pd.read_csv(forecast_data_files[coin_name])

    # Create a Plotly figure object
    fig = px.line(x=forecast_data['Date'].head(forecast_days), y=forecast_data['Predicted_Price'].head(forecast_days),
                  labels={'x': 'Date', 'y': 'Price'})

    # Add Loss_Profit as text labels on the plot
    for i in range(forecast_days):
        fig.add_annotation(x=forecast_data['Date'].iloc[i], y=forecast_data['Predicted_Price'].iloc[i],
                           text=f'{forecast_data["Loss_Profit"].iloc[i]:.2f}', showarrow=True, arrowhead=1)

    # Set plot title
    fig.update_layout(title=f'Loss_Profit Plot for {coin_name} in ({forecast_days} Days)')

    return fig
