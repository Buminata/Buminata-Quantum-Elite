import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import os
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh
from xgboost import XGBRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPRegressor

# Load environment variables
load_dotenv()

# ==============================================================================
# BUMINATA QUANTUM ELITE v7.0 (QUANTUM PROJECTION CORE)
# ==============================================================================

# --- APP CONFIG ---
st.set_page_config(
    page_title="Buminata Quantum Elite",
    page_icon="📉",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- TRADINGVIEW-STYLE AESTHETICS ---
st.markdown("""
<style>
    .stApp { background-color: #0c0d10; color: #d1d4dc; }
    [data-testid="stHeader"] { background-color: #0c0d10; }
    [data-testid="stSidebar"] { background-color: #131722; border-right: 1px solid #2a2e39; }
    
    .advisor-card {
        background: linear-gradient(145deg, #1e222d, #131722);
        border: 1px solid #2a2e39;
        padding: 24px;
        border-radius: 12px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    }
    
    .signal-header { font-size: 0.9rem; color: #80848e; text-transform: uppercase; letter-spacing: 1.5px; }
    .price-value { font-size: 2rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    
    .buy-zone { color: #00ff88; text-shadow: 0 0 10px rgba(0, 255, 136, 0.3); }
    .sell-zone { color: #ff3366; text-shadow: 0 0 10px rgba(255, 51, 102, 0.3); }
    .neutral-zone { color: #80848e; }
    
    h1, h2, h3 { color: #eef400 !important; font-family: 'Inter', sans-serif; }
</style>
""", unsafe_allow_html=True)

# --- QUANTUM INTELLIGENCE ENGINE ---
class QuantumProjectionEngine:
    @staticmethod
    @st.cache_data(ttl=1)
    def fetch_data(ticker, timeframe="1m", period="1d"):
        try:
            data = yf.download(ticker, period=period, interval=timeframe, progress=False)
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            return data
        except Exception:
            return None

    @staticmethod
    def compute_advanced_indicators(df):
        df = df.copy()
        for i in range(1, 4):
            df[f'Lag_{i}'] = df['Close'].shift(i)
        
        # Volatility & Momentum
        df['ATR'] = (df['High'] - df['Low']).rolling(14).mean()
        df['EMA9'] = df['Close'].ewm(span=9).mean()
        df['EMA21'] = df['Close'].ewm(span=21).mean()
        df['EMA50'] = df['Close'].ewm(span=50).mean()
        
        # MACD
        df['EMA12'] = df['Close'].ewm(span=12).mean()
        df['EMA26'] = df['Close'].ewm(span=26).mean()
        df['MACD'] = df['EMA12'] - df['EMA26']
        df['Signal_L'] = df['MACD'].ewm(span=9).mean()
        
        # Bollinger Bands
        df['MA20'] = df['Close'].rolling(20).mean()
        df['Std20'] = df['Close'].rolling(20).std()
        df['Upper_B'] = df['MA20'] + (df['Std20'] * 2)
        df['Lower_B'] = df['MA20'] - (df['Std20'] * 2)
        
        # S/R Detection
        df['Sup'] = df['Low'].rolling(window=15).min()
        df['Res'] = df['High'].rolling(window=15).max()
        
        # Simple Pattern Recognition
        # Engulfing
        df['Engulfing'] = ((df['Close'] > df['Open']) & (df['Open'].shift(1) > df['Close'].shift(1)) & 
                           (df['Close'] > df['Open'].shift(1)) & (df['Open'] < df['Close'].shift(1)))
        
        df['RSI'] = 100 - (100 / (1 + (df['Close'].diff().where(df['Close'].diff() > 0, 0).rolling(14).mean() / 
                                     df['Close'].diff().where(df['Close'].diff() < 0, 0).abs().rolling(14).mean().replace(0, 0.001))))
        return df.dropna()

    @staticmethod
    def calculate_correlation(df1, ticker2):
        """Analyze live correlation with market benchmark."""
        try:
            df2 = QuantumProjectionEngine.fetch_data(ticker2, period="1d", timeframe="1m")
            if df2 is not None and not df2.empty:
                # Sync indexes
                combined = pd.concat([df1['Close'], df2['Close']], axis=1).dropna()
                combined.columns = ['Asset', 'Benchmark']
                corr = combined.corr().iloc[0, 1]
                return float(corr)
            return 0.0
        except: return 0.0

    @staticmethod
    def forecast_quantum_target(df):
        """Hybrid Quantum Ensemble: XG-3 + Deep Neural Network."""
        try:
            train_df = df.copy().tail(1200)
            features = ['Open', 'High', 'Low', 'Close', 'Volume', 'RSI', 'ATR', 'EMA9', 'EMA21', 'EMA50', 'MACD', 'Lag_1']
            
            X = train_df[features]
            y = train_df['Close'].shift(-5)
            valid_idx = y.dropna().index
            X_train = X.loc[valid_idx]
            y_train = y.loc[valid_idx]
            
            # --- MODEL 1: XGBOOST (Gradient Boosting) ---
            model_xg = XGBRegressor(n_estimators=100, max_depth=6, learning_rate=0.05, random_state=42)
            model_xg.fit(X_train, y_train)
            
            # --- MODEL 2: MLP (Deep Learning / Neural Network) ---
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            model_nn = MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=500, random_state=42)
            model_nn.fit(X_train_scaled, y_train)
            
            # Ensemble Projection
            latest_feat = df[features].iloc[-1:].values
            p_xg = model_xg.predict(latest_feat)[0]
            p_nn = model_nn.predict(scaler.transform(latest_feat))[0]
            
            # Weighted Hybrid (60% XGBoost, 40% Neural Network)
            final_p = (p_xg * 0.6) + (p_nn * 0.4)
            return float(final_p)
        except:
            return float(df['Close'].iloc[-1])

    @staticmethod
    def generate_spot_advice(df, forecast_p, risk_mode="Moderate", market_closed=False):
        """Balanced High-Reward Spot Advisor with Market-Closed support."""
        last = df.iloc[-1]
        current_p = last['Close']
        ema9, ema21, ema50 = last['EMA9'], last['EMA21'], last['EMA50']
        macd, signal_l = last['MACD'], last['Signal_L']
        rsi, atr = last['RSI'], last['ATR']
        
        # Balanced Tech-Strictness
        rr_req = 2.5 if risk_mode == "Conservative" else 1.8 if risk_mode == "Moderate" else 1.2
        atr_m = 0.8 if risk_mode == "Conservative" else 0.4 if risk_mode == "Moderate" else 0.1
        
        # Trend & Momentum
        trend_up = current_p > ema50
        momentum_up = ema9 > ema21
        macd_up = macd > signal_l
        
        diff = forecast_p - current_p
        sl_dist = atr * 1.6
        potential_entry = current_p
        potential_sl = potential_entry - sl_dist
        potential_tp = forecast_p
        
        risk = potential_entry - potential_sl
        reward = potential_tp - potential_entry
        rr_ratio = reward / risk if risk > 0 else 0
        
        state = "NEUTRAL"
        entry, target, sl, confidence = current_p, current_p, current_p, 0
        
        # MARKET CLOSED MODE (Next Day Projection)
        if market_closed:
            if trend_up and rr_ratio >= rr_req:
                state = "NEXT DAY BUY"
                confidence = min((rr_ratio / 4) * 100, 95)
            elif not trend_up and rr_ratio >= rr_req:
                state = "NEXT DAY SELL"
                confidence = min((rr_ratio / 4) * 100, 95)
            return {
                "state": state, "entry": current_p, "target": potential_tp, 
                "sl": potential_sl, "confidence": confidence, "forecast": forecast_p,
                "rr": rr_ratio, "is_offlight": True
            }

        # LIVE MODE
        # Sideways/Low-Volatility Filter
        is_sideways = abs(diff) < (atr * 0.2) or abs(ema9 - ema21) < (atr * 0.1)
        
        if is_sideways:
            state = "NEUTRAL" # Explicit Sideways protection
        elif (trend_up and momentum_up and macd_up and rsi < 70 and 
            diff > (atr * atr_m) and rr_ratio >= rr_req):
            state = "BUY"
            entry = current_p
            target = potential_tp
            sl = potential_sl
            confidence = min((rr_ratio / 4) * 100, 100)
        elif (not trend_up and not momentum_up and not macd_up and rsi > 30 and 
              diff < -(atr * atr_m)):
            potential_sl_sell = potential_entry + sl_dist
            potential_tp_sell = forecast_p
            risk_s = potential_sl_sell - potential_entry
            reward_s = potential_entry - potential_tp_sell
            rr_s = reward_s / risk_s if risk_s > 0 else 0
            
            if rr_s >= rr_req:
                state = "SELL"
                entry = current_p
                target = potential_tp_sell
                sl = potential_sl_sell
                rr_ratio = rr_s
                confidence = min((rr_ratio / 4) * 100, 100)

        return {
            "state": state, "entry": entry, "target": target, 
            "sl": sl, "confidence": confidence, "forecast": forecast_p,
            "rr": rr_ratio, "is_offlight": False
        }

class QuantumBacktestEngine:
    @staticmethod
    def run_backtest(df):
        results = []
        in_pos = False
        entry_p = 0
        for i in range(50, len(df)-1):
            row = df.iloc[i:i+1]
            c_p = row['Close'].iloc[0]
            if not in_pos and row['EMA9'].iloc[0] > row['EMA21'].iloc[0] and row['RSI'].iloc[0] < 60:
                in_pos, entry_p = True, c_p
                results.append({"type": "BUY", "price": c_p, "time": row.index[0]})
            elif in_pos and (c_p < row['EMA21'].iloc[0] or row['RSI'].iloc[0] > 75):
                results.append({"type": "SELL", "price": c_p, "time": row.index[0], "profit": (c_p - entry_p)/entry_p*100})
                in_pos = False
        return results

# --- SIDEBAR CONTROL ---
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    st.markdown("### 💠 QUANTUM NAVIGATION")
    market_cat = st.radio("MARKET SELECTION", ["CRYPTO", "US STOCKS"], horizontal=True)
    
    if market_cat == "CRYPTO":
        ticker = st.selectbox("ACTIVE PAIR", ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD"], index=0)
    else:
        ticker = st.selectbox("ACTIVE TICKER", ["NVDA", "TSLA", "AAPL", "AMD", "MSFT", "GOOGL"], index=0)
        
    st.markdown("---")
    st.markdown("### 🛠 STRATEGY PROFILE")
    risk_mode = st.selectbox("RISK CHARACTER", ["Conservative", "Moderate", "Aggressive"], index=1)
    
    st.markdown("### 📊 MARKET COMPARISON")
    comp_ticker = st.selectbox("COMPARE AGAINST", ["BTC-USD", "ETH-USD", "SPY", "QQQ", "NVDA", "TSLA"], index=2 if market_cat == "US STOCKS" else 0)
    
    sync_rate = st.slider("REFRESH INTERVAL (SEC)", 2, 60, 5)
    
    st.markdown("---")
    st.markdown("#### ℹ️ SYSTEM DISCLOSURES")
    st.info("**Latency:** US Stocks - 15m delay. Crypto - Near real-time feed.")
    st.warning("**Risk:** AI projections are speculative. Not financial advice.")
    

st_autorefresh(interval=sync_rate * 1000, key="quantum_sync")

# --- LIVE HUD ---
def render_live_hud(ticker, price, change, pct):
    color = "#00ff88" if change >= 0 else "#ff3366"
    st.markdown(f"""
    <div style="background-color: #131722; padding: 10px 20px; border-left: 5px solid #eef400; border-radius: 4px; margin-bottom: 25px; display: flex; align-items: center; justify-content: space-between; font-family: 'JetBrains Mono', monospace;">
        <div style="display: flex; align-items: center;">
            <div class="pulse" style="width: 8px; height: 8px; background-color: {color}; border-radius: 50%; margin-right: 12px;"></div>
            <span style="color: #eef400; font-weight: bold; margin-right: 15px;">QUANTUM LIVE PRICE</span>
            <span style="color: #ffffff;">{ticker}</span>: <span style="color: {color}; font-weight: bold;">${price:,.2f}</span>
            <span style="color: {color}; margin-left: 10px; font-size: 0.8rem;">{change:+.2f} ({pct:+.2f}%)</span>
        </div>
        <div style="font-size: 0.75rem; color: #80848e;">
            ENGINE: <span style="color: #00ff88;">REALTIME_SYNC</span> | FEED: YAHOO_FINANCE
        </div>
    </div>
    <style>
    .pulse {{
        box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7);
        animation: pulse-green 2s infinite;
    }}
    @keyframes pulse-green {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }}
    }}
    </style>
    """, unsafe_allow_html=True)

# --- MAIN ENGINE EXECUTION ---
df_raw = QuantumProjectionEngine.fetch_data(ticker)

if df_raw is not None and not df_raw.empty:
    # Market Hours Detection for Stocks
    is_closed = False
    if market_cat == "US STOCKS":
        h = datetime.now().hour
        # US Market typically 9:30 AM - 4:00 PM ET (Approx 14:30 - 21:00 UTC)
        # Simplified check for demonstration (replace with actual timezone logic if needed)
        if h < 14 or h >= 21: 
            is_closed = True
            # Switch to Daily data for better Next-Day projection
            df_raw = QuantumProjectionEngine.fetch_data(ticker, timeframe="1d")

    # Main Analytics
    df = QuantumProjectionEngine.compute_advanced_indicators(df_raw)
    forecast_p = QuantumProjectionEngine.forecast_quantum_target(df)
    advice = QuantumProjectionEngine.generate_spot_advice(df, forecast_p, risk_mode, market_closed=is_closed)
    
    # Benchmarking Correlation
    benchmark_ticker = "BTC-USD" if market_cat == "CRYPTO" else "SPY"
    corr_score = QuantumProjectionEngine.calculate_correlation(df, benchmark_ticker)
    
    # Attempt to get the absolute latest intraday price
    try:
        t_obj = yf.Ticker(ticker)
        curr_p = t_obj.basic_info.last_price
        if curr_p is None or np.isnan(curr_p): curr_p = df['Close'].iloc[-1]
    except:
        curr_p = df['Close'].iloc[-1]
        
    chg = curr_p - df['Close'].iloc[-2]
    pct = (chg / df['Close'].iloc[-2]) * 100
    
    hud_label = "NEXT DAY OUTLOOK" if is_closed else "QUANTUM LIVE PRICE"
    
    # Render HUD
    color = "#00ff88" if chg >= 0 else "#ff3366"
    st.markdown(f"""
    <div style="background-color: #131722; padding: 10px 20px; border-left: 5px solid #eef400; border-radius: 4px; margin-bottom: 25px; display: flex; align-items: center; justify-content: space-between; font-family: 'JetBrains Mono', monospace;">
        <div style="display: flex; align-items: center;">
            <div class="pulse" style="width: 8px; height: 8px; background-color: {color}; border-radius: 50%; margin-right: 12px;"></div>
            <span style="color: #eef400; font-weight: bold; margin-right: 15px;">{hud_label}</span>
            <span style="color: #ffffff;">{ticker}</span>: <span style="color: {color}; font-weight: bold;">${curr_p:,.2f}</span>
            <span style="color: {color}; margin-left: 10px; font-size: 0.8rem;">{chg:+.2f} ({pct:+.2f}%)</span>
        </div>
        <div style="font-size: 0.75rem; color: #80848e;">
            MODE: <span style="color: #00ff88;">{'OFFLINE_PROJECTION' if is_closed else 'REALTIME_SYNC'}</span> | FEED: YAHOO_FINANCE
        </div>
    </div>
    <style>
    .pulse {{ box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); animation: pulse-green 2s infinite; }}
    @keyframes pulse-green {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0.7); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 255, 136, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 255, 136, 0); }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # --- ROW 1: PRIMARY ANALYTICS ---
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("LIVE PRICE", f"${curr_p:,.2f}", f"{chg:+.2f} ({pct:+.2f}%)")
    col2.metric("ALPHA CONFIDENCE", f"{advice['confidence']:.1f}%")
    
    rsi_val = df['RSI'].iloc[-1]
    sentiment = "NEUTRAL"
    if rsi_val > 70: sentiment = "OVERBOUGHT"
    elif rsi_val < 30: sentiment = "OVERSOLD"
    elif rsi_val > 55: sentiment = "BULLISH"
    elif rsi_val < 45: sentiment = "BEARISH"
    
    col3.metric("MARKET SENTIMENT", sentiment)
    col4.metric(f"CORR vs {benchmark_ticker}", f"{corr_score:+.2f}")

    st.divider()

    # --- ROW 2: ADVISOR & PERFORMANCE ---
    c_adv, c_perf = st.columns([1, 2])
    
    with c_adv:
        st.subheader("🎯 ADVISOR v7 (HIGH REWARD)")
        zone_class = "buy-zone" if advice['state'] == "BUY" else "sell-zone" if advice['state'] == "SELL" else "neutral-zone"
        rr_color = "#00ff88" if advice['rr'] >= 3 else "#ff9800" if advice['rr'] >= 2 else "#80848e"
        
        st.markdown(f"""
        <div class="advisor-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <p class="signal-header">QUANTUM PERSPECTIVE</p>
                <span style="background: {rr_color}; color: #000; padding: 2px 8px; border-radius: 4px; font-size: 0.7rem; font-weight: bold;">RR {advice['rr']:.1f}</span>
            </div>
            <h1 class="{zone_class}" style="font-size: 3.5rem; margin:0;">{advice['state']}</h1>
            <hr style="border-color: #2a2e39">
            <p class="signal-header">RECOM_ENTRY</p>
            <p class="price-value">${advice['entry']:,.2f}</p>
            <p class="signal-header" style="color: #00ff88">ALPHA_TARGET</p>
            <p class="price-value" style="color: #00ff88">${advice['target']:,.2f}</p>
            <p class="signal-header" style="color: #ff3366">SAFETY_SL</p>
            <p class="price-value" style="color: #ff3366">${advice['sl']:,.2f}</p>
            <div style="background: rgba(238, 244, 0, 0.05); padding: 12px; border-radius: 8px; font-size: 0.75rem; color: #80848e; margin-top:15px; border: 1px solid rgba(238, 244, 0, 0.1);">
                <b>🛡️ HIGH REWARD PROTOCOL:</b><br>
                Signals now strictly require a minimum **RR Ratio of {risk_mode} Strategy ({rr_color})**. 
                Current validation enforces high-quality convergence to prioritize exponential gains while protecting capital.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c_perf:
        t_stats, t_log, t_comp = st.tabs(["🚀 PERFORMANCE", "📋 HFT LOG", "📊 CROSS-ASSET"])
        
        with t_stats:
            bt_results = QuantumBacktestEngine.run_backtest(df)
            if bt_results:
                bt_df = pd.DataFrame(bt_results)
                trades = bt_df[bt_df['type'] == 'SELL']
                win_rate = (len(trades[trades['profit'] > 0]) / len(trades) * 100) if len(trades) > 0 else 0
                avg_profit = trades['profit'].mean() if len(trades) > 0 else 0
                
                s1, s2, s3 = st.columns(3)
                s1.metric("SIM_WIN_RATE", f"{win_rate:.0f}%")
                s2.metric("SIM_AVG_PROFIT", f"{avg_profit:+.2f}%")
                s3.metric("SIM_TOTAL_TRADES", len(bt_df))
                
                st.markdown("#### Historical Simulation Log (Current Window)")
                st.dataframe(bt_df.sort_index(ascending=False), use_container_width=True)
            else:
                st.info("No trades identified with current strict logic in this timeframe.")

        with t_log:
            log_df = df.tail(50).copy()
            log_df['TIME'] = log_df.index.strftime('%H:%M:%S')
            log_df['TREND'] = log_df.apply(lambda x: "🟢 BULL" if x['Close'] > x['EMA9'] else "🔴 BEAR", axis=1)
            st.dataframe(
                log_df[['TIME', 'Close', 'Volume', 'TREND', 'RSI']].sort_index(ascending=False),
                use_container_width=True,
                column_config={
                    "Close": st.column_config.NumberColumn("Price", format="$%.2f"),
                    "Volume": st.column_config.NumberColumn("Lot", format="%d"),
                    "RSI": st.column_config.ProgressColumn("RSI", min_value=0, max_value=100)
                },
                hide_index=True
            )
            
        with t_comp:
            st.markdown(f"#### Analyzing {ticker} vs {comp_ticker}")
            df_comp = QuantumProjectionEngine.fetch_data(comp_ticker)
            if df_comp is not None and not df_comp.empty:
                # Align and Normalize
                combined_c = pd.concat([df['Close'], df_comp['Close']], axis=1).dropna()
                combined_c.columns = [ticker, comp_ticker]
                
                # Correlation Heatmap style
                c_val = combined_c.corr().iloc[0,1]
                st.metric("PAIR CORRELATION", f"{c_val:+.2f}", 
                          "Strong Link" if abs(c_val) > 0.7 else "Moderate Link" if abs(c_val) > 0.4 else "Decoupled")
                
                # Comparison Chart
                fig_c = go.Figure()
                # Normalize to % change for better comparison
                n_asset = (combined_c[ticker] / combined_c[ticker].iloc[0] - 1) * 100
                n_bench = (combined_c[comp_ticker] / combined_c[comp_ticker].iloc[0] - 1) * 100
                
                fig_c.add_trace(go.Scatter(x=combined_c.index, y=n_asset, name=ticker, line=dict(color='#eef400', width=2)))
                fig_c.add_trace(go.Scatter(x=combined_c.index, y=n_bench, name=comp_ticker, line=dict(color='#80848e', width=1, dash='dot')))
                
                fig_c.update_layout(template="plotly_dark", height=300, 
                                    margin=dict(l=0, r=0, t=10, b=0),
                                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                    yaxis_title="% Change",
                                    legend=dict(orientation="h", y=1.2))
                st.plotly_chart(fig_c, use_container_width=True)
            else:
                st.error("Failed to fetch comparison data.")

    # --- ROW 3: TRADING TERMINAL ---
    st.divider()
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.02, row_heights=[0.8, 0.2])
    
    # Candlestick
    fig.add_trace(go.Candlestick(x=df.index, open=df['Open'], high=df['High'], low=df['Low'], close=df['Close'], name='Price Feed'), row=1, col=1)
    
    # Tech Overlays
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA9'], name='EMA 9', line=dict(color='#2962ff', width=1.5)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA50'], name='Trend Baseline (EMA50)', line=dict(color='rgba(238, 244, 0, 0.3)', width=1)), row=1, col=1)
    
    # Bollinger Bands
    fig.add_trace(go.Scatter(x=df.index, y=df['Upper_B'], name='Upper Band', line=dict(color='rgba(173, 216, 230, 0.2)', width=1)), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Lower_B'], name='Lower Band', line=dict(color='rgba(173, 216, 230, 0.2)', width=1), fill='tonexty'), row=1, col=1)
    
    # Support & Resistance
    fig.add_trace(go.Scatter(x=df.index, y=df['Res'], name='Dynamic Resistance', line=dict(color='#ff3366', width=1, dash='dot'), opacity=0.5), row=1, col=1)
    fig.add_trace(go.Scatter(x=df.index, y=df['Sup'], name='Dynamic Support', line=dict(color='#00ff88', width=1, dash='dot'), opacity=0.5), row=1, col=1)
    
    if advice['state'] != "NEUTRAL":
        fig.add_hline(y=advice['target'], line_dash="dash", line_color="#00ff88" if advice['state']=="BUY" else "#ff3366", 
                      annotation_text=f"QUANTUM TARGET: {advice['target']:,.2f}", annotation_position="bottom right", row=1, col=1)

    v_cols = ['#089981' if c >= o else '#f23645' for o, c in zip(df['Open'], df['Close'])]
    fig.add_trace(go.Bar(x=df.index, y=df['Volume'], name='Volume Lot', marker_color=v_cols, opacity=0.3), row=2, col=1)
    
    fig.update_layout(template="plotly_dark", height=700, paper_bgcolor="#0c0d10", plot_bgcolor="#0c0d10", 
                      xaxis_rangeslider_visible=False, margin=dict(l=0, r=40, t=10, b=0),
                      yaxis=dict(gridcolor='#2a2e39', side="right"), xaxis=dict(gridcolor='#2a2e39'))
    st.plotly_chart(fig, use_container_width=True)

else:
    st.error("❌ PACKET_LOSS: Quantum Engine Offline. Check Market Hours.")

st.markdown("<div style='text-align: center; color: #444; padding: 20px;'>© 2026 Buminata Quantum Technology • XG-3 Advanced Neural Engine</div>", unsafe_allow_html=True)
