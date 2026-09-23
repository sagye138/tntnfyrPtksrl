import requests
import streamlit as st

st.set_page_config(page_title="코인 구매 계산기", layout="centered")

# 1. UI 대형화 커스텀 CSS (버튼, 입력창, 글자 크기 대폭 확대)
st.markdown(
    """
    <style>
    /* 모든 버튼 크기 및 폰트 대형화 */
    div.stButton > button {
        min-height: 3.8rem !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        border-radius: 12px !important;
    }
    /* 숫자 입력창 높이 및 폰트 확대 */
    div[data-baseweb="input"] {
        min-height: 3.6rem !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"] input {
        font-size: 1.35rem !important;
        font-weight: 700 !important;
    }
    /* 입력창 라벨(제목) 글자 크기 확대 */
    div[data-testid="stWidgetLabel"] p {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
        margin-bottom: 6px !important;
    }
    /* 결과 수치(Metric) 크기 확대 */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 실시간 환율 API
@st.cache_data(ttl=60)
def fetch_usd_krw_rate():
  try:
    url = "https://open.er-api.com/v6/latest/USD"
    res = requests.get(url, timeout=5)
    return float(res.json()["rates"]["KRW"])
  except Exception:
    return 1350.0


# 세션 상태 초기화
if "mode" not in st.session_state:
  st.session_state.mode = "usd"

live_rate = fetch_usd_krw_rate()
if "e_val" not in st.session_state:
  st.session_state.e_val = live_rate

st.title("⚡ 코인 구매 계산기")

# 2. 대형 모드 전환 버튼 (달러당 / 퍼센트당)
col_m1, col_m2 = st.columns(2)
with col_m1:
  btn_type_usd = "primary" if st.session_state.mode == "usd" else "secondary"
  if st.button(
      "💵 달러당 계산", type=btn_type_usd, use_container_width=True
  ):
    st.session_state.mode = "usd"
    st.rerun()

with col_m2:
  btn_type_pct = (
      "primary" if st.session_state.mode == "percent" else "secondary"
  )
  if st.button(
      "📊 퍼센트당 계산", type=btn_type_pct, use_container_width=True
  ):
    st.session_state.mode = "percent"
    st.rerun()

st.divider()

# 공통 입력: 구매 코인 원화 금액 (N)
n = st.number_input(
    "구매할 코인 금액 (원, N)",
    min_value=0,
    value=10000,
    step=1000,
    format="%d",
)

# ---------------------------------------------------------
# 모드 1: 달러당 x원으로 구매
# ---------------------------------------------------------
if st.session_state.mode == "usd":
  st.caption(f"현재 조회된 시장 환율: {live_rate:,.2f}원 / USD")

  # 현재 환율 즉시 적용 대형 버튼
  if st.button(
      f"⚡ 현재 환율 바로 적용 ({live_rate:,.2f}원)",
      use_container_width=True,
  ):
    st.cache_data.clear()
    st.session_state.e_val = fetch_usd_krw_rate()
    st.rerun()

  # 현재 달러 환율 (E) 입력창
  e = st.number_input(
      "현재 달러 환율 (원, E)",
      min_value=0.01,
      step=1.0,
      format="%.2f",
      key="e_val",
  )

  # 기준 환율 (x) 입력창
  x = st.number_input(
      "기준 환율 (1달러당 x원)",
      min_value=0.01,
      value=1450.0,
      step=1.0,
      format="%.2f",
  )

  if e > 0:
    usd = n / e
    final_krw = usd * x

    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("1차 환산 달러", f"${usd:,.4f}")
    col2.metric("최종 지출 금액", f"{final_krw:,.0f} 원")

    st.caption(
        f"계산식: ({n:,}원 ÷ {e:,.2f}원) × {x:,.2f}원 = {final_krw:,.2f}원"
    )

# ---------------------------------------------------------
# 모드 2: 퍼센트 형식으로 구매
# ---------------------------------------------------------
else:
  y = st.number_input(
      "적용할 퍼센트 (y%)",
      min_value=0.0,
      value=5.0,
      step=0.1,
      format="%.2f",
  )

  y_amount = n * (y / 100)
  total_with_y = n + y_amount

  st.divider()
  col1, col2 = st.columns(2)
  col1.metric(f"N원의 {y}% 금액", f"{y_amount:,.0f} 원")
  col2.metric("최종 지출 금액 (N + y%)", f"{total_with_y:,.0f} 원")

  st.caption(
      f"계산식: {n:,}원 × {y}% = {y_amount:,.0f}원 | 원금 포함: {total_with_y:,.0f}원"
  )
