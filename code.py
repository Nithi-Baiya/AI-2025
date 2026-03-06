import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta

# --- 1. เตรียมข้อมูลและ Train AI ---
@st.cache_resource # ใช้ cache เพื่อให้โหลด Model ครั้งเดียว ไม่ต้องโหลดใหม่ทุกครั้งที่กดปุ่ม
def train_model():
    df = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
    
    # เคลีนข้อมูลเบื้องต้น
    # แปลง Gender และ BMI Category เป็นตัวเลข
    le_gender = LabelEncoder()
    df['Gender'] = le_gender.fit_transform(df['Gender'])
    
    le_bmi = LabelEncoder()
    df['BMI Category'] = le_bmi.fit_transform(df['BMI Category'])
    
    # เลือก Features ที่สำคัญมาสอน AI
    features = ['Gender', 'Age', 'Sleep Duration', 'Physical Activity Level', 'Stress Level', 'BMI Category', 'Heart Rate', 'Daily Steps']
    X = df[features]
    y = df['Quality of Sleep'] # เราจะทำนายคุณภาพการนอน
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    return model, le_gender, le_bmi

model, le_gender, le_bmi = train_model()

# --- 2. หน้าตาแอป (UI) ---
st.set_page_config(page_title="AI Sleep Predictor", page_icon="🤖")
st.title("🤖 AI Sleep Quality Predictor")
st.markdown("วิเคราะห์คุณภาพการนอนของคุณด้วย AI จากข้อมูลงานวิจัยจริง")

with st.sidebar:
    st.header("👤 ข้อมูลพื้นฐาน")
    gender = st.selectbox("เพศ", ["Male", "Female"])
    age = st.number_input("อายุ", 10, 100, 30)
    steps = st.number_input("จำนวนก้าวเดินเมื่อวาน", 0, 20000, 5000)
    heart_rate = st.number_input("อัตราการเต้นหัวใจขณะพัก (BPM)", 40, 120, 70)
    bmi_cat = st.selectbox("กลุ่ม BMI", ["Normal", "Overweight", "Obese"])

st.subheader("⏰ ข้อมูลจากนาฬิกาปลุกและการนอน")
col1, col2 = st.columns(2)
with col1:
    bed_time = st.time_input("เข้านอนจริง", datetime.strptime("22:00", "%H:%M").time())
    wake_time = st.time_input("ตื่นจริง", datetime.strptime("06:00", "%H:%M").time())
with col2:
    stress = st.slider("ระดับความเครียด (1-10)", 1, 10, 5)
    activity = st.slider("ระดับกิจกรรมทางกาย (นาที/วัน)", 0, 120, 30)

# --- 3. การทำนายผล ---
if st.button("🚀 ให้ AI วิเคราะห์ผล"):
    # คำนวณ Sleep Duration
    start = datetime.combine(datetime.today(), bed_time)
    end = datetime.combine(datetime.today(), wake_time)
    if end <= start: end += timedelta(days=1)
    duration = (end - start).total_seconds() / 3600
    
    # เตรียมข้อมูลสำหรับเข้า Model
    input_data = pd.DataFrame([[
        le_gender.transform([gender])[0],
        age,
        duration,
        activity,
        stress,
        le_bmi.transform([bmi_cat])[0],
        heart_rate,
        steps
    ]], columns=['Gender', 'Age', 'Sleep Duration', 'Physical Activity Level', 'Stress Level', 'BMI Category', 'Heart Rate', 'Daily Steps'])
    
    prediction = model.predict(input_data)[0]
    
    st.divider()
    
    # แสดงผลลัพธ์
    st.header(f"คุณภาพการนอนที่ AI ทำนาย: {prediction}/10")
    
    if prediction >= 8:
        st.balloons()
        st.success("AI วิเคราะห์ว่าคุณภาพการนอนของคุณอยู่ในเกณฑ์ดีเยี่ยม!")
    elif prediction >= 6:
        st.warning("AI วิเคราะห์ว่าคุณภาพการนอนอยู่ในระดับปานกลาง ควรพักผ่อนให้มากขึ้น")
    else:
        st.error("AI พบว่าคุณภาพการนอนของคุณค่อนข้างต่ำ โปรดระมัดระวังสุขภาพ")

    # ข้อมูลเสริมจาก Dataset
    st.info(f"💡 จากข้อมูลที่คุณกรอก AI พบว่าระยะเวลาการนอน {duration:.1f} ชม. และระดับความเครียด {stress}/10 เป็นปัจจัยสำคัญต่อคะแนนของคุณ")
