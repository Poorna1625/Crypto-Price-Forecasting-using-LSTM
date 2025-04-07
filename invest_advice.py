import csv
import pandas as pd

def Invest_advice(selected_coin, time_horizon, target_profit, investment_amount, risk_tolerance):
    # Filenames mapped to coin symbols
    filenames = {
        'BTC': 'BTC_forecast.csv',
        'ETH': 'ETH_forecast.csv',
        'DOGE': 'DOGE_forecast.csv',
        'LIT': 'LIT_forecast.csv',
    }
    filename = filenames.get(selected_coin)
    if filename is None:
        return None  # Selected coin not found

    forecast_data = pd.read_csv(filename)
    forecast_days = 0
    total_profit = 0
    for _, row in forecast_data.iterrows():
        profit = row['Loss_Profit']
        total_profit += profit
        forecast_days += 1

    daily_profit = total_profit / forecast_days
    expected_profit = daily_profit * time_horizon  # Use time_horizon instead of days

    # You can also add logic here to take into account the investment_amount and risk_tolerance

    if expected_profit >= target_profit:
        return [selected_coin]  # Return the selected coin as the investment option

    return None  # No combination of coins can reach the target profit


