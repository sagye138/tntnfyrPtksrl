import requests
import streamlit as st

st.set_page_config(page_title="코인 환산 계산기", layout="centered")


# 실시간 환율 API 호출 함수 (5분 캐싱)
@st.cache_data(ttl=300)
def fetch_usd_krw_rate():
  try:
    url = "https://open.er-api.com/v6/latest/USD"
    res = requests.get(url, timeout=5)
    data = res.json()
    return float(data["rates"]["KRW"])
  except Exception as err:
    st.error(f"환율 API 호출 실패: {err}")
    return 1350.0  # 실패 시 기본값


st.title("코인 환산 계산기")

# 환율 불러오기 및 새로고침
current_rate = fetch_usd_krw_rate()

col_rate, col_btn = st.columns([3, 1])
with col_rate:
  st.info(f"현재 실시간 환율: **{current_rate:,.2f}원 / USD**")
with col_btn:
  if st.button("환율 갱신"):
    st.cache_data.clear()
    st.rerun()

# 입력값
n = st.number_input(
    "구매할 코인 금액 (원, N)", min_value=0, value=10000, step=1000
)

# API 환율을 기본값으로 사용하되, 직접 수정도 가능하게 처리
e = st.number_input(
    "적용할 현재 달러 환율 (원, E)",
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

# 계산
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
else:
  st.error("현재 환율은 0보다 커야 합니다.")
