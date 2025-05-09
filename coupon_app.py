import streamlit as st
import json
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

# ======== 한글 폰트 설정 ========
matplotlib.rc('font', family='Malgun Gothic')

# ======== 데이터 파일 경로 ========
DATA_FILE = "coupon_data.json"
HISTORY_FILE = "coupon_history.json"

# ======== 데이터 불러오기 ========
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        users = json.load(f)
else:
    users = {}

if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
else:
    history = []

# ======== 데이터 저장 함수 ========
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ======== 적립/사용 기록 추가 함수 ========
def add_record(name, amount, action):
    record = {
        "고객명": name,
        "적립수": amount if action == "적립" else 0,
        "사용수": amount if action == "사용" else 0,
        "날짜": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    history.append(record)
    save_data()

# ======== Streamlit UI 시작 ========
st.markdown("<h4>💳 구내식당 쿠폰 적립</h4>", unsafe_allow_html=True)
st.write("")
st.markdown("<h5>💳 쿠폰 적립/사용</h5>", unsafe_allow_html=True)

name = st.text_input("고객 이름을 입력하세요")
amount = st.number_input("쿠폰 수를 입력하세요", min_value=1, step=1)

col1, col2 = st.columns(2)

with col1:
    if st.button("➕ 쿠폰 적립"):
        if name:
            users[name] = users.get(name, 0) + amount
            add_record(name, amount, "적립")
            st.success(f"{name}님께 {amount}개 적립 완료! (총 {users[name]}개)")
        else:
            st.warning("고객 이름을 입력해 주세요.")

with col2:
    if st.button("➖ 쿠폰 사용"):
        if name:
            if users.get(name, 0) >= amount:
                users[name] -= amount
                add_record(name, amount, "사용")
                st.success(f"{name}님께서 {amount}개 사용했습니다. (남은 쿠폰: {users[name]}개)")
            else:
                st.error("쿠폰이 부족합니다.")
        else:
            st.warning("고객 이름을 입력해 주세요.")

# ======== 이용자별 총 적립 (이모티콘 포함) ========
st.write("")
st.write("")
st.markdown("<h5>👑 이용자별 총 적립</h5>", unsafe_allow_html=True)

if users:
    ranking_df = pd.DataFrame(list(users.items()), columns=["고객명", "보유 쿠폰수"])
    ranking_df = ranking_df.sort_values(by="보유 쿠폰수", ascending=False)
    ranking_df["보유 쿠폰수"] = ranking_df["보유 쿠폰수"].astype(int)

    total_coupons = ranking_df["보유 쿠폰수"].sum()

    if total_coupons > 0:
        # 🎟️ 쿠폰 이모티콘 컬럼 추가
        ranking_df["쿠폰"] = ranking_df["보유 쿠폰수"].apply(lambda x: "🎟️" * x)

        st.dataframe(ranking_df)
    else:
        st.write("현재 보유 쿠폰이 있는 고객이 없습니다.")
else:
    st.write("등록된 고객이 없습니다.")

# ======== 날짜별 적립/사용 이력 보기 (모든 적립/사용 개별 이력 표시) ========
st.write("")
st.write("")
st.markdown("<h5>📅 쿠폰 적립/사용 이력</h5>", unsafe_allow_html=True)

if history:
    history_df = pd.DataFrame(history)

    # 날짜+시간 포맷 유지
    history_df["날짜"] = pd.to_datetime(history_df["날짜"]).dt.strftime("%Y-%m-%d")

    # 적립/사용 표시 (명확히 구분)
    history_df["이력"] = history_df.apply(
        lambda row: f"적립 +{row['적립수']}" if row['적립수'] > 0 else f"사용 -{row['사용수']}", axis=1
    )

    # 필요한 컬럼만 정리
    display_df = history_df[["날짜", "고객명", "이력"]]

    # 최신순 정렬
    display_df = display_df.sort_values(by="날짜", ascending=False)

    st.dataframe(display_df)

else:
    st.write("적립/사용 기록이 없습니다.")

# ======== 쿠폰 이력 엑셀로 내보내기 ========
st.write("")
st.write("")
st.markdown("<h5>📥 쿠폰 이력 엑셀로 내보내기</h5>", unsafe_allow_html=True)

if st.button("엑셀 내보내기"):
    if history:
        df = pd.DataFrame(history)
        df["날짜"] = pd.to_datetime(df["날짜"]).dt.strftime("%Y-%m-%d")
        df["적립/사용"] = df.apply(lambda row: f"+{row['적립수']}" if row['적립수'] > 0 else f"-{row['사용수']}", axis=1)
        df = df[["날짜", "고객명", "적립/사용"]]
        try:
            df.to_excel("coupon_history.xlsx", index=False)
            st.success("엑셀로 내보냈습니다. (coupon_history.xlsx)")
        except PermissionError:
            st.error("엑셀 파일이 열려 있어 저장할 수 없습니다. 닫고 다시 시도해 주세요.")
    else:
        st.write("내보낼 적립/사용 기록이 없습니다.")
