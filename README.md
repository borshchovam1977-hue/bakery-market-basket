# 🥐 Bakery Market Basket Analysis

Interactive Streamlit dashboard for analyzing customer purchasing patterns at "The Bread Basket" bakery in Edinburgh.

## 📊 Features

- **Item Frequency Analysis** - See the most popular items
- **Market Basket Analysis** - Discover items frequently bought together
- **Time of Day Analysis** - Understand purchasing patterns by daypart
- **Interactive Filters** - Filter by time of day and specific items

## 🚀 Live Demo

[Open App](https://your-app-name.streamlit.app)

## 📁 Dataset

The dataset contains 20,507 entries with over 9,000 transactions from October 2016 to April 2017.

**Columns:**
- `TransactionNo` - Unique transaction identifier
- `Items` - Items purchased
- `DateTime` - Date and time of transaction
- `Daypart` - Part of the day (Morning, Afternoon, Evening, Night)
- `DayType` - Weekend or Weekday

## 🛠️ Installation

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📝 License

MIT License
