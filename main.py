import requests
import streamlit as st

st.set_page_config(page_title="코인 구매 계산기", layout="centered")

# UI 스타일링
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
    .amount-badge {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1E88E5;
        margin-top: -6px;
        margin-bottom: 12px;
    }
    .sync-badge {
        text-align: center;
        font-size: 1.3rem;
        font-weight: 800;
        color: #888;
        margin: 12px 0;
    }
    /* 최종 지출 금액 대형 전광판 카드 */
    .hero-final-card {
        background: linear-gradient(135deg, #1976D2 0%, #0D47A1 100%);
        border-radius: 18px;
        padding: 24px 20px;
        text-align: center;
        color: #FFFFFF;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
        margin: 24px 0 16px 0;
    }
    .hero-final-label {
        font-size: 1.15rem;
        font-weight: 600;
        opacity: 0.9;
        margin-bottom: 6px;
        letter-spacing: -0.3px;
    }
    .hero-final-price {
        font-size: 3.2rem;
        font-weight: 900;
        line-height: 1.1;
        letter-spacing: -1px;
    }
    .hero-final-price span {
        font-size: 2rem;
        font-weight: 700;
    }
    .hero-final-korean {
        font-size: 1.35rem;
        font-weight: 700;
        color: #90CAF9;
        margin-top: 8px;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 한글 금액 단위 변환 함수
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


# 숫자 파싱 도우미
def parse_int(s: str) -> int:
  digits = "".join(c for c in s if c.isdigit())
  return int(digits) if digits else 0


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
live_rate = fetch_usd_krw_rate()

if "mode" not in st.session_state:
  st.session_state.mode = "usd"
if "e_val" not in st.session_state:
  st.session_state.e_val = live_rate
if "x_val" not in st.session_state:
  st.session_state.x_val = 1450.0
if "y_val" not in st.session_state:
  st.session_state.y_val = 5.0

if "n_str" not in st.session_state:
  st.session_state.n_str = "10,000"
if "final_str" not in st.session_state:
  init_n = 10000
  init_final = (init_n / live_rate) * 1450.0
  st.session_state.final_str = f"{int(round(init_final)):,}"


# 1. 구매 코인 금액(N) 변경 시 -> 최종 지출 계산
def on_n_change():
  n = parse_int(st.session_state.n_str)
  st.session_state.n_str = f"{n:,}"

  if st.session_state.mode == "usd":
    e = st.session_state.e_val
    x = st.session_state.x_val
    final = (n / e) * x if e > 0 else 0
  else:
    y = st.session_state.y_val
    final = n * (1 + y / 100)

  st.session_state.final_str = f"{int(round(final)):,}"


# 2. 최종 지출 금액 변경 시 -> 구매 코인 금액(N) 역산
def on_final_change():
  final = parse_int(st.session_state.final_str)
  st.session_state.final_str = f"{final:,}"

  if st.session_state.mode == "usd":
    e = st.session_state.e_val
    x = st.session_state.x_val
    n = (final / x) * e if x > 0 else 0
  else:
    y = st.session_state.y_val
    multiplier = 1 + y / 100
    n = final / multiplier if multiplier > 0 else 0

  st.session_state.n_str = f"{int(round(n)):,}"


# 파라미터(환율 or 퍼센트) 변경 시 자동 재계산
def on_param_change():
  on_n_change()


# 빠른 증감 버튼 콜백
def add_to_n(delta):
  n = max(0, parse_int(st.session_state.n_str) + delta)
  st.session_state.n_str = f"{n:,}"
  on_n_change()


def reset_n():
  st.session_state.n_str = "0"
  on_n_change()


def add_to_final(delta):
  final = max(0, parse_int(st.session_state.final_str) + delta)
  st.session_state.final_str = f"{final:,}"
  on_final_change()


def reset_final():
  st.session_state.final_str = "0"
  on_final_change()


# 환율 갱신 버튼 콜백
def apply_live_rate():
  st.cache_data.clear()
  st.session_state.e_val = fetch_usd_krw_rate()
  on_n_change()


# ---------------------------------------------------------
# UI 렌더링
# ---------------------------------------------------------
st.title("⚡ 코인 구매 계산기")

# 계산 모드 선택 대형 버튼
col_m1, col_m2 = st.columns(2)
with col_m1:
  btn_usd = "primary" if st.session_state.mode == "usd" else "secondary"
  if st.button("💵 달러당 계산", type=btn_usd, use_container_width=True):
    st.session_state.mode = "usd"
    on_n_change()
    st.rerun()

with col_m2:
  btn_pct = "primary" if st.session_state.mode == "percent" else "secondary"
  if st.button("📊 퍼센트당 계산", type=btn_pct, use_container_width=True):
    st.session_state.mode = "percent"
    on_n_change()
    st.rerun()

st.divider()

# 조건 설정 영역
if st.session_state.mode == "usd":
  st.caption(f"실시간 시장 환율: {live_rate:,.2f}원 / USD")

  if st.button(
      f"⚡ 현재 환율 바로 적용 ({live_rate:,.2f}원)",
      use_container_width=True,
      on_click=apply_live_rate,
      key="apply_live_rate_btn",
  ):
    pass

  col_e, col_x = st.columns(2)
  with col_e:
    st.number_input(
        "현재 달러 환율 (원, E)",
        min_value=0.01,
        step=1.0,
        format="%.2f",
        key="e_val",
        on_change=on_param_change,
    )
  with col_x:
    st.number_input(
        "기준 환율 (1달러당 x원)",
        min_value=0.01,
        step=1.0,
        format="%.2f",
        key="x_val",
        on_change=on_param_change,
    )
else:
  st.number_input(
      "적용할 퍼센트 (y%)",
      min_value=0.0,
      step=0.1,
      format="%.2f",
      key="y_val",
      on_change=on_param_change,
  )

st.divider()

# 1. 구매할 코인 금액 (N)
st.text_input(
    "구매할 코인 금액 (원, N)",
    key="n_str",
    on_change=on_n_change,
    placeholder="예: 10,000",
)
n_val = parse_int(st.session_state.n_str)
st.markdown(
    f"<div class='amount-badge'>👉 코인 금액: <b>{n_val:,}원</b>"
    f" ({to_korean_money(n_val)})</div>",
    unsafe_allow_html=True,
)

btn_n = st.columns(5)
btn_n[0].button(
    "+1백",
    on_click=add_to_n,
    args=(100,),
    use_container_width=True,
    key="btn_n_0.01man",
)
btn_n[1].button(
    "+1천",
    on_click=add_to_n,
    args=(1000,),
    use_container_width=True,
    key="btn_n_0.1man",
)
btn_n[2].button(
    "+1만",
    on_click=add_to_n,
    args=(10000,),
    use_container_width=True,
    key="btn_n_1man",
)
btn_n[3].button(
    "+10만",
    on_click=add_to_n,
    args=(100000,),
    use_container_width=True,
    key="btn_n_10man",
)
btn_n[4].button(
    "초기화", on_click=reset_n, use_container_width=True, key="btn_n_reset"
)

st.markdown(
    "<div class='sync-badge'>⇅ 양방향 연동 ⇅</div>", unsafe_allow_html=True
)

# 2. 최종 지출 금액 (직접 수정 가능 인풋)
st.text_input(
    "최종 지출 금액 직접 수정 (원)",
    key="final_str",
    on_change=on_final_change,
    placeholder="예: 10,741",
)
final_val = parse_int(st.session_state.final_str)

btn_f = st.columns(5)
btn_f[0].button(
    "+1백",
    on_click=add_to_final,
    args=(100,),
    use_container_width=True,
    key="btn_f_0.01man",
)
btn_f[1].button(
    "+1천",
    on_click=add_to_final,
    args=(1000,),
    use_container_width=True,
    key="btn_f_0.1man",
)
btn_f[2].button(
    "+1만",
    on_click=add_to_final,
    args=(10000,),
    use_container_width=True,
    key="btn_f_1man",
)
btn_f[3].button(
    "+10만",
    on_click=add_to_final,
    args=(100000,),
    use_container_width=True,
    key="btn_f_10man",
)
btn_f[4].button(
    "초기화", on_click=reset_final, use_container_width=True, key="btn_f_reset"
)

# 3. 한눈에 들어오는 대형 최종 지출 금액 전광판
st.markdown(
    f"""
    <div class="hero-final-card">
        <div class="hero-final-label">💳 최종 지출 금액</div>
        <div class="hero-final-price">{final_val:,} <span>원</span></div>
        <div class="hero-final-korean">({to_korean_money(final_val)})</div>
    </div>
""",
    unsafe_allow_html=True,
)

# 하단 세부 계산식 요약
if st.session_state.mode == "usd":
  usd_val = n_val / st.session_state.e_val if st.session_state.e_val > 0 else 0
  st.caption(
      f"1차 환산: **${usd_val:,.4f}** | 계산식: ({n_val:,}원 ÷"
      f" {st.session_state.e_val:,.2f}원) × {st.session_state.x_val:,.2f}원 ="
      f" {final_val:,}원"
  )
else:
  diff = final_val - n_val
  st.caption(
      f"추가 수수료({st.session_state.y_val}%): **{diff:,}원** | 계산식:"
      f" {n_val:,}원 × (1 + {st.session_state.y_val}%) = {final_val:,}원"
  )
