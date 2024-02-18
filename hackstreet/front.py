import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
from alpha_vantage.fundamentaldata import FundamentalData
from stocknews import StockNews

# Custom CSS styles
st.markdown(
    """
    <style>
        body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            background-image: url('file:///C:/Users/HP/Desktop/hackstreet/images.jfif');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }

        .sidebar .sidebar-content {
            background-color:  #000000; /* Change sidebar background color here */
            padding-top: 20px; /* Adjust top padding */
        }

        .sidebar .sidebar-content .stTextInput>div>div>input {
            background-color: #34495e; /* Change sidebar input background color here */
            border: none;
            border-radius: 5px;
            padding: 8px;
        }

        .main .block-container {
            max-width: 1200px;
            margin: auto;
            padding: 20px;
        }

        .main .block-container .stButton>button {
            background-color: #3498db;
            color: #fff;
            border-radius: 5px;
            padding: 10px 20px;
            border: none;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }

        .main .block-container .stButton>button:hover {
            background-color: #2980b9;
        }

        .main .block-container .stDataFrame {
            overflow-x: auto;
        }

        .main .block-container .stDataFrame table {
            border-collapse: collapse;
            width: 100%;
        }

        .main .block-container .stDataFrame table th,
        .main .block-container .stDataFrame table td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }

        .main .block-container .stDataFrame table th {
            background-color: #f2f2f2;
        }

        .toggle-container {
            margin-top: 20px;
        }
        </style>
    """,
    unsafe_allow_html=True
)

st.title("STOCK DASHBOARD")

# Sidebar inputs
ticker = st.sidebar.text_input('Ticker')
start_date = st.sidebar.date_input('Start date')
end_date = st.sidebar.date_input('End date')

# Check if the input fields are empty
if not ticker or not start_date or not end_date:
    st.warning("Please enter a value for Ticker, Start date, and End date.")
else:
    # Download data
    data = yf.download(ticker, start=start_date, end=end_date)

    # Check if data is not empty
    if not data.empty:
        # Create a line chart for stock price movements
        fig = px.line(data, x=data.index, y='Adj Close', title=f'Stock Price Movements for {ticker}')
        st.plotly_chart(fig)
    else:
        st.write("No data available for the selected dates or ticker.")

    # Toggle for pricing data section
    if st.button('Toggle Pricing Data'):
        st.header("Pricing Data")
        if not data.empty:
            # Calculate percentage change
            data2 = data.copy()
            data2['% change'] = data['Adj Close'].pct_change()
            data2.dropna(inplace=True)
            st.write(data2)

            # Calculate annual return
            annual_return = data2['% change'].mean() * 252 * 100
            st.write("Annual Return:", annual_return, '%')

            # Calculate standard deviation
            stdev = np.std(data2['% change']) * np.sqrt(252)
            st.write("Standard Deviation:", stdev * 100, '%')

            # Calculate risk-adjusted return
            risk_adj_return = annual_return / (stdev * 100)
            st.write("Risk-adjusted Return:", risk_adj_return)
        else:
            st.write("No pricing data available.")

    # Toggle for fundamental data section
    if st.button('Toggle Fundamental Data'):
        st.header("Fundamental Data")
        key = 'WYPVWETGNFQCACI7'  # You may need to replace this with your Alpha Vantage API key
        fd = FundamentalData(key, output_format='pandas')

        # Fetch balance sheet data
        st.subheader("Balance Sheet")
        balance_sheet_data = fd.get_balance_sheet_annual(ticker)
        if isinstance(balance_sheet_data, tuple):
            balance_sheet_df = balance_sheet_data[0]  # Extract the DataFrame from the tuple
            st.dataframe(balance_sheet_df)
        else:
            st.write("No balance sheet data available.")

        # Fetch income statement data
        st.subheader("Income Statement")
        income_statement_data = fd.get_income_statement_annual(ticker)
        if isinstance(income_statement_data, tuple):
            income_statement_df = income_statement_data[0]  # Extract the DataFrame from the tuple
            st.dataframe(income_statement_df)
        else:
            st.write("No income statement data available.")

        # Fetch cash flow statement data
        st.subheader("Cash Flow Statement")
        cash_flow_data = fd.get_cash_flow_annual(ticker)
        if isinstance(cash_flow_data, tuple):
            cash_flow_df = cash_flow_data[0]  # Extract the DataFrame from the tuple
            st.dataframe(cash_flow_df)
        else:
            st.write("No cash flow statement data available.")

    # Toggle for news section
    if st.button('Toggle News'):
        st.header(f'News of {ticker}')
        sn = StockNews(ticker, save_news=False)
        df_news = sn.read_rss()
        for i in range(min(10, len(df_news))):
            st.subheader(f'News {i + 1}')
            st.write(df_news['published'][i])
            st.write(df_news['title'][i])
            st.write(df_news['summary'][i])
            title_sentiment = df_news['sentiment_title'][i]
            st.write(f'Title Sentiment: {title_sentiment}')
            news_sentiment = df_news['sentiment_summary'][i]
            st.write(f'News Sentiment: {news_sentiment}')