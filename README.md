# Portfolio Tracker 📈

This project is a portfolio tracking system designed for investors to follow their stock trading history, manage their portfolios, and analyze historical performance. The project is developed using Python and SQLite.

This system supports various markets, including:
- **BIST (Borsa İstanbul)** for Turkish stock market investments
- **US Stock Markets** (like NYSE, NASDAQ) for American stocks
- **Crypto Markets** (like Binance, Coinbase) for cryptocurrency trading
- **Commodity Markets** (like NYMEX, COMEX) for commodities such as Gold, Silver, Crude Oil, etc.

## 🔍 Features

- **Portfolio Creation**: Users can create portfolios under custom names.
- **Stock Buying / Selling**: Add stocks to your portfolio or execute sell transactions.
- **Transaction Logging**: All buy/sell transactions are logged in detail and stored persistently in an SQLite database.
- **Automatic Company Info Retrieval**: The system fetches company name, exchange, and currency details automatically using the stock symbol.
- **Multiple Portfolio Support**: Users can create and manage multiple portfolios.

---

## 📂 Database Structure

The project uses two dynamically created tables per portfolio within an SQLite database, based on the portfolio name.

### 1. `{portfolio_name}` (Portfolio Status)

This table stores the current holdings and basic details of the portfolio.

| Column   | Data Type | Description                           |
|----------|-----------|---------------------------------------|
| symbol   | TEXT      | Stock symbol                          |
| name     | TEXT      | Company name                          |
| cost     | REAL      | Average purchase price                |
| quantity | REAL      | Quantity owned                        |
| exchange | TEXT      | Exchange currency (e.g., TRY)         |
| market   | TEXT      | Market name (e.g., BIST)              |

#### Sample Data (for the `myportfolio` table):

| symbol | name                                   | cost   | quantity | exchange | market |
|--------|----------------------------------------|--------|----------|----------|--------|
| THYAO  | Türk Hava Yollari Anonim Ortakligi     | 270    | 300      | TRY      | BIST   |

---

### 2. `{portfolio_name}_trade_history` (Transaction History)

This table records the details of every transaction (buy or sell) performed.

| Column   | Data Type | Description                                  |
|----------|-----------|----------------------------------------------|
| date     | DATE      | Transaction date (YYYY-MM-DD)                |
| action   | TEXT      | Transaction type ("buy" or "sell")           |
| symbol   | TEXT      | Stock symbol                                 |
| s_name   | TEXT      | Company name                                 |
| exchange | TEXT      | Exchange where the trade was executed        |
| currency | TEXT      | Transaction currency (e.g., USD, TRY)         |
| cost     | REAL      | Unit price used for the transaction          |
| quantity | REAL      | Quantity bought or sold                      |

#### Sample Data (for the `myportfolio_trade_history` table):

| date       | action | symbol | s_name                                | exchange | currency | cost   | quantity |
|------------|--------|--------|---------------------------------------|----------|----------|--------|----------|
| 2025-04-09 | buy    | THYAO  | Türk Hava Yollari Anonim Ortakligi  | BIST     | TRY      | 270  | 300     |

---

## ℹ️ Overview

The system allows users to:

- Track which stocks they purchased.
- Record the dates and prices of transactions.
- Evaluate their portfolio’s current value and performance based on detailed, logged transactions.

All data is stored persistently in an SQLite database. Each portfolio is associated with two tables:
- A table for the current portfolio status.
- A table for transaction history.

This design ensures fast and reliable data access without using CSV or file-based storage methods.

---

## 📖 Additional Notes

- **Data Retrieval**: Stock prices and company details are fetched via the `yfinance` library.
- **Currency Conversion**: If a transaction is made in USD, the system retrieves the current TRY/USD exchange rate to convert values accordingly.
- **Multiple Portfolios**: Users can manage more than one portfolio simultaneously, with dynamic table creation for each portfolio.

---
### Important Notes

- **Stock Symbols**: Stock symbols are directly retrieved using their respective tickers, for example, `THYAO` for Turkish Airlines or `AAPL` for Apple.
  
- **Commodity Symbols**: Commodities are also tracked by their respective symbols, but please note that for commodities like Gold, Silver, Oil, etc., you should **not** refer to them as simple names like "Silver" or "Gold". Instead, use their specific symbols:

  - **Gold**: `GC` (Gold Futures)
  - **Silver**: `SI` (Silver Futures)
  - **Brent Crude Oil**: `BZ` (Brent Oil Futures)
  - **WTI Crude Oil**: `CL` (West Texas Intermediate Oil)
  - **Natural Gas**: `NG` (Natural Gas Futures)
  - **Copper**: `HG` (Copper Futures)
  ### Usage Examples in `main.py`

  ---

## 📞 Contact

If you encounter any issues, have questions, or need further assistance, please feel free to reach out:

- **Email**: sorucu89@gmail.com  
- **GitHub Issues**: Open an issue on this repository

Your feedback and contributions are most welcome!

---

## License

This project is licensed under the MIT License.
