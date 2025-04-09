from User import User
from Portfolio import Portfolio

# Creating a user "enes"
User = User("Enes")

# Creating portfolios for the user
Portfolios = Portfolio(User)

# A new portfolio is created: "Enes_Capital_Portföy"
User.create_new_portfolio("Enes_Capital_Portföy")

# Adding stocks to the "Enes_Capital_Portföy" portfolio
Portfolios.buy_stock("Enes_Capital_Portföy", "THYAO", 300.25, 30, "BIST")  # Buying Turkish Airlines (THYAO) from BIST
Portfolios.buy_stock("Enes_Capital_Portföy", "BTC", 78123.26, 0.01, "Crypto Market")  # Buying Bitcoin (BTC) from Crypto Market
Portfolios.buy_stock("Enes_Capital_Portföy", "TSLA", 232.01, 0.6, "America")  # Buying Tesla (TSLA) from the American stock market
Portfolios.buy_stock("Enes_Capital_Portföy", "SI", 29.93, 0.6, "Commodity")  # Buying Silver (SI) from Commodity market

# Selling stocks from "Enes_Capital_Portföy" portfolio
Portfolios.sell_stock("Enes_Capital_Portföy", "THYAO", 301.25, 10, "BIST")  # Selling 10 shares of THYAO from BIST

# Viewing the current status of "Enes_Capital_Portföy" portfolio
Portfolios.portfolio_status("Enes_Capital_Portföy")

# Viewing the portfolio status of "Enes_Capital_Portföy" on a specific date (2025-04-08)
Portfolios.portfolio_status_date("Enes_Capital_Portföy", "2025-04-08")

# Closing the connection
User.close_conn()
