import requests
import streamlit as st

st.set_page_config(page_title="코인 구매 계산기", layout="centered")

# 버튼 크기 및 폰트 확대 커스텀 CSS
st.markdown(
    """
    <style>
    div.stButton > button {
        height: 3.2rem;
        font-size: 1.15rem;
        font-weight: 700;
        border-radius: 10px;
        width: 100%;
        margin-top: 5px;
        margin-bottom: 5px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 실시간 환율 API (5분 캐싱)
@st.cache_data(ttl=300)
def fetch_usd_krw_rate():
  try:
    url = "https://open.er-api.com/v6/latest/USD"
    res = requests.get(url, timeout=5)
    data = res.json()
    return float(data["rates"]["KRW"])
  except Exception as err:
    return 1350.0


st.title("코인 구매 계산기")

# 구매 방식 선택
mode = st.radio(
    "구매 방식 선택",
    ["달러당 x원으로 구매", "퍼센트 형식으로 구매"],
    horizontal=True,
)

st.divider()

# 공통 입력: 구매 코인 원화 금액 (N)
n = st.number_input(
    "구매할 코인 금액 (원, N)", min_value=0, value=10000, step=1000
)

# 1. 달러당 x원으로 구매 모드
if mode == "달러당 x원으로 구매":
  current_rate = fetch_usd_krw_rate()

  col_rate, col_btn = st.columns([3, 1])
  with col_rate:
    st.info(f"실시간 기준 환율: **{current_rate:,.2f}원 / USD**")
  with col_btn:
    if st.button("환율 갱신", use_container_width=True):
      st.cache_data.clear()
      st.rerun()

  e = st.number_input(
      "현재 달러 환율 (원, E)",
      min_value=0.01,
      value=current_rate,
      step=1.0,
      format="%.2f",
  )
  x = st.number_input(
      "기준 환율 (1달러당 x원)",
      min_value=0.01,
      value=1450.0,
      step=1.0,
      format="%.2f",
  )

  if e > 0:
    usd = n / e  # 1단계: 원화 -> 달러
    final_krw = usd * x  # 2단계: 달러 -> 최종 원화

    st.divider()
    col1, col2 = st.columns(2)
    col1.metric("1차 환산 달러", f"${usd:,.4f}")
    col2.metric("최종 지출 금액", f"{final_krw:,.0f} 원")

    st.caption(
        f"계산식: ({n:,}원 ÷ {e:,.2f}원) × {x:,.2f}원 = {final_krw:,.2f}원"
    )

# 2. 퍼센트 형식으로 구매 모드
else:
  y = st.number_input(
      "적용할 퍼센트 (y%)",
      min_value=0.0,
      value=5.0,
      step=0.1,
      format="%.2f",
  )

  # N원의 y% 계산
  y_amount = n * (y / 100)
  total_with_y = n + y_amount

  st.divider()
  col1, col2 = st.columns(2)
  col1.metric(f"N원의 {y}% 금액", f"{y_amount:,.0f} 원")
  col2.metric("최종 지출 금액 (N + y%)", f"{total_with_y:,.0f} 원")

  st.caption(
      f"계산식: {n:,}원 × {y}% = {y_amount:,.0f}원 (원금 합산 시 {total_with_y:,.0f}원)"
  )
