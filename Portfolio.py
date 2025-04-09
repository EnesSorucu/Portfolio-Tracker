from _datetime import datetime, timedelta
import yfinance as yf

class Portfolio:
    def __init__(self, user):
        self.user = user
        self.conn = user.conn
        self.cursor = user.cursor

    @staticmethod
    def get_extension(stock_market):
        # Map different stock markets to their respective extensions
        exchange_mapping = {
            "BIST": ".IS",
            "America": "",
            "Crypto Market": "-USD",
            "Commodity": "=F",
            "Foreign Currency": "=X"
        }
        # Return the appropriate extension based on stock market
        extension = exchange_mapping.get(stock_market, "")
        return extension

    @staticmethod
    def get_price(symbol, stockmarket, date=None):
        # Get the appropriate market extension
        extension = Portfolio.get_extension(stockmarket)
        yfinance_extension = f"{symbol}{extension}"

        # If no date is given, fetch the latest market price
        if not date:
            stock = yf.Ticker(yfinance_extension)
            stock_info = stock.info
            last_price = stock_info['regularMarketPrice']
            return round(last_price, 2)

        # If a specific date is provided, fetch historical data
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_obj = date_obj + timedelta(days=1)
        past = date_obj - timedelta(days=15)
        end_date = date_obj.strftime("%Y-%m-%d")

        df = yf.Ticker(yfinance_extension).history(start=past.strftime("%Y-%m-%d"), end=end_date) # Fetch historical data for the given date range
        return round(df["Close"].iloc[-1], 2)

    @staticmethod
    def get_stock_info(symbol, stockmarket):
        # Get the market extension for the given stock market
        extension = Portfolio.get_extension(stockmarket)
        yfinance_symbol = f"{symbol}{extension}"

        # Mapping stock exchanges to their names
        exchange_mapping = {
            "NYQ":"America",
            "NMS":"America",
            "NGM":"America",
            "NCM":"America",
            "ASE":"America",

            "IST": "BIST",

            "CCC": "Crypto Market",

            "CMX": "Commodity",
            "NYM": "Commodity",
            "USX": "Commodity",

            "CCY": "Foreign Currency"
        }

        # Get stock info from Yahoo Finance
        stock = yf.Ticker(yfinance_symbol)
        stock_info = stock.info

        # Extract company details from stock info
        company_name = stock_info.get('longName', stock_info.get('shortName', 'Name not available'))
        exchange = exchange_mapping.get(stock_info.get('exchange', 'Unknown'), "Unknown Exchange")
        currency = stock_info.get("currency", "Unknown")

        infos = {"company_name": company_name, "exchange": exchange, "currency": currency} # Return the stock information in a dictionary
        return infos

    def portfolio_infos(self, p_name):
        self.cursor.execute(f"SELECT * FROM {p_name}") # Retrieve the portfolio information from the database
        rows = self.cursor.fetchall()

        tryusd_exchange = Portfolio.get_price("TRY", "Foreign Currency") # Get the current TRY to USD exchange rate
        portfolio_value = 0
        total_profit = 0
        all_infos = {
            "general": {
                "portfolio_value": portfolio_value,
                "total_profit": total_profit,
                "profit_percentage": 0.0,
            },
            # Initialize portfolio structure for different markets
            "America": {"total": 0, "profit": 0, "exchange": "$", "portfolio_percentage": 0 ,"stocks":[]},
            "BIST": {"total": 0, "profit": 0, "exchange": "₺", "portfolio_percentage": 0 ,"stocks":[]},
            "Crypto Market": {"total": 0, "profit": 0, "exchange": "$", "portfolio_percentage": 0 ,"stocks":[]},
            "Commodity": {"total": 0, "profit": 0, "exchange": "$", "portfolio_percentage": 0 ,"stocks":[]}
        }

        # Process each stock in the portfolio
        if rows:
            for row in rows:
                symbol = row[0]
                cost = row[2]
                quantity = row[3]
                exchange = row [4]
                market = row[5]

                last_p = Portfolio.get_price(symbol, market) # Get the latest price of the stock

                p_l = (last_p - cost) * quantity # Calculate profit/loss and total value
                p_l = round(p_l, 2)

                total = quantity * last_p
                total = round(total, 2)

                percentage = ((last_p - cost) / cost) * 100 # Calculate profit percentage
                percentage = round(percentage, 2)

                if exchange == "USD": # Adjust values for USD exchange rate if necessary
                    all_infos["general"]["total_profit"] += p_l * tryusd_exchange
                    all_infos["general"]["portfolio_value"] += total * tryusd_exchange

                else:
                    all_infos["general"]["total_profit"] += p_l
                    all_infos["general"]["portfolio_value"] += total

                all_infos[market]["total"] += total # Update market-specific information
                all_infos[market]["profit"] += p_l

                # Store detailed stock info
                infos = {
                            "symbol": symbol,
                            "cost": cost,
                            "quantity": quantity,
                            "last_p": last_p,
                            "total": total,
                            "p_l": p_l,
                            "p_l_percentage": percentage}

                all_infos[market]["stocks"].append(infos)

        # Calculate profit percentage based on portfolio value
        if all_infos["general"]["portfolio_value"] > 0:
            profit_percentage = (all_infos["general"]["total_profit"]/all_infos["general"]["portfolio_value"]) * 100
            all_infos["general"]["profit_percentage"]= round(profit_percentage, 2)

        # Calculate market-specific and stock-specific portfolio percentages
        for key, info in all_infos.items():
            if key != "general":
                market_total_in_try = info["total"] * tryusd_exchange if info["exchange"] == "$" else info["total"]

                if all_infos["general"]["portfolio_value"] > 0:
                    market_percentage = (market_total_in_try / all_infos["general"]["portfolio_value"]) * 100
                    info["portfolio_percentage"] = round(market_percentage, 2)

                for stock in info["stocks"]:
                    if info["exchange"] == "$":
                        stock_total = stock["total"] * tryusd_exchange
                    else:
                        stock_total = stock["total"]

                    portfolio_percentage = (stock_total / all_infos["general"]["portfolio_value"]) * 100
                    stock["portfolio_percentage"] = round(portfolio_percentage, 2)

        return all_infos

    def trade_history(self, p_name, symbol, cost, quantity, action, stockmarket):
        # Define the table name for trade history based on portfolio name
        portfolio_trade_history_n = f"{p_name}_trade_history"

        # Retrieve stock information like company name, currency, and exchange
        infos = Portfolio.get_stock_info(symbol, stockmarket)
        s_name = infos["company_name"]
        currency = infos["currency"]
        exchange = infos["exchange"]

        today = datetime.now().strftime("%Y-%m-%d") # Get the current date for trade record

        # If trade history table exists, insert a new trade record
        if portfolio_trade_history_n in self.user.tables():
            self.cursor.execute(f"INSERT INTO {portfolio_trade_history_n} "
                                f"(date, action, symbol, s_name, exchange, currency, cost, quantity) "
                                f"VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (today, action, symbol, s_name, exchange, currency, cost, quantity))

        else: # If the table does not exist, create it and then insert the trade record
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {portfolio_trade_history_n} ("
                                f"date DATE," # Date of the trade
                                f"action TEXT,"  # Action (buy/sell)
                                f"symbol TEXT, "  # Stock symbol
                                f"s_name TEXT, "  # Company name
                                f"exchange TEXT,"  # Exchange (e.g., USD, TRY)
                                f"currency TEXT,"  # Currency type (USD, EUR, etc.)
                                f"cost REAL, "  # Cost per unit of the stock
                                f"quantity REAL) "  # Quantity of stocks bought or sold
                                )
            # Insert the trade record into the newly created table
            self.cursor.execute(f"INSERT INTO {portfolio_trade_history_n} (date, action, symbol, exchange, currency, s_name, cost, quantity) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                (today, action, symbol, exchange, currency, s_name, cost, quantity))

    def buy_stock(self, p_name, symbol, cost, quantity, stockmarket):
        # Retrieve existing stock information from the portfolio
        self.cursor.execute(f"SELECT symbol, cost, quantity FROM {p_name} WHERE symbol = ?", (symbol,))
        existing_stock = self.cursor.fetchone()

        # Get stock information like company name and currency
        stock_infos = Portfolio.get_stock_info(symbol, stockmarket)
        s_name = stock_infos["company_name"]
        currency = stock_infos["currency"]

        if existing_stock:
            # If the stock already exists in the portfolio, update its quantity and cost
            old_symbol, old_cost, old_quantity = existing_stock

            # Calculate new quantity and average cost
            new_quantity = old_quantity + quantity
            new_cost = (old_cost * old_quantity + cost * quantity) / new_quantity
            new_cost = round(new_cost, 2)

            # Update the stock entry in the portfolio
            self.cursor.execute(f"UPDATE {p_name} SET cost = ?, quantity = ? WHERE symbol = ?",
                                (new_cost, new_quantity, symbol))
            print(f"{symbol} updated: New Cost = {new_cost}, New Quantity = {new_quantity}")

        else:
            # If the stock does not exist, add it to the portfolio
            self.cursor.execute(f"INSERT INTO {p_name} VALUES (?, ?, ?, ?, ?, ?)", (symbol, s_name, cost, quantity, currency, stockmarket))
            print(f"{symbol} added to portfolio.")

        self.trade_history(p_name, symbol, cost, quantity, "buy", stockmarket) # Record the transaction in the trade history

    def sell_stock(self, p_name, symbol, cost, quantity, stockmarket):
        self.cursor.execute(f"SELECT symbol, cost, quantity FROM {p_name} WHERE symbol = ?", (symbol,)) # Retrieve existing stock information from the portfolio
        existing_stock = self.cursor.fetchone()

        if existing_stock:
            # If the stock exists, update the quantity and cost based on the sale
            old_symbol, old_cost, old_quantity = existing_stock
            new_quantity = old_quantity - quantity

            if new_quantity > 0:
                # Calculate new average cost after selling some stocks
                new_cost = (old_cost * old_quantity - cost * quantity) / new_quantity
                new_cost = round(new_cost, 2)

                # Update the portfolio with the new values
                self.cursor.execute(f"UPDATE {p_name} SET cost = ?, quantity = ? WHERE symbol = ?",
                                    (new_cost, new_quantity, symbol))

                print(f"{symbol} updated: New Cost = {new_cost}, New Quantity = {new_quantity}")
                self.trade_history(p_name, symbol, cost, quantity, "sell", stockmarket) # Record the sell transaction in the trade history

            elif new_quantity == 0:
                # If the stock quantity becomes zero, delete it from the portfolio
                self.cursor.execute(f"DELETE FROM {p_name} WHERE symbol = ?", (symbol,))
                print(f"{symbol} stock has been removed from the table because you have no more lots left.")
                self.trade_history(p_name, symbol, cost, quantity, "sell", stockmarket) # Record the sell transaction in the trade history

            # If the quantity to sell is more than what the user holds, show an error
            else:
                print(f"You don't have that many lots. Your lot count at {symbol} is: {old_quantity}")
        else:
            print("You have entered an incorrect or non-existent stock symbol") # If the stock doesn't exist, show an error


    def portfolio_status(self, p_name):
        # Retrieve the portfolio information using the portfolio_infos method
        portfolio_infos = self.portfolio_infos(p_name)
        general_info = portfolio_infos["general"]

        # Iterate through each market (except the 'general' market). Because it is a dictionary containing general information
        for market in portfolio_infos:
            if market != "general":
                if portfolio_infos[market]["total"] > 0: # Check if there is any value in the market
                    print(f"{market} Portfolio")

                    # Iterate through each stock in the market
                    for stock in portfolio_infos[market]["stocks"]:
                        # Print detailed information about the stock
                        print(f"{stock["symbol"]} \n"
                              f"value:{stock["total"]}{portfolio_infos[market]["exchange"]} "
                              f"quantity: {stock["quantity"]} "
                              f"cost: {stock["cost"]} "
                              f"price: {stock["last_p"]} "
                              f"portfolio percentage: %{stock["portfolio_percentage"]}")

                        # Display profit or loss information based on performance
                        if stock["p_l"] >= 0:
                            print(f"Profit📈: {stock["p_l"]} (+{stock["p_l_percentage"]}%)\n")

                        else:
                            print(f"Loss📉: {stock["p_l"]} ({stock["p_l_percentage"]}%)\n")
                    # Print the summary for the market (total value, profit, and market percentage)
                    print(f"*** {market} Portfolio || Total value: {portfolio_infos[market]["total"]} "
                        f"Profit: {portfolio_infos[market]["profit"]} "
                        f"Market Percentage: %{portfolio_infos[market]["portfolio_percentage"]} ***\n")
        # Print the overall portfolio value, total profit, and profit percentage
        print(f"Portfolio value: {round(general_info["portfolio_value"],2)} "
              f"Total Profit: {round(general_info["total_profit"], 2)} (%{general_info["profit_percentage"]})")

    def portfolio_status_date(self, p_name, date=datetime.now().strftime("%Y-%m-%d")):
        # Retrieve all trade history records after the specified date
        self.cursor.execute(f"SELECT * FROM {p_name}_trade_history WHERE date >= ?", (date,))
        history = self.cursor.fetchall()
        trades = []

        # Process each trade in the history
        for history_ in history:
            if history_[1] == "buy":
                # Find if the trade already exists for the symbol in the 'trades' list
                trade = next((trade for trade in trades if trade["symbol"] == history_[2]), None)
                if trade:
                    # Update existing buy trade by adding new quantity and adjusting cost
                    buy_quantity = history_[7] + trade["buy_quantity"]
                    trade["buy_cost"] = (trade["buy_cost"] * trade["buy_quantity"] + history_[6] * history_[7]) / buy_quantity
                    trade["buy_quantity"] = buy_quantity

                else:
                    # Add new buy trade to the trades list
                    trades.append({"symbol": history_[2],
                                   "buy_cost": history_[6],
                                   "sell_cost": 0,
                                   "buy_quantity": history_[7],
                                   "sell_quantity": 0,
                                   "Market": history_[4],
                                   "Exchange": history_[5]})

            elif history_[1] == "sell":
                # Find if the trade exists for the symbol in the 'trades' list
                trade = next((trade for trade in trades if trade["symbol"] == history_[2]), None)
                if trade:
                    # Update existing sell trade by adding new quantity and adjusting cost
                    sell_quantity = trade["sell_quantity"] + history_[7]
                    trade["sell_cost"] = (trade["sell_cost"] * trade["sell_quantity"] + history_[6] * history_[7]) / sell_quantity
                    trade["sell_quantity"] = sell_quantity

                else:
                    # Add new sell trade to the trades list
                    trades.append({"symbol": history_[2],
                                   "buy_cost": 0,
                                   "sell_cost": history_[6],
                                   "buy_quantity": 0,
                                   "sell_quantity": history_[7],
                                   "Market": history_[4],
                                   "Exchange": history_[5]})

            else:
                print("databasede bir sıkıntı var")
        # Retrieve the current portfolio value
        infos = self.portfolio_infos(p_name)
        total_value = infos["general"]["portfolio_value"]
        # Get the current exchange rate for TRY (Turkish Lira)
        tryusd_exchange = Portfolio.get_price("TRY", "Foreign Currency")
        p_l = 0
        # Calculate the profit and loss for each trade
        for trade in trades:
            quantity = (trade["buy_quantity"] - trade["sell_quantity"])
            if quantity < 0:
                # If there are more sell transactions than buy, calculate profit/loss for past prices
                past_p = Portfolio.get_price(trade["symbol"], trade["Market"], date)

                if trade["Exchange"] == "USD": # Adjust for USD exchange if needed
                    past_p *= tryusd_exchange
                    sell_cost = trade["sell_cost"] * tryusd_exchange

                else:
                    sell_cost = trade["sell_cost"]
                p_l += (sell_cost - past_p) * abs(quantity)

            else:
                # If there are more buy transactions than sell, calculate profit/loss for current prices
                today_p = Portfolio.get_price(trade["symbol"], trade["Market"])
                if trade["Exchange"] == "USD":
                    today_p *= tryusd_exchange
                    buy_cost = trade["buy_cost"] * tryusd_exchange

                else:
                    buy_cost = trade["buy_cost"]
                p_l += (today_p - buy_cost) * quantity
            # Calculate the profit/loss for trades that have both buy and sell transactions
            trade_p_l = (trade["buy_cost"] - trade["sell_cost"]) * min(trade["buy_quantity"], trade["sell_quantity"])
            p_l += trade_p_l

        # Calculate the number of days between the provided date and today
        today = datetime.now().date()
        date = datetime.strptime(date, "%Y-%m-%d").date()
        last_days = today - date

        # Calculate the profit/loss percentage based on the total portfolio value
        percentage = round(p_l/total_value *100, 2)

        # Print the profit/loss for the given period with percentage
        if p_l >= 0:
            print(f"{round(p_l, 2)}₺ (+{percentage})% Last {last_days.days} days")
        else:
            print(f"{round(p_l, 2)}₺ ({percentage})% Last {last_days.days} days")