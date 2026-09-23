import requests
import streamlit as st

st.set_page_config(page_title="코인 구매 계산기", layout="centered")

# UI 스타일링 (버튼, 텍스트창, 한글 배지 크기 확대)
st.markdown(
    """
    <style>
    div.stButton > button {
        min-height: 3.5rem !important;
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"] {
        min-height: 3.6rem !important;
        border-radius: 10px !important;
    }
    div[data-baseweb="input"] input {
        font-size: 1.4rem !important;
        font-weight: 700 !important;
    }
    div[data-testid="stWidgetLabel"] p {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800 !important;
    }
    .amount-badge {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1E88E5;
        margin-top: -6px;
        margin-bottom: 12px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 한글 금액 단위 변환 함수 (10000 -> 1만 원, 150000 -> 15만 원)
def to_korean_money(val: int) -> str:
  if val <= 0:
    return "0원"
  eok = val // 100000000
  man = (val % 100000000) // 10000
  won = val % 10000

  parts = []
  if eok > 0:
    parts.append(f"{eok:,}억")
  if man > 0:
    parts.append(f"{man:,}만")
  if won > 0:
    parts.append(f"{won:,}")
  return " ".join(parts) + " 원"


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
if "n_str" not in st.session_state:
  st.session_state.n_str = "10,000"

live_rate = fetch_usd_krw_rate()
if "e_val" not in st.session_state:
  st.session_state.e_val = live_rate


# 금액 입력값 자동 쉼표 포맷팅 콜백
def format_n():
  raw = "".join(c for c in st.session_state.n_str if c.isdigit())
  st.session_state.n_str = f"{int(raw):,}" if raw else "0"


# 금액 빠른 증감 콜백
def add_amount(delta):
  raw = "".join(c for c in st.session_state.n_str if c.isdigit())
  current = int(raw) if raw else 0
  new_val = max(0, current + delta)
  st.session_state.n_str = f"{new_val:,}"


def reset_amount():
  st.session_state.n_str = "0"


st.title("⚡ 코인 구매 계산기")

# 1. 계산 모드 선택 대형 버튼
col_m1, col_m2 = st.columns(2)
with col_m1:
  btn_usd = "primary" if st.session_state.mode == "usd" else "secondary"
  if st.button("💵 달러당 계산", type=btn_usd, use_container_width=True):
    st.session_state.mode = "usd"
    st.rerun()

with col_m2:
  btn_pct = "primary" if st.session_state.mode == "percent" else "secondary"
  if st.button("📊 퍼센트당 계산", type=btn_pct, use_container_width=True):
    st.session_state.mode = "percent"
    st.rerun()

st.divider()

# 2. 구매 코인 원화 금액 (N) - 쉼표 자동 지원
st.text_input(
    "구매할 코인 금액 (원, N)",
    key="n_str",
    on_change=format_n,
    placeholder="예: 10,000",
)

# 입력된 숫자 추출 및 한글 단위 표시
raw_num = "".join(c for c in st.session_state.n_str if c.isdigit())
n = int(raw_num) if raw_num else 0

st.markdown(
    f"<div class='amount-badge'>👉 현재 금액: <b>{n:,}원</b> ({to_korean_money(n)})</div>",
    unsafe_allow_html=True,
)

# 간편 금액 조절 버튼
btn_cols = st.columns(5)
btn_cols[0].button(
    "+1만", on_click=add_amount, args=(10000,), use_container_width=True
)
btn_cols[1].button(
    "+5만", on_click=add_amount, args=(50000,), use_container_width=True
)
btn_cols[2].button(
    "+10만", on_click=add_amount, args=(100000,), use_container_width=True
)
btn_cols[3].button(
    "+100만", on_click=add_amount, args=(1000000,), use_container_width=True
)
btn_cols[4].button("초기화", on_click=reset_amount, use_container_width=True)

st.write("")

# ---------------------------------------------------------
# 모드 1: 달러당 x원으로 구매
# ---------------------------------------------------------
if st.session_state.mode == "usd":
  st.caption(f"실시간 시장 환율: {live_rate:,.2f}원 / USD")

  if st.button(
      f"⚡ 현재 환율 바로 적용 ({live_rate:,.2f}원)",
      use_container_width=True,
  ):
    st.cache_data.clear()
    st.session_state.e_val = fetch_usd_krw_rate()
    st.rerun()

  e = st.number_input(
      "현재 달러 환율 (원, E)",
      min_value=0.01,
      step=1.0,
      format="%.2f",
      key="e_val",
  )

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
