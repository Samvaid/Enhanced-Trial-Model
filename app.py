import streamlit as st
import math
from scipy.stats import norm
import yfinance as yf
import plotly.graph_objects as go

# Black-Scholes Formula
def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = (math.log(S / K) + (r + 0.5 * sigma**2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    if option_type == "call":
        return S * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        return K * math.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

# Plot Interactive Stock Chart
def plot_stock_chart(ticker, period):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    # Calculate Percentage Change
    start_price = hist['Close'].iloc[0]
    end_price = hist['Close'].iloc[-1]
    percentage_change = ((end_price - start_price) / start_price) * 100

    # Determine Color for Percentage Change
    color = "green" if percentage_change > 0 else "red"

    # Plot with Plotly
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist['Close'], mode='lines', name='Close Price'
    ))
    fig.update_layout(
        title=f"{ticker.upper()} Stock Price ({period.upper()})",
        xaxis_title="Date",
        yaxis_title="Price",
        hovermode="x unified",
        template="plotly_dark"
    )

    # Display Percentage Change
    st.markdown(
        f'<p style="color:{color}; font-size:20px;">Percentage Change: {percentage_change:.2f}%</p>',
        unsafe_allow_html=True
    )
    return fig

# Streamlit UI
st.set_page_config(page_title="Enhanced Black-Scholes App", layout="wide")
st.title("Enhanced Black-Scholes Pricing Model")

# Inputs
ticker = st.text_input("Enter Stock Ticker Symbol", value="AAPL")
K = st.number_input("Strike Price", value=100.0, format="%.2f")
T = st.number_input("Time to Maturity (Years)", value=1.0, format="%.2f")
r = st.number_input("Risk-Free Interest Rate (r)", value=0.05, format="%.3f")

# Fetch stock data
stock = yf.Ticker(ticker)
hist = stock.history(period="1y")
S = hist["Close"][-1]  # Current price
daily_returns = hist["Close"].pct_change().dropna()
default_volatility = daily_returns.std() * math.sqrt(252)  # Annualized volatility
sigma = st.number_input("Volatility (σ)", value=default_volatility, format="%.3f")

# Results
call_price = black_scholes(S, K, T, r, sigma, option_type="call")
put_price = black_scholes(S, K, T, r, sigma, option_type="put")

st.write("### Option Prices:")
st.success(f"CALL Option Price: ${call_price:.2f}")
st.error(f"PUT Option Price: ${put_price:.2f}")

# Time Frame Selector (Moved here)
st.write("### Select Time Frame for Stock Chart")
time_frame = st.selectbox(
    "Time Frame", 
    options=["5y", "3y", "1y", "ytd", "6mo", "3mo", "1mo", "1wk"], 
    index=2
)

# Stock Chart with Percentage Change
st.write("### Stock Chart")
fig = plot_stock_chart(ticker, time_frame)
st.plotly_chart(fig, use_container_width=True)
