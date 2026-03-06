import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
 
# --- 1. โหลดข้อมูล Dataset ---
@st.cache_data # ใช้ Cache เพื่อให้แอปโหลดไวขึ้น
def load_data():
    df = pd.read_csv('Sleep_health_and_lifestyle_dataset.csv')
    return df
 
df = load_data()
 
st.set_page_config(page_title="Data-Driven Sleep Analyzer", page_icon="📊")
 
st.title("📊 Sleep Analyzer (Data-Driven)")
st.markdown("ประเมินคุณภาพการนอนของคุณโดยเปรียบเทียบกับ **ข้อมูลจริงจากกลุ่มตัวอย่าง 374 ราย**")
 
# --- 2. ส่วนรับข้อมูลจากผู้ใช้ ---
with st.sidebar:
    st.header("👤 ข้อมูลของคุณ")
    user_job = st.selectbox("อาชีพของคุณ", df['Occupation'].unique())
    user_age = st.slider("อายุ", 20, 60, 30)
    user_bmi = st.selectbox("กลุ่ม BMI", df['BMI Category'].unique())
 
st.subheader("⏰ บันทึกการนอนเช้านี้")
col1, col2 = st.columns(2)
with col1:
    bed_time = st.time_input("เข้านอนตอน", datetime.strptime("23:00", "%H:%M").time())
    alarm_time = st.time_input("ตั้งปลุกไว้ตอน", datetime.strptime("06:00", "%H:%M").time())
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
 
    # --- 4. แสดงผลลัพธ์ ---
    st.subheader(f"เปรียบเทียบกับกลุ่มอาชีพ: {user_job}")
    
    m1, m2 = st.columns(2)
    # เทียบชั่วโมงนอนของผู้ใช้ กับ ค่าเฉลี่ยของคนอาชีพเดียวกันใน Dataset
    diff_duration = user_sleep_duration - avg_sleep_group
    m1.metric("ชั่วโมงการนอนของคุณ", f"{user_sleep_duration:.1f} ชม.", f"{diff_duration:.1f} ชม. จากค่าเฉลี่ยกลุ่ม")
    
    # คำนวณคะแนนโดยอิงจาก Stress Level ใน Dataset
    # ใน Dataset ยิ่ง Stress สูง Quality ยิ่งต่ำ เราจะใช้ Logic นี้มาประเมิน
    expected_quality = 10 - stress_input # Logic คร่าวๆ: เครียดมาก คุณภาพน้อย
    m2.metric("คาดการณ์คุณภาพการนอน", f"{expected_quality}/10", f"ฐานข้อมูลระบุค่าเฉลี่ยที่ {avg_quality_group:.1f}")
 
    # --- 5. คำแนะนำแบบเจาะจง (Insights) ---
    st.info("💡 **Insight จากฐานข้อมูล:**")
    
    # ตรวจสอบความเสี่ยงโรคจากการนอน (Sleep Disorder) ในกลุ่มอาชีพเดียวกัน
    disorder_stats = comparison_group['Sleep Disorder'].value_counts(normalize=True) * 100
    if 'Insomnia' in disorder_stats or 'Sleep Apnea' in disorder_stats:
        risk = disorder_stats.get('Insomnia', 0) + disorder_stats.get('Sleep Apnea', 0)
        st.write(f"- ในกลุ่มอาชีพ {user_job} ของคุณ พบความเสี่ยงโรคจากการนอนประมาณ {risk:.1f}%")
    
    if user_sleep_duration < avg_sleep_group:
        st.warning(f"- วันนี้คุณนอนน้อยกว่าค่าเฉลี่ยของเพื่อนร่วมอาชีพ {user_job} เล็กน้อย พยายามหาเวลาพักผ่อนเพิ่มนะครับ")
    else:
        st.success(f"- ยอดเยี่ยม! คุณนอนได้มากกว่าค่าเฉลี่ยของกลุ่มอาชีพ {user_job}")
 
    # แสดงกราฟเปรียบเทียบ
    st.write("### กราฟแสดงความสัมพันธ์ของกลุ่มตัวอย่าง (Sleep Duration vs Quality)")
    st.scatter_chart(data=comparison_group, x='Sleep Duration', y='Quality of Sleep', color="#FF4B4B")
