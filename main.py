import os
import uuid
import pandas as pd
import streamlit as st
import datetime as dt

# 데이터 파일 경로
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "medications.csv")
EMOTION_FILE = os.path.join(DATA_DIR, "emotions.csv")
PRIORITY_FILE = os.path.join(DATA_DIR, "priorities.csv")

# 데이터 컬럼 정의
data_columns = ["ID", "약물 이름", "복약 시간", "복용 용량", "복약 완료"]
emotion_columns = ["ID", "날짜", "감정", "점수", "기록"]
priority_columns = ["ID", "작업명", "긴급도", "중요도", "상태"]

# 초기 데이터 디렉토리 및 파일 생성 함수
def initialize_files():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    for file, columns in [
        (DATA_FILE, data_columns),
        (EMOTION_FILE, emotion_columns),
        (PRIORITY_FILE, priority_columns)
    ]:
        if not os.path.exists(file) or os.path.getsize(file) == 0:
            pd.DataFrame(columns=columns).to_csv(file, index=False)

# 데이터 로드 및 저장 함수
def load_data(file, columns):
    if not os.path.exists(file) or os.path.getsize(file) == 0:
        st.session_state[file] = pd.DataFrame(columns=columns)
    else:
        try:
            st.session_state[file] = pd.read_csv(file)
        except pd.errors.EmptyDataError:
            st.session_state[file] = pd.DataFrame(columns=columns)
    return st.session_state[file]

def save_data(file, data):
    st.session_state[file] = data
    data.to_csv(file, index=False)

# 초기화 실행
initialize_files()

# 데이터 불러오기
med_data = load_data(DATA_FILE, data_columns)
emotion_data = load_data(EMOTION_FILE, emotion_columns)
priority_data = load_data(PRIORITY_FILE, priority_columns)

# **Streamlit 앱 시작**
st.title("마음의 정원")
st.sidebar.title("메뉴")

# **1. 복약 관리**
st.header("💊 복약 관리")
with st.form("add_medication"):
    med_name = st.text_input("약물 이름", placeholder="예: 항우울제")
    med_time = st.time_input("복약 시간", dt.time(9, 0))
    med_dosage = st.text_input("복용 용량", placeholder="예: 50mg")
    if st.form_submit_button("추가"):
        new_row = pd.DataFrame([{
            "ID": str(uuid.uuid4()),
            "약물 이름": med_name,
            "복약 시간": med_time.strftime("%H:%M"),
            "복용 용량": med_dosage,
            "복약 완료": False
        }])
        med_data = pd.concat([med_data, new_row], ignore_index=True)
        save_data(DATA_FILE, med_data)
        st.success("복약 정보가 추가되었습니다!")

st.subheader("📋 복약 리스트")
for idx, row in med_data.iterrows():
    col1, col2 = st.columns([3, 1])
    if not row["복약 완료"]:
        col1.write(f"{row['약물 이름']} ({row['복용 용량']}) - {row['복약 시간']}")
        if col2.button("완료", key=f"med-{row['ID']}"):
            med_data.loc[idx, "복약 완료"] = True
            save_data(DATA_FILE, med_data)
            st.success(f"{row['약물 이름']} 완료!")
    else:
        col1.markdown(
            f"✅ <span style='background-color:lightgreen'>{row['약물 이름']} ({row['복용 용량']})</span>",
            unsafe_allow_html=True,
        )

st.download_button("복약 데이터 다운로드", med_data.to_csv(index=False), "medications.csv", "text/csv")

# **2. 감정 기록**
st.header("😊 감정 기록")
with st.form("add_emotion"):
    date = st.date_input("날짜", dt.date.today())
    emotion = st.selectbox("오늘 기분", ["😀 행복", "😞 슬픔", "😠 화남", "😨 불안", "😐 보통"])
    score = st.slider("기분 점수", 0, 10, 5)
    note = st.text_area("기록", "오늘의 기분을 기록하세요.")
    if st.form_submit_button("기록 추가"):
        sentiment = "Negative" if "안좋아" in note else "Positive"
        new_row = pd.DataFrame([{
            "ID": str(uuid.uuid4()),
            "날짜": date,
            "감정": emotion,
            "점수": score,
            "기록": note
        }])
        emotion_data = pd.concat([emotion_data, new_row], ignore_index=True)
        save_data(EMOTION_FILE, emotion_data)
        st.success("감정 기록이 추가되었습니다!")
        if sentiment == "Negative":
            st.warning("힘든 하루였군요. 짧은 명상을 시도해 보세요.")

st.subheader("📈 감정 변화 차트")
if not emotion_data.empty:
    st.bar_chart(emotion_data.groupby("감정")["점수"].mean())
st.download_button("감정 데이터 다운로드", emotion_data.to_csv(index=False), "emotion_data.csv", "text/csv")

# **3. 우선순위 정리**
st.header("🔗 우선순위 정리")
with st.form("add_task"):
    task = st.text_input("작업명")
    urgent = st.selectbox("긴급도", ["높음", "보통", "낮음"])
    important = st.selectbox("중요도", ["높음", "보통", "낮음"])
    if st.form_submit_button("작업 추가"):
        new_row = pd.DataFrame([{
            "ID": str(uuid.uuid4()),
            "작업명": task,
            "긴급도": urgent,
            "중요도": important,
            "상태": "미완료"
        }])
        priority_data = pd.concat([priority_data, new_row], ignore_index=True)
        save_data(PRIORITY_FILE, priority_data)
        st.success("작업이 추가되었습니다!")

st.subheader("📋 작업 리스트")
for idx, row in priority_data.iterrows():
    col1, col2, col3 = st.columns([3, 1, 1])
    col1.write(f"{row['작업명']} - 긴급도: {row['긴급도']}, 중요도: {row['중요도']}")
    if row["상태"] == "미완료" and col2.button("완료", key=f"task-{row['ID']}"):
        priority_data.loc[idx, "상태"] = "완료"
        save_data(PRIORITY_FILE, priority_data)
        st.success(f"{row['작업명']} 완료!")
st.bar_chart(priority_data["상태"].value_counts())
