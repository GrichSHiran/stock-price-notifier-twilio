import requests
import os
# import html

from twilio.rest import Client
# from twilio.http.http_client import TwilioHttpClient


# --- FUNCTIONS ---
def fetch_json(url: str, params: dict) -> dict:
    """
    Fetch json object via an API REST call;
    Return a Python dictionary
    """
    response = requests.get(url=url, params=params)
    print(f"\n---STATUS: {response.status_code}---\n")
    response.raise_for_status()

    return response.json()


# --- CONSTANTS ---
STOCK = 'TSLA'
COMPANY_NAME = 'Tesla Inc'
THRESHOLD = 0.05

STOCK_ENDPOINT = r'https://www.alphavantage.co/query'
NEWS_ENDPOINT = r'https://newsapi.org/v2/everything'

# Use environment variables for the following constants
FROM_NUMBER = os.environ.get('FROMNUMBER')
TO_NUMBER = os.environ.get('TONUMBER')

TWILIO_ID = os.environ.get('TWILIOACCSID')
TWILIO_API_KEY = os.environ.get('TWILIOAUTHTOKEN')
AV_API_KEY = os.environ.get('AVAPI')
NEWS_API_KEY = os.environ.get('NEWSAPI')

# --- MAIN ---
stock_params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK,
    'apikey': AV_API_KEY,
}

stock_dict = fetch_json(STOCK_ENDPOINT, stock_params)

daily_dict = stock_dict['Time Series (Daily)']
yesterday, daybefore = list(daily_dict.keys())[0:2]

# print(f"\n--- {yesterday} & {daybefore} ---")

ystr_closing = float(daily_dict[yesterday]['4. close'])
dyb4_closing = float(daily_dict[daybefore]['4. close'])

# print(f"Yesterday: {ystr_closing}")
# print(f"Daybefore: {dyb4_closing}")
# print(type(ystr_closing))

threshold = ystr_closing * THRESHOLD
difference = abs(ystr_closing - dyb4_closing)
diff_pcent = "{:.0%}".format((difference/ystr_closing))

is_over = difference > threshold
is_up = ystr_closing > dyb4_closing
symbol = "🔺" if is_up else "🔻"

# print(f"Threshold: {threshold}")
# print(f"Difference: {difference}){diff_pcent}")
# print(f"Is Over 5%: {is_over_5pcent}")

is_over = True    # Override a boolean for testing
if is_over:

    # print("!!--- GET NEWS ---!!")
    news_params = {
        'apiKey': NEWS_API_KEY,
        'q': COMPANY_NAME,
        'pageSize': 3,
    }

    news_dict = fetch_json(NEWS_ENDPOINT, news_params)
    articles = news_dict['articles']

    # proxy_client = TwilioHttpClient()
    # proxy_client.sesion.proxies = {'https': os.environ['https_proxy']}

    client = Client(TWILIO_ID, TWILIO_API_KEY)
    # client = Client(TWILIO_ID, TWILIO_API_KEY, http_client=proxy_client)

    for artc in articles:

        title = artc['title']
        descb = artc['description']
        link = artc['url']
        # pblsh = artc['publishedAt']

        text = f"{STOCK}: {symbol}{diff_pcent}\nHeadline: {title}\nBrief: {descb}\nLink: {link}"

        message = client.messages.create(
            body=text,
            from_=FROM_NUMBER,
            to=TO_NUMBER
        )

#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.

or

TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

