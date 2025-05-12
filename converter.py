import os
from dotenv import load_dotenv
import requests
import hmac
import hashlib
import time
import argparse

# Load environment variables from .env file
load_dotenv()

# Retrieve API key and secret from environment variables
COINBASE_API_KEY = os.getenv('COINBASE_API_KEY')
COINBASE_API_SECRET = os.getenv('COINBASE_API_SECRET')

def create_coinbase_signature(timestamp, method, request_path, body=''):
    message = timestamp + method + request_path + body
    hmac_key = hmac.new(COINBASE_API_SECRET.encode(), message.encode(), hashlib.sha256)
    return hmac_key.hexdigest()

def fetch_coinbase_price(crypto):
    timestamp = str(int(time.time()))
    method = 'GET'
    request_path = f'/v2/prices/{crypto}-USD/spot'
    headers = {
        'CB-ACCESS-KEY': COINBASE_API_KEY,
        'CB-ACCESS-SIGN': create_coinbase_signature(timestamp, method, request_path),
        'CB-ACCESS-TIMESTAMP': timestamp
    }
    url = 'https://api.coinbase.com' + request_path
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return float(data['data']['amount'])
    else:
        return None

def fetch_coingecko_price(crypto):
    url = 'https://api.coingecko.com/api/v3/simple/price'
    params = {
        'ids': crypto,
        'vs_currencies': 'usd'
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data[crypto]['usd']
    else:
        return None

def fetch_crypto_prices():
    prices = {}

    # Fetch Bitcoin price from Coinbase
    bitcoin_price = fetch_coinbase_price('BTC')
    if bitcoin_price is not None:
        prices['bitcoin'] = bitcoin_price

    # Fetch Ethereum price from Coinbase
    ethereum_price = fetch_coinbase_price('ETH')
    if ethereum_price is not None:
        prices['ethereum'] = ethereum_price

    # Fetch Solana price from CoinGecko
    solana_price = fetch_coingecko_price('solana')
    if solana_price is not None:
        prices['solana'] = solana_price

    return prices

def convert_to_usd(amount, crypto, prices):
    if crypto not in prices:
        raise ValueError(f"Unsupported cryptocurrency: {crypto}")
    return amount * prices[crypto]

def main():
    parser = argparse.ArgumentParser(description="Cryptocurrency to USD Converter")
    parser.add_argument('amount', type=float, help="Amount of cryptocurrency")
    parser.add_argument('crypto', choices=['bitcoin', 'ethereum', 'solana'], help="Type of cryptocurrency")
    args = parser.parse_args()

    prices = fetch_crypto_prices()
    usd_value = convert_to_usd(args.amount, args.crypto, prices)
    print(f"{args.amount} {args.crypto.capitalize()} is worth ${usd_value:.2f} USD")

if __name__ == '__main__':
    main()
