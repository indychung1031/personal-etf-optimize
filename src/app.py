import streamlit as st
import pandas as pd
import os
import json
import data_loader
import utils

# Page Config
st.set_page_config(page_title="Indy's ETF Manager", layout="wide")

# --- Sidebar Navigation ---
st.sidebar.title("📌 Menu")
menu = st.sidebar.radio(
    "Go to",
    ["Indy's ETF Information", "ETF Composition", "Invest in ETF"]
)

# --- Shared Data Loading ---
@st.cache_data
def load_etf_metadata():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        meta_path = os.path.join(base_dir, '..', 'data', 'etf_metadata.json')
        with open(meta_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_compositions():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        comp_path = os.path.join(base_dir, '..', 'data', 'etf_compositions.json')
        with open(comp_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

etf_metadata = load_etf_metadata()
compositions = load_compositions()

# Mapping for View 3 AUM aggregation - Now DYNAMIC
@st.cache_data(ttl=3600)
def get_dynamic_etf_aums(etf_tickers):
    caps = data_loader.get_market_caps(etf_tickers)
    # Convert to Billions for internal scaling consistency
    return {t: (v / 1e9) for t, v in caps.items()}

ETF_AUMS_RAW = get_dynamic_etf_aums(list(etf_metadata.keys()))
# Combine with metadata to ensure we have a fallback
ETF_AUMS = {}
used_fallbacks = []
for k, meta in etf_metadata.items():
    val = ETF_AUMS_RAW.get(k, 0.0)
    if val <= 0:
        val = meta.get('fallback_aum', 0.0)
        used_fallbacks.append(k)
    ETF_AUMS[k] = val

TOTAL_AUM = sum(ETF_AUMS.values())

if used_fallbacks:
    st.sidebar.info(f"💡 현재 실시간 API 제한으로 인해 **2026년 2월 최신 보정 데이터**를 사용하여 포트폴리오를 구성 중입니다. (대상: {len(used_fallbacks)}개 ETF)")

# --- View 1: Indy's ETF Information ---
if menu == "Indy's ETF Information":
    st.title("📘 Indy's ETF Information")
    
    st.markdown("### 1. The Scale of Global Capital (거시적 관점)")
    st.info("""
    **"왜 미국 시장인가?"**
    
    전 세계 주식 자본의 약 **50~60%**가 미국 시장에 집중되어 있습니다. 'myetf'는 이 거대한 흐름을 추종합니다.
    """)
    
    m1, m2, m3 = st.columns(3)
    m1.metric("전 세계 주식 시장 총액", "$130.0 T", "Global Market")
    m2.metric("미국 주식 시장 총액", "$65.0 T", "50% of World")
    m3.metric("분석 대상 ETF 총 자산 (AUM)", f"${TOTAL_AUM/1e3:.1f} T", "Selected 22 ETFs")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🏛️ S&P 500 (VOO)")
        st.markdown(f"""
        *   **Total Market Cap**: ~$50 Trillion
        *   **ETF AUM (VOO)**: ~${ETF_AUMS.get('VOO', 1300):.1f} Billion (Live)
        *   **특징**: 미국 상위 500개 우량주. 안정성의 상징.
        """)
    with col2:
        st.markdown("#### 💻 Nasdaq 100 (QQQ)")
        st.markdown(f"""
        *   **Total Market Cap**: ~$25 Trillion
        *   **ETF AUM (QQQ)**: ~${ETF_AUMS.get('QQQ', 400):.1f} Billion (Live)
        *   **특징**: 기술주 중심의 초고속 성장 엔진.
        """)
        
    st.markdown("---")
    
    st.markdown("### 2. The Titans (Top 20 Concentration)")
    st.warning("""
    **"왜 상위 20개만 봐도 충분한가?"**
    *   **VOO**: 상위 20개 기업이 전체의 **약 48%** 차지.
    *   **QQQ**: 상위 20개 기업이 전체의 **무려 66%** 차지.
    *   나머지 수백 개 기업보다, **상위 20개 '슈퍼스타 기업'**이 내 계좌의 운명을 결정합니다.
    """)
    
    st.markdown("---")
    
    st.markdown("### 3. The Growth Engines (9 Themes)")
    st.markdown("""
    지수의 안정성에 **폭발적인 성장성(Alpha)**을 더하기 위해 9개 미래 산업을 선정했습니다.
    """)
    
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 AI & Robotics", "💾 Semiconductor", "🚀 Future Mobility", "🧬 Bio & Resources"])
    
    def show_etf_details(etf_list, description):
        st.caption(description)
        for ticker in etf_list:
            if ticker in compositions:
                comp = compositions[ticker]
                # Show Top 10 instead of Top 5 to align with calculation logic
                top10 = ", ".join([f"{k} ({v}%)" for k, v in list(comp.items())[:10]])
                
                with st.expander(f"**{ticker}** Analysis", expanded=False):
                    st.write(f"**Top 10 Holdings:** {top10}")
                    
                    # Generic description from metadata
                    if ticker in etf_metadata:
                        st.write(f"✅ **{etf_metadata[ticker]['name']}**: {etf_metadata[ticker]['description']}")
                    else:
                        st.write("✅ **Custom Theme**: 미래 성장 동력 확보를 위한 선정 종목")
    
    with tab1:
        st.subheader("인공지능과 로봇 혁명")
        show_etf_details(["AIQ", "BOTZ", "ROBO", "CHAT", "QTUM"], "AI 모델, 빅데이터 처리, 그리고 물리적 로봇 자동화 기술에 투자합니다.")
        
    with tab2:
        st.subheader("디지털 산업의 쌀, 반도체")
        show_etf_details(["SMH", "SOXX", "CIBR", "HACK"], "AI 연산의 핵심인 GPU/NPU와 이를 지키는 사이버 보안 기술입니다.")
        
    with tab3:
        st.subheader("우주 개척과 자율주행 파괴적 혁신")
        show_etf_details(["ARKX", "UFO", "ROKT", "DRIV", "IDRV"], "지구를 넘어 우주로 확장하고, 도로 위의 이동 혁명을 주도하는 기업들입니다.")
        
    with tab4:
        st.subheader("생명 연장과 필수 자원")
        show_etf_details(["IBB", "XBI", "XME", "PICK", "SETM", "COPP"], "인류 수명 연장의 꿈(Bio)과 기술 구현에 필수적인 희소 자원(Resources)입니다.")
    
    st.markdown("---")
    
    st.markdown("### 4. Indy's Selection Criteria")
    with st.expander("🎯 핵심 선정 기준 (Why this mix?)", expanded=True):
        st.markdown("""
        **1. The Reality Check (Market Cap)**
        *   우리는 VOO와 QQQ를 **50:50으로 단순히 섞지 않습니다.**
        *   실제 시장의 덩치 차이(**76.5% vs 23.5%**)를 존중하여, **'진짜 미국 시장의 평균'**을 Core로 삼습니다.
        
        **2. The Future Alpha (Growth)**
        *   시장 평균(Beta)만으로는 부족합니다.
        *   인류의 삶을 바꿀 **9가지 혁신 테마**에 가산점을 주어, 지수 대비 초과 수익(Alpha)을 추구합니다.
        
        **3. Direct Ownership**
        *   ETF 수수료(0.75%~)를 아끼고, 원하지 않는 종목은 걸러낼 수 있는 **'다이렉트 인덱싱'**을 구현합니다.
        """)

# --- View 2: ETF Composition ---
elif menu == "ETF Composition":
    st.title("🧩 ETF Composition (Underlying Stocks)")
    st.markdown("Indy's ETF를 구성하는 **모든 개별 종목(Master Stock List)**의 상세 정보입니다.")
    
    # Flatten the compositions logic to show a representative table
    # We assume a standard 70/30 split for this view to show "Sample Weights"
    
    # Calculated already at top level for reuse
    # ETF_AUMS = { ... }
    # TOTAL_AUM = sum(ETF_AUMS.values())

    # 1. Calculate Consolidated Weights using centralized logic
    with st.spinner("Calculating Portfolio Weights..."):
        stock_counter, stock_cap_details = utils.calculate_consolidated_weights(ETF_AUMS, compositions)
        # Total score for display purposes
        total_raw_score = sum(sum(breakdown.values()) for breakdown in stock_cap_details.values())

    # Create DF
    data = []
    
    # Needs Market Cap Data
    with st.spinner("Fetching Market Cap Data for Portfolio Analysis..."):
        all_tickers = list(stock_counter.keys())
        market_caps = data_loader.get_market_caps(all_tickers)
    
    total_portfolio_mcap = 0
    
    for t, w in stock_counter.items():
        # Get sectors/ETFs this stock belongs to from the breakdown keys
        sectors = ", ".join(list(stock_cap_details.get(t, {}).keys()))
        mcap = market_caps.get(t) or market_caps.get(t.replace('.', '-'), 0)
        total_portfolio_mcap += mcap
        
        # Format Market Cap
        if mcap > 0:
            mcap_str = f"${mcap/1e9:,.2f} B"
        else:
            mcap_str = "$0.00 B"
            
        # Get Capital Contribution for this stock
        allocated_cap = sum(stock_cap_details.get(t, {}).values())
        
        data.append({
            "Ticker": t, 
            "Consolidated Weight (%)": w, 
            "Allocated Cap ($B)": allocated_cap,
            "Market Cap": mcap_str,
            "Raw Mcap": mcap,
            "Sectors": sectors
        })
        
    df = pd.DataFrame(data).sort_values(by="Consolidated Weight (%)", ascending=False)
    
    # Metrics
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("Total Unique Stocks", len(df))
        
    with c2:
        # Portfolio Market Cap vs US Total
        total_us_market = 65e12 # Updated from $55T to $65T
        coverage = (total_portfolio_mcap / total_us_market) * 100
        st.metric("Portfolio Mcap Coverage", f"{coverage:.1f}% of US Market", f"${total_portfolio_mcap/1e12:.1f}T / $65T")
        
    with c3:
        st.metric("Total Allocated Capital", f"${total_raw_score:.1f} B", "Sum of ETF Weights")

    with st.expander("🔍 지표 상세 설명 (Metric Definitions)", expanded=False):
        st.markdown(f"""
        1. **Total Unique Stocks ({len(df)})**
            *   22개 ETF에서 중복을 제거하고 선별된 **최종 기업 수**입니다. 여러 지수에 중복 포함된 핵심 우량주들을 통합하여 관리합니다.
        
        2. **Portfolio Mcap Coverage ({coverage:.1f}%)**
            *   선별된 {len(df)}개 기업이 **미국 전체 주식 시장($65T)**에서 차지하는 가치의 비중입니다. 상위 우량주 집중 투자를 통해 시장의 80% 이상을 효과적으로 추종합니다.
        
        3. **Total Allocated Capital (${total_raw_score:.1f} B)**
            *   각 ETF의 자산 규모(AUM)와 비중을 고려해 계산된 **가상의 총 투자 원금**입니다. 이 금액을 기준으로 각 개별 종목의 최종 비중(%)이 결정됩니다.
        """)

    st.dataframe(
        df[["Ticker", "Consolidated Weight (%)", "Allocated Cap ($B)", "Market Cap", "Sectors"]].style.format({
            "Consolidated Weight (%)": "{:.5f}%",
            "Allocated Cap ($B)": "${:.2f} B"
        }),
        use_container_width=True,
        height=800
    )

# --- View 3: Invest in ETF ---
elif menu == "Invest in ETF":
    st.title("💰 Invest in ETF (Execution)")
    st.info("투자금을 입력하면, 현재가 기준으로 **매수해야 할 주식 수**를 계산해 드립니다.")
    
    col_inv, _ = st.columns([1, 2])
    with col_inv:
        total_investment = st.number_input("Total Investment ($)", value=10000.0, step=100.0)
        
    # Re-implement Calculator Logic
    # ... (Same Strategy Inputs) ...
    # Calculated already at top level
    # ETF_AUMS = { ... }
    # TOTAL_AUM = sum(ETF_AUMS.values())
    
    st.markdown("### 🎯 Investment Strategy (Market Consensus)")
    st.info(f"""
    **"시장은 정답을 알고 있다 (The Market Knows)"**
    
    *   우리는 인위적인 비중(70:30 등)을 정하지 않습니다.
    *   **전 세계 투자자들이 실제 돈을 걸고 있는 규모(AUM)**를 그대로 따릅니다.
    *   **Core (VOO+QQQ)**: 전체의 약 **{((ETF_AUMS['VOO']+ETF_AUMS['QQQ'])/TOTAL_AUM)*100:.1f}%**
    *   **Themes (Growth)**: 전체의 약 **{(sum(list(ETF_AUMS.values())[2:])/TOTAL_AUM)*100:.1f}%**
    """)

    if st.button("🚀 Calculate Purchase Plan (Data-Driven)", type="primary"):
        final_weights = {}
        
        # Use centralized logic from utils
        final_weights, stock_cap_details = utils.calculate_consolidated_weights(ETF_AUMS, compositions)
        total_raw_score = sum(ETF_AUMS.values()) # Just for metrics display
                        
        # Fractional Shares Option (Default: True per user request)
        allow_fractional = st.checkbox("Allow Fractional Shares (소수점 거래 허용)", value=True, help="체크하면 1주 미만의 소수점 단위까지 매수하여 현금을 최대한 활용합니다.")
        
        # Price Fetch & Calc
        with st.spinner("Fetching Real-time Prices..."):
            sorted_t = sorted(final_weights.keys())
            prices = data_loader.get_latest_prices(sorted_t)
            
            buy_list = []
            skipped_list = []
            missing_price_list = []
            total_cost = 0
            
            for t, w in final_weights.items():
                p = prices.get(t) or prices.get(t.replace('.', '-'), 0)
                if p > 0:
                    amt = total_investment * (w/100)
                    
                    if allow_fractional:
                        shares = round(amt / p, 6) # Increase to 6 decimal places to catch small positions
                    else:
                        shares = int(amt // p)
                        
                    if shares > 0:
                        cost = shares * p
                        # Get sectors/ETFs this stock belongs to from the breakdown keys (from refactored utils call)
                        sectors = ", ".join(list(stock_cap_details.get(t, {}).keys()))
                        
                        buy_list.append({
                            "Ticker": t, "Shares": shares, "Price ($)": p, 
                            "Cost ($)": cost, "Weight (%)": w, "Sectors": sectors
                        })
                        total_cost += cost
                    else:
                        skipped_list.append({
                            "Ticker": t, "Price ($)": p, "Required ($)": p, "Allocated ($)": amt
                        })
                else:
                    missing_price_list.append(t)
            
            # Display
            if buy_list:
                df_buy = pd.DataFrame(buy_list).sort_values("Cost ($)", ascending=False)
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Cost", f"${total_cost:,.2f}")
                c2.metric("Cash Balance", f"${total_investment - total_cost:,.2f}")
                c3.metric("Purchased Stocks", f"{len(buy_list)} / {len(final_weights)}")
                
                st.dataframe(
                    df_buy.style.format({"Price ($)": "${:.2f}", "Cost ($)": "${:.2f}", "Weight (%)": "{:.2f}%", "Shares": "{:.6f}"}),
                    use_container_width=True,
                    height=600,
                    hide_index=True
                )
                st.caption(f"Showing top {len(df_buy)} holdings. Scroll down to see more.")
                
                if missing_price_list:
                    st.error(f"⚠️ {len(missing_price_list)} Stocks Failed to Fetch Price (Showing first 20): {', '.join(missing_price_list[:20])}...")
                
                csv = df_buy.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="💾 Download Order Sheet",
                    data=csv,
                    file_name="order_sheet.csv",
                    mime="text/csv",
                    key="download_order_sheet_button"
                )
                
                if skipped_list:
                    with st.expander(f"⚠️ Skipped Stocks ({len(skipped_list)}) - Insufficient Capital", expanded=False):
                        st.warning(f"""
                        **{len(skipped_list)}개 종목은 투자금 부족으로 매수하지 못했습니다.**
                        
                        예: 1주 가격이 $100인데, 배정된 금액이 $10라면 매수할 수 없습니다.
                        모든 종목을 사려면 투자 금액을 늘려야 합니다.
                        """)
                        st.dataframe(pd.DataFrame(skipped_list))
                        
            else:
                st.warning("매수할 종목이 없습니다. 투자 금액을 늘리거나 네트워크 연결을 확인해주세요.")
                
                with st.expander("🔍 Debug Info (Why is it empty?)", expanded=True):
                    st.write(f"**Target Stocks**: {len(final_weights)}")
                    st.write(f"**Fetched Prices**: {len(prices)}")
                    
                    if len(final_weights) > 0:
                        st.write("Top 5 Weights (Calculated):")
                        top5 = sorted(final_weights.items(), key=lambda x: x[1], reverse=True)[:5]
                        st.json(dict(top5))
                        
                    if len(prices) == 0:
                        st.error("No prices fetched. Check yfinance connection.")
                    else:
                        st.write("Sample Prices:")
                        st.json(dict(list(prices.items())[:5]))
                        st.json({k: v for k, v in prices.items() if 'BRK' in k}) # Explicitly check BRK
