"""
COMP1010 project : Your Financial advisor

z5508199 - Rose Nguyen
"""

from flask import Flask, request, session, jsonify, url_for, redirect
from functions import create_if_not_exist, write_json_file, read_json_file
from pyhtml import *
import pyhtml as h
from pyhtml import html, body, table, tr, th, td, p
from collections import defaultdict
import requests
import json
from datetime import datetime, timedelta
import os
import logging
from flask import Flask, request, render_template_string
from openai import OpenAI


##=============== prompt =============================
data_finances = None
check_response = False


##================================================================
def promt_finances(data, query):
    promt = f'''Based on the data below, answer the following questions as accurately as possible.
    Data: {data}\n
    Query: {query}
    '''
    logging.info(f"Promt : {promt}")
    return promt


# ===================== default open ai api =================
# ================ format data ====================
def format_stock_data_to_text(stock_data):
    result = []

    try:
        for symbol, data in stock_data.items():
            result.append(f"***symbols : {symbol} ({len(data)} entries)")
            for entry in data:
                result.append(
                    f"Timestamp: {entry['timestamp']}, Open: {entry['open']}, High: {entry['high']}, Low: {entry['low']}, Close: {entry['close']}, Volume: {entry['volume']}, Change Percent: {entry['change_percent']:.2f}%")
    except:
        result = ['No data']
    logging.info(f'data format : {result}')
    return "\n".join(result)


# ====================end ========================
client = OpenAI(
    api_key='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')

def chat_response(prompt):
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    logging.info(f"Chatbot Response: {completion.choices[0].message.content}")
    return completion.choices[0].message.content


# ===================== END =================


app = Flask(__name__)

app.secret_key = "givemeanhdforthiscourse"

@app.route('/', methods=["GET","POST"])
def homepage():
    response = html(
         head(
            link(rel="stylesheet", type="text/css", href=url_for('static', filename='style-login.css'))
        ),
        body(
            form(
                label(for_="username_input_id")("Username"),
                input_(type="text", id="username_input_id", name="uname"),  # Username field
                br,
                label(for_="password_input_id")("Password: "),
                input_(type="password", id="password_input_id", name="pword"),  # Password field
                br,
                input_(type="submit", formaction="/main_screen", value="Create new user"),  # Button for create
                br,
                input_(type="submit", formaction="/main_screen", value="Login")  # Button for login
            )
        )
    )
    return str(response)
@app.route("/create_login", methods=["POST"])
#might simplify this step, not gonna check password but just put name data on json
def create_login():
    response = html(
        body(
            form(
                label(for_="username_input_id")("Username"),
                input_(type="text", id="username_input_id", name="uname"),
                br,
                label(for_="password_input_id")("Password: "),
                input_(type="password", id="password_input_id", name="pword"),
                br,
                input_(type="submit", value="Create new user"),
                action="/check_create_login",
                method="POST"
            )
        )
    )
    return str(response)


@app.route("/check_login",methods=["POST"])
def check_login():
    create_if_not_exist("files/login_info.json", [])

    login_info = read_json_file("files/login_info.json")

    username = request.form.get("uname", "").strip()
    password = request.form.get("pword", "").strip()

    user = next((user for user in login_info if user.get("username") == username), None)

    if user:
        if user["password"] == password:
            session["logged_in"] = username
            return redirect(url_for("main_screen"))
        else:
            return jsonify({"status": "error", "message": "Incorrect password"}), 401
    else:
        return jsonify({"status": "error", "message": "Username does not exist"}), 404

@app.route('/main_screen',methods=["GET","POST"])
def main_screen():
    text = "Welcome to the Financial Advisor!"
    button = input_(type="submit", value="Log out", formaction="/",_class="btn")
    explore = input_(type="submit", value="Explore the Stock Market today", formaction="/program",_class="explore")

    response = html(
        head(
            link(rel="stylesheet", type="text/css", href=url_for('static', filename='style-mainpage.css'))
        ),
        body(
            h1(text),
            form(button, explore)
        )
    )
    return str(response)

# use apis from here
YF_API_KEY = "WIKR5S4I9WFKIYY9"
OPENAI_API_KEY = os.getenv(
    "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")


def generate_symbol_checkbox():
    return [
        input_(type="checkbox", name="finance", value="AAPL", id="AAPL"),
        label(for_="AAPL")("AAPL"),
        br(),
        input_(type="checkbox", name="finance", value="GOOGL", id="GOOGL"),
        label(for_="GOOGL")("GOOGL"),
        br(),
        input_(type="checkbox", name="finance", value="TSLA", id="TSLA"),
        label(for_="TSLA")("TSLA"),
        br(),
        input_(type="checkbox", name="finance", value="BTC-USD", id="BTC-USD"),
        label(for_="BTC-USD")("BTC-USD"),
        br()
    ]


def generate_region_dropdown():
    return select(name="region", id="region")(
        option(value="US")("United States"),
        option(value="CA")("Canada"),
        option(value="EU")("Europe"),
        option(value="IN")("India"),
        option(value="AU")("Australia")
    )


check_response = False


def fetch_data(symbols):
    global check_response  # Declare that we are using the global variable
    all_stock_data = {}
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    for symbol in symbols:
        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=S1308FPOSYD1B7Y7'
        r = requests.get(url)

        if r.status_code == 200:
            data = r.json()
            if 'Time Series (Daily)' in data:
                time_series = data['Time Series (Daily)']
                filtered_data = []

                # Filter data to include only the last 7 days
                for timestamp, values in time_series.items():
                    timestamp_dt = datetime.strptime(timestamp, '%Y-%m-%d')
                    if start_date <= timestamp_dt <= end_date:
                        open_price = float(values['1. open'])
                        high_price = float(values['2. high'])
                        low_price = float(values['3. low'])
                        close_price = float(values['4. close'])
                        volume = int(values['5. volume'])

                        # Calculate the percentage change
                        change_percent = ((close_price - open_price) / open_price) * 100 if open_price else 0.0

                        filtered_data.append({
                            'timestamp': timestamp,
                            'open': open_price,
                            'high': high_price,
                            'low': low_price,
                            'close': close_price,
                            'volume': volume,
                            'change_percent': change_percent
                        })

                all_stock_data[symbol] = filtered_data
            else:
                all_stock_data[symbol] = {"error": "No time series data found."}
        else:
            print(f"Failed to fetch data for {symbol}: {r.status_code}")
            all_stock_data[symbol] = {"error": f"Failed to fetch data with status code {r.status_code}"}

    check_response = True  # Set the global flag to True when data is fetched
    logging.info(f"data fetched : {all_stock_data}")
    data_finances = format_stock_data_to_text(all_stock_data)
    print(all_stock_data)
    return all_stock_data


# =================== parse to string =================
def format_stock_data_to_text(stock_data):
    result = []

    # Iterate over each symbol in the stock data dictionary
    for symbol, data_list in stock_data.items():
        result.append(f"***{symbol} : {len(data_list)} entries")  # Add the symbol and the number of entries

        # Iterate over each entry for the symbol
        for entry in data_list:
            # Format each entry's data into a readable text format
            timestamp = entry['timestamp']
            open_price = entry['open']
            high_price = entry['high']
            low_price = entry['low']
            close_price = entry['close']
            volume = entry['volume']
            change_percent = entry['change_percent']

            result.append(
                f"Timestamp: {timestamp}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}, Change Percent: {change_percent:.2f}%")

    # Join all the result lines into one text block and return it
    return "\n".join(result)


# ====================== end ==========================
def generate_results_table(data):
    if isinstance(data, dict) and 'error' in data:
        return p()(f"Error: {data['error']}")

    if not data:
        return p()("No data available")

    rows = [
        tr(
            th(style="width: 150px;")("Symbol"),
            th(style="width: 150px;")("Date"),
            th(style="width: 100px;")("Open"),
            th(style="width: 100px;")("High"),
            th(style="width: 100px;")("Low"),
            th(style="width: 100px;")("Close"),
            th(style="width: 120px;")("Change %"),
            th(style="width: 120px;")("Volume")
        )
    ]

    for symbol,stock_data in data.items():
        if isinstance(stock_data, list):
            for entry in stock_data:
                date_str = entry['timestamp']
                open_price = entry.get('open', 'N/A')
                high_price = entry.get('high', 'N/A')
                low_price = entry.get('low', 'N/A')
                close_price = entry.get('close', 'N/A')
                change_percent = entry.get('change_percent', 'N/A')
                volume = entry.get('volume', 'N/A')

                rows.append(
                    tr(
                        td(style="width: 150px;")(symbol),
                        td(style="width: 150px;")(date_str),
                        td(style="width: 100px;")(f"${float(open_price):.2f}" if open_price != 'N/A' else 'N/A'),
                        td(style="width: 100px;")(f"${float(high_price):.2f}" if high_price != 'N/A' else 'N/A'),
                        td(style="width: 100px;")(f"${float(low_price):.2f}" if low_price != 'N/A' else 'N/A'),
                        td(style="width: 100px;")(f"${float(close_price):.2f}" if close_price != 'N/A' else 'N/A'),
                        td(style="width: 120px;")(
                            f"{float(change_percent):.2f}%" if change_percent != 'N/A' else 'N/A'),
                        td(style="width: 120px;")(volume if volume != 'N/A' else 'N/A')
                    )
                )

    return table(border="1")(rows)


def generate_chatbox(current_message):
    chat_display = []

    # If there's a current message, display it
    if current_message:
        chat_display.append(p()(f"User: {current_message['user']}"))
        chat_display.append(p()(f"Bot: {current_message['bot']}"))

    else:
        chat_display.append(p()("Chat messages will appear here..."))

    return div()(
        h3()("Chat with us:"),
        div(id="chat-box")(*chat_display),
        form(method="POST")(
            textarea(id="user-message", name="user-message", rows="4", cols="30", placeholder="Type your message..."),
            p(),
            input_(type="submit", value="Send")
        )
    )


def generate_stock_checkbox():
    return div(style="display: flex; flex-wrap: wrap;")(
        div(style="margin-right: 20px;")(
            input_(type="checkbox", name="finance", value="AAPL", id="AAPL"),
            label(for_="AAPL")("AAPL")
        ),
        div(style="margin-right: 20px;")(
            input_(type="checkbox", name="finance", value="GOOGL", id="GOOGL"),
            label(for_="GOOGL")("GOOGL")
        ),
        div(style="margin-right: 20px;")(
            input_(type="checkbox", name="finance", value="TSLA", id="TSLA"),
            label(for_="TSLA")("TSLA")
        ),
        div(style="margin-right: 20px;")(
            input_(type="checkbox", name="finance", value="BTC-USD", id="BTC-USD"),
            label(for_="BTC-USD")("BTC-USD")
        )
    )


@app.route('/get-stock-data', methods=["GET", "POST"])
def stock_data():
    results_html = ""
    data_finances = 'No data available'  # Default value for data_finances

    if 'stock_data' in session:
        results_html = generate_results_table(session['stock_data'])
        data_finances = format_stock_data_to_text(session['stock_data'])  # Get text representation of the stock data

    if request.method == 'POST':
        if 'finance' in request.form and 'fetch_data' in request.form:
            symbols = request.form.getlist('finance')
            if symbols:
                stock_data = fetch_data(symbols)
                session['stock_data'] = stock_data
                data_finances = format_stock_data_to_text(stock_data)  # Update data_finances with the new data
                results_html = generate_results_table(stock_data)
            else:
                results_html = p()("Please choose at least one stock symbol.")

        user_message = request.form.get("user-message", "").strip()
        if user_message:
            prompt = promt_finances(data_finances, user_message)  # Pass the formatted stock data text to the prompt
            logging.info(f"Prompt: {prompt}")
            bot_response = chat_response(prompt)
            session['chat_response'] = {'user': user_message, 'bot': bot_response}

    current_message = session.get('chat_response', None)
    chat_display = []
    if current_message:
        chat_display.append(p()(f"User: {current_message['user']}"))
        chat_display.append(p()(f"Bot: {current_message['bot']}"))
    else:
        chat_display.append(p()("Chat messages will appear here..."))

    page_html = html(
        body(
            h1()("Stock Data and Chat Interface"),
            div(style="display: flex;")(
                div(style="width: 60%; padding-right: 20px;")(
                    form(method="POST", action="/get-stock-data")(
                        h3()("Select Stocks:"),
                        generate_stock_checkbox(),
                        p(),
                        input_(type="submit", name="fetch_data", value="Fetch Stock Data")
                    ),
                    results_html if results_html else "",
                ),
                div(style="width: 40%; padding-left: 10px; margin-right: 20px;")(
                    h3()("Chat with us:"),
                    div(id="chat-box")(*chat_display),
                    form(method="POST", action="/get-stock-data")(
                        input_(type="text",
                               id="user-message",
                               name="user-message",
                               style="width: 100%; height: 40px; padding-right: 10px; margin-right: 20px;",
                               placeholder="Type your message..."),
                        p(),
                        input_(type="submit", value="Send")
                    ),
                ),
            ),
            p(),
            a(href="/")("Back to Home"),
        )
    )

    return render_template_string(str(page_html))


@app.route('/program',methods=["GET","POST"])
def program():

    response = html(
        head(
            link(rel="stylesheet", type="text/css", href=url_for('static', filename='style-program.css'))
        ),
        body(
            h1("Welcome to the Financial Advisor"),
            br(),
            p("Select a stock symbol and region to fetch stock data and generate financial advice."),
            br(),
            a(href="/get-stock-data")("Go to Get Stock Data")
        )
    )
    return str(response)

if __name__ == '__main__':
    app.run(debug=True,port=5001)
