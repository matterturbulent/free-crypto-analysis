# Import modules
from urllib.request import urlopen
import json
import sys
import pandas as pd
import numpy as np

# Introduction
print("""_________________________________
\n\n\033[1mFree Crypto Analysis\033[0m\n
This program provides you financial analyis of crypto
tokens. It leverages the free CoinGecko API. Specify 
the tokens you want to analyze, the historical time
period, and the investment duration such as month. 

The analyses calculated are:
    • Average Returns
    • Asset Volatility (Risk)
    • Correlation Between Assets 

Made by @MatterTurbulent\n""")

# Enter parameters for querying Coingecko API
user_token_input = input("""_________________________________\n
\033[1mSpecify the Tokens\033[0m\n
What tokens do you want to analyze? When analyzing multiple tokens, 
seperate each with a comma. Find the token ID on its CoinGecko page 
in the top right 'Info box'. Input lowercase (i.e 'ethereum, bitcoin'). 
https://www.coingecko.com/\n\n""")   

# Split the string into a list of strings based on the comma
user_token_list = user_token_input.replace(" ", "").split(',')

# Check if the IDs are all among the viable coingecko IDs. Raise an exception if at least one isn't.
api_ids = "https://api.coingecko.com/api/v3/coins/list?include_platform=false"
viable_ids = urlopen(api_ids)
ids_json = json.loads(viable_ids.read())

for proposed_token in user_token_list:
    found = False
    for viable_token in ids_json:
        if proposed_token == viable_token["id"]:
            found = True
            break
    if not found:
        sys.exit("""Error, you've submitted a token ID that doesn't match IDs at CoinGecko.
Double-check the ID spelling and run this program again.""")

# Input integer representing how far back the user wants to analyze
historical_period = input("""

\033[1mSpecify the Historical Period\033[0m

How many days back do you want to analyze? I.e. '90' or '180'.
You MUST input and integer.\n\n""")

# Convert input to an integer
try:
    historical_period = int(historical_period)
except ValueError:
    print("\nError: You must input an integer.")
    sys.exit(1)
    
# Input integer representing the user's investment duration
investment_duration = input("""

\033[1mSpecify the Investment Duration\033[0m

How long are you considering holding tokens, in days? I.e. '30' or '90'.
You MUST input an integer.\n\n""")

# Convert input to an integer
try:
    investment_duration = int(investment_duration)
except ValueError:
    print("\nError: You must input an integer.")
    sys.exit(1)

#Parsing and preparing data 
dataframe = pd.DataFrame()

for token_id in user_token_list:
    
    # Store the URL in token_prices as parameter for urlopen
    gecko_api_response = f"https://api.coingecko.com/api/v3/coins/{token_id}/market_chart?vs_currency=usd&days={historical_period}&interval=daily"
    
    # Store the response of URL
    market_data = urlopen(gecko_api_response)
  
    # Storing the JSON response from url in data
    data_json = json.loads(market_data.read())
    
    # List comprehension to loop through the json and pull the price within each pair of the 2D list
    # Sppend to daily_prices_list and then add as a column to the dataframe
    prices = data_json["prices"]
    daily_prices_list = []
    for price in prices:
        daily_prices_list.append(price[1])
    
    # Trim off excess days if index mismatch
    cleaned_list = daily_prices_list[:(historical_period)]
    
    # Add token data to dataframe
    dataframe[token_id] = cleaned_list
    
# Slice the DataFrame based on the desired investment period
interval_data = dataframe.iloc[::investment_duration]
    
print(f"""_________________________________
\n\n\033[1mHere is the market data:\033[0m\n
{interval_data}
_________________________________
""")

# Basic Financial Statistics

selected=list(dataframe.columns[0:])
returns_daily = dataframe[selected].pct_change()

expected_returns = returns_daily.mean().mul(100).round(3).astype(str) + "%"

cov_daily = returns_daily.cov()

single_asset_std = np.sqrt(np.diagonal(cov_daily))
single_asset_std = pd.Series(single_asset_std, index=user_token_list).mul(100).round(3).astype(str) + "%" 

print(f"""\033[1mAverage Returns\033[0m\n
Average % returns when holding these tokens over a {investment_duration}-day investment
period, per the past {historical_period} days of market data:\n
{expected_returns}\n\n""")

print(f"""\033[1mStandard Deviation\033[0m\n
Standard deviation of prices for the tokens, when holding these tokens 
over a {investment_duration}-day investment period, per the past {historical_period} days of market data:\n
{single_asset_std}\n\nLarger number means the token is more volatile.\n\n""")

print(f"""\033[1mAre the Assets Correlated?\033[0m\n
Covariance between these tokens:\n
{cov_daily}\n
The degree to which one token's price moves when the another's moves
Positive number indicates they move in the same direction, Negative 
means they move inversely.""")

# Outro 
print("""

_________________________________

Made by @MatterTurbulent

If you liked this tool and want to send the creator a tip, send to
the wallet address 0xC51f78e7a599C75a6AF11696Cd232A3d4EF33549 
on Ethereum or Optimism\n\n🌔""")