import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from datetime import datetime, timedelta

# --- 1. โหลดข้อมูล Dataset ---
@st.cache_data # ใช้ Cache เพื่อให้แอปโหลดไวขึ้น
def load_data():
# --- 1. เตรียมข้อมูลและ Train AI ---
@st.cache_resource
def train_model():
    df = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
    return df
    
    # ฟังก์ชันแบ่งช่วงอายุ
    def age_grouping(age):
        if age < 25: return 'Youth'
        elif age <= 40: return 'Young Adult'
        elif age <= 60: return 'Middle Aged'
        else: return 'Senior'

df = load_data()
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

st.set_page_config(page_title="Data-Driven Sleep Analyzer", page_icon="📊")
model, le_gender, le_bmi, le_age_group = train_model()

st.title("📊 Sleep Analyzer (Data-Driven)")
st.markdown("ประเมินคุณภาพการนอนของคุณโดยเปรียบเทียบกับ **ข้อมูลจริงจากกลุ่มตัวอย่าง 374 ราย**")
# --- 2. หน้าตาแอป (UI) ---
st.title("🤖 AI Sleep Predictor (Age Group Mode)")

# --- 2. ส่วนรับข้อมูลจากผู้ใช้ ---
with st.sidebar:
    st.header("👤 ข้อมูลของคุณ")
    user_job = st.selectbox("อาชีพของคุณ", df['Occupation'].unique())
    user_age = st.slider("อายุ", 20, 60, 30)
    user_bmi = st.selectbox("กลุ่ม BMI", df['BMI Category'].unique())
    st.header("👤 ข้อมูลพื้นฐาน")
    gender = st.selectbox("เพศ", ["Male", "Female"])
    
    # รับอินพุตเป็นช่วงอายุแทนการกรอกตัวเลขเดี่ยวๆ
    age_choice = st.selectbox("ช่วงอายุของคุณ", ["Youth (<25)", "Young Adult (25-40)", "Middle Aged (41-60)", "Senior (>60)"])
    # ตัดเอาเฉพาะชื่อกลุ่มเพื่อไปเข้าเครื่องมือแปลง (le_age_group)
    age_group_label = age_choice.split(" (")[0]
    
    steps = st.number_input("จำนวนก้าวเดินเมื่อวาน", 0, 20000, 5000)
    heart_rate = st.number_input("อัตราการเต้นหัวใจ (BPM)", 40, 120, 70)
    bmi_cat = st.selectbox("กลุ่ม BMI", ["Normal", "Overweight", "Obese"])

st.subheader("⏰ บันทึกการนอนเช้านี้")
# --- 3. ส่วนการคำนวณและทำนาย ---
st.subheader("⏰ บันทึกการนอนจากนาฬิกาปลุก")
col1, col2 = st.columns(2)
with col1:
    bed_time = st.time_input("เข้านอนตอน", datetime.strptime("23:00", "%H:%M").time())
    alarm_time = st.time_input("ตั้งปลุกไว้ตอน", datetime.strptime("06:00", "%H:%M").time())
    bed_time = st.time_input("เวลาเข้านอน", datetime.strptime("22:30", "%H:%M").time())
    wake_time = st.time_input("เวลาตื่นนอน", datetime.strptime("06:30", "%H:%M").time())
with col2:
    actual_wake = st.time_input("ตื่นจริงตอน", datetime.strptime("06:15", "%H:%M").time())
    stress_input = st.slider("ระดับความเครียดวันนี้ (1-10)", 1, 10, 5)

if st.button("📈 วิเคราะห์โดยเทียบกับ Dataset"):
    # คำนวณเวลานอนจริงของผู้ใช้
    d_bed = datetime.combine(datetime.today(), bed_time)
    d_wake = datetime.combine(datetime.today(), actual_wake)
    if d_wake <= d_bed: d_wake += timedelta(days=1)
    user_sleep_duration = (d_wake - d_bed).total_seconds() / 3600

    # --- 3. การเปรียบเทียบกับ Dataset ---
    # กรองข้อมูลตามอาชีพหรือกลุ่มที่ใกล้เคียง
    comparison_group = df[df['Occupation'] == user_job]
    avg_sleep_group = comparison_group['Sleep Duration'].mean()
    avg_quality_group = comparison_group['Quality of Sleep'].mean()

    st.divider()
    stress = st.slider("ระดับความเครียด", 1, 10, 5)
    activity = st.slider("กิจกรรมทางกาย (นาที)", 0, 120, 30)

    # --- 4. แสดงผลลัพธ์ ---
    st.subheader(f"เปรียบเทียบกับกลุ่มอาชีพ: {user_job}")
if st.button("🚀 วิเคราะห์ด้วย AI"):
    # คำนวณระยะเวลาการนอน
    start = datetime.combine(datetime.today(), bed_time)
    end = datetime.combine(datetime.today(), wake_time)
    if end <= start: end += timedelta(days=1)
    duration = (end - start).total_seconds() / 3600

    m1, m2 = st.columns(2)
    # เทียบชั่วโมงนอนของผู้ใช้ กับ ค่าเฉลี่ยของคนอาชีพเดียวกันใน Dataset
    diff_duration = user_sleep_duration - avg_sleep_group
    m1.metric("ชั่วโมงการนอนของคุณ", f"{user_sleep_duration:.1f} ชม.", f"{diff_duration:.1f} ชม. จากค่าเฉลี่ยกลุ่ม")
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

    # คำนวณคะแนนโดยอิงจาก Stress Level ใน Dataset
    # ใน Dataset ยิ่ง Stress สูง Quality ยิ่งต่ำ เราจะใช้ Logic นี้มาประเมิน
    expected_quality = 10 - stress_input # Logic คร่าวๆ: เครียดมาก คุณภาพน้อย
    m2.metric("คาดการณ์คุณภาพการนอน", f"{expected_quality}/10", f"ฐานข้อมูลระบุค่าเฉลี่ยที่ {avg_quality_group:.1f}")

    # --- 5. คำแนะนำแบบเจาะจง (Insights) ---
    st.info("💡 **Insight จากฐานข้อมูล:**")
    prediction = model.predict(input_data)[0]

    # ตรวจสอบความเสี่ยงโรคจากการนอน (Sleep Disorder) ในกลุ่มอาชีพเดียวกัน
    disorder_stats = comparison_group['Sleep Disorder'].value_counts(normalize=True) * 100
    if 'Insomnia' in disorder_stats or 'Sleep Apnea' in disorder_stats:
        risk = disorder_stats.get('Insomnia', 0) + disorder_stats.get('Sleep Apnea', 0)
        st.write(f"- ในกลุ่มอาชีพ {user_job} ของคุณ พบความเสี่ยงโรคจากการนอนประมาณ {risk:.1f}%")
    st.divider()
    st.metric("คุณภาพการนอนที่ AI คาดการณ์", f"{prediction} / 10")

    if user_sleep_duration < avg_sleep_group:
        st.warning(f"- วันนี้คุณนอนน้อยกว่าค่าเฉลี่ยของเพื่อนร่วมอาชีพ {user_job} เล็กน้อย พยายามหาเวลาพักผ่อนเพิ่มนะครับ")
    else:
        st.success(f"- ยอดเยี่ยม! คุณนอนได้มากกว่าค่าเฉลี่ยของกลุ่มอาชีพ {user_job}")

    # แสดงกราฟเปรียบเทียบ
    st.write("### กราฟแสดงความสัมพันธ์ของกลุ่มตัวอย่าง (Sleep Duration vs Quality)")
    st.scatter_chart(data=comparison_group, x='Sleep Duration', y='Quality of Sleep', color="#FF4B4B")
    # คำแนะนำตามช่วงอายุ
    st.subheader(f"💡 คำแนะนำสำหรับกลุ่ม {age_group_label}")
    if age_group_label == "Young Adult":
        st.write("ช่วงวัยนี้มักมีความเครียดสะสมสูง ควรระวังเรื่องการใช้หน้าจอก่อนนอน")
    elif age_group_label == "Middle Aged":
        st.write("ควรไปพบเเพทย์เเละตรวจสขภาพ (Sleep Apnea)")
