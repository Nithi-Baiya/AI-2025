import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta

# --- 1. เตรียมข้อมูลและ Train AI ---
@st.cache_resource
def train_model():
    df = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
    
    # ฟังก์ชันแบ่งช่วงอายุ
    def age_grouping(age):
        if age < 25: return 'Youth'
        elif age <= 40: return 'Young Adult'
        elif age <= 60: return 'Middle Aged'
        else: return 'Senior'

    df['Age Group'] = df['Age'].apply(age_grouping)
    
    # แปลงข้อมูลตัวอักษรเป็นตัวเลข (Encoding)
    le_gender = LabelEncoder()
    df['Gender'] = le_gender.fit_transform(df['Gender'])
    
    le_bmi = LabelEncoder()
    df['BMI Category'] = le_bmi.fit_transform(df['BMI Category'])
    
    le_age_group = LabelEncoder()
    df['Age Group'] = le_age_group.fit_transform(df['Age Group'])
    
    # เลือก Features (เปลี่ยนจาก Age เป็น Age Group)
    features = ['Gender', 'Age Group', 'Sleep Duration', 'Physical Activity Level', 'Stress Level', 'BMI Category', 'Heart Rate', 'Daily Steps']
    X = df[features]
    y = df['Quality of Sleep']
    
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    return model, le_gender, le_bmi, le_age_group

model, le_gender, le_bmi, le_age_group = train_model()

# --- 2. หน้าตาแอป (UI) ---
st.title("🤖 AI Sleep Predictor (Age Group Mode)")

with st.sidebar:
    st.header("👤 ข้อมูลพื้นฐาน")
    gender = st.selectbox("เพศ", ["Male", "Female"])
    
    # รับอินพุตเป็นช่วงอายุแทนการกรอกตัวเลขเดี่ยวๆ
    age_choice = st.selectbox("ช่วงอายุของคุณ", ["Youth (<25)", "Young Adult (25-40)", "Middle Aged (41-60)", "Senior (>60)"])
    # ตัดเอาเฉพาะชื่อกลุ่มเพื่อไปเข้าเครื่องมือแปลง (le_age_group)
    age_group_label = age_choice.split(" (")[0]
    
    steps = st.number_input("จำนวนก้าวเดินเมื่อวาน", 0, 20000, 5000)
    heart_rate = st.number_input("อัตราการเต้นหัวใจ (BPM)", 40, 120, 70)
    bmi_cat = st.selectbox("กลุ่ม BMI", ["Normal", "Overweight", "Obese"])

# --- 3. ส่วนการคำนวณและทำนาย ---
st.subheader("⏰ บันทึกการนอนจากนาฬิกาปลุก")
col1, col2 = st.columns(2)
with col1:
    bed_time = st.time_input("เวลาเข้านอน", datetime.strptime("22:30", "%H:%M").time())
    wake_time = st.time_input("เวลาตื่นนอน", datetime.strptime("06:30", "%H:%M").time())
with col2:
    stress = st.slider("ระดับความเครียด", 1, 10, 5)
    activity = st.slider("กิจกรรมทางกาย (นาที)", 0, 120, 30)

if st.button("🚀 วิเคราะห์ด้วย AI"):
    # คำนวณระยะเวลาการนอน
    start = datetime.combine(datetime.today(), bed_time)
    end = datetime.combine(datetime.today(), wake_time)
    if end <= start: end += timedelta(days=1)
    duration = (end - start).total_seconds() / 3600
    
    # เตรียมข้อมูลส่งให้ Model
    input_data = pd.DataFrame([[
        le_gender.transform([gender])[0],
        le_age_group.transform([age_group_label])[0],
        duration,
        activity,
        stress,
        le_bmi.transform([bmi_cat])[0],
        heart_rate,
        steps
    ]], columns=['Gender', 'Age Group', 'Sleep Duration', 'Physical Activity Level', 'Stress Level', 'BMI Category', 'Heart Rate', 'Daily Steps'])
    
    prediction = model.predict(input_data)[0]
    
    st.divider()
    st.metric("คุณภาพการนอนที่ AI คาดการณ์", f"{prediction} / 10")
    
    # คำแนะนำตามช่วงอายุ
    st.subheader(f"💡 คำแนะนำสำหรับกลุ่ม {age_group_label}")
    if age_group_label == "Young Adult":
        st.write("ช่วงวัยนี้มักมีความเครียดสะสมสูง ควรระวังเรื่องการใช้หน้าจอก่อนนอน")
    elif age_group_label == "Middle Aged":
        st.write("ควรไปพบเเพทย์เเละตรวจสขภาพ (Sleep Apnea)")
