# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


# def print_hi(name):
#     # Use a breakpoint in the code line below to debug your script.
#     print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
# if __name__ == '__main__':
#     print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/


from pandas_datareader import data as web
import pandas as pd
import numpy as np
import json
import yfinance as yf
from numpy import ones
from datetime import datetime
import matplotlib.pyplot as plt
from pypfopt.efficient_frontier import EfficientFrontier
from pypfopt import risk_models, objective_functions
from pypfopt import expected_returns
import mysql.connector
from mysql.connector import Error
from stock import stock

from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices

from flask import render_template, request, jsonify, Response
import connexion
import requests

# # Create the application instance
# app = connexion.App(__name__, specification_dir='./')
#
# # Read the swagger.yml file to configure the endpoints
# app.add_api('swagger.yml')
#
# # Create a URL route in our application for "/"
# @app.route('/')
# def home():
#     """
#     This function just responds to the browser ULR
#     localhost:5000/
#     :return:        the rendered template 'home.html'
#     """
#     return render_template('home.html')
#
# # If we're running in stand alone mode, run the application
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)

# Create stocks list
stocks = []

# sectos
sectors = []

# portfolio tickers
assets = []

# number of stocks in the portfolio
num_stocks_portfolio = 7


plt.style.use('fivethirtyeight')

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='babyinvestor',
                                         user='root',
                                         password='root')
    sql_select_Query = "select * from dow_30"
    cursor = connection.cursor()
    cursor.execute(sql_select_Query)
    records = cursor.fetchall()
    print("Total number of rows in dow 30 is: ", cursor.rowcount)

    print("\nPrinting each stock record")

    counter = 0

    for row in records:
        counter += 1
        stocks.append(stock(counter, row[0], row[1], row[2], row[3], row[4], row[5]))

    for obj in stocks:
        print(obj.i, obj.ticker, obj.sector, sep=' ')

    print(max(obj.stock_return for obj in stocks))

    for num in range(0, len(stocks), 1):
        for x in stocks:
            if x.stock_return == max(obj.stock_return for obj in stocks):
                print("i found it!")
                stocks.remove(x)
                if sectors.count(x.sector) < 2:
                    if len(assets) < num_stocks_portfolio:
                        assets.append(x.ticker)
                        sectors.append(x.sector)
                    break
                else:
                    print("yawa")
                    x = None
                # if len(portfolio_tickers) < num_stocks_portfolio:
                #     portfolio_tickers.append()

                # stocks.remove(

    for x in assets:
        print(x)

    for x in sectors:
        print(x)





except Error as e:
    print("Error reading data from MySQL table", e)
finally:
    if (connection.is_connected()):
        connection.close()
        cursor.close()
        print("MySQL connection is closed")


# assets = ["V", "AAPL", "HD", "UNH", "MSFT", "NKE", "DIS"]


def get_symbol(symbol):
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)

    result = requests.get(url).json()

    for x in result['ResultSet']['Result']:
        if x['symbol'] == symbol:
            return x['name']


x = len(assets)

weights_per_stock = 1 / x

weights = []

for u in assets:
    print(weights_per_stock)
    weights.append(weights_per_stock)

print(weights)

# Get the stock starting date
stockStartDate = '2013-01-01'
# Get the stocks ending date aka todays date and format it in the form YYYY-MM-DD
today = datetime.today().strftime('%Y-%m-%d')

df = pd.DataFrame()

# Create a dataframe to store the adjusted close price of the stocks
df = pd.DataFrame()
# Store the adjusted close price of stock into the data frame
for stock in assets:
    df[stock] = web.DataReader(stock, data_source='yahoo', start=stockStartDate, end=today)['Adj Close']

# print(df)

# Show the daily simple returns, NOTE: Formula = new_price/old_price - 1
returns = df.pct_change()
print(returns)

# Generate Covariance matrix for the selected stocks
cov_matrix_annual = returns.cov() * 252
print(cov_matrix_annual)

# Calculate  portfolio Variance
port_variance = np.dot(weights, np.dot(cov_matrix_annual, weights))
print(port_variance)

mu = expected_returns.mean_historical_return(df)  # returns.mean() * 252
S = risk_models.sample_cov(df)  # Get the sample covariance matrix

ef = EfficientFrontier(mu, S)
ef.add_objective(objective_functions.L2_reg, gamma=0.4)

#Maximize the Sharpe ratio
weights = ef.max_sharpe()
#weights = ef.efficient_risk(0.20, False)
# Get the weights
cleaned_weights = ef.clean_weights()
# print(cleaned_weights)
# ef.portfolio_performance(verbose=True)

print(json.dumps([dict(ticker=pn, weight=cleaned_weights[pn]) for pn in cleaned_weights]))


# Create the application instance
app = connexion.App(__name__, specification_dir='./')


# Read the swagger.yml file to configure the endpoints
# app.add_api('swagger.yml')

# Create a URL route in our application for "/"
@app.route('/', methods=['GET'])
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/
    :return:        the rendered template 'home.html'
    """
    resp = Response(json.dumps({'Assets': [dict(ticker=pn, name=get_symbol(pn), weight=cleaned_weights[pn]) for pn in cleaned_weights]}))
    return resp;
    # return jsonify(Assets = json.dumps([dict(ticker=pn, weight=cleaned_weights[pn]) for pn in cleaned_weights]))


# If we're running in stand alone mode, run the application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
