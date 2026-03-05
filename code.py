import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Alarm Sleep Tracker", page_icon="⏰")

# --- ส่วนเก็บข้อมูลใน Session ---
if 'history' not in st.session_state:
    st.session_state.history = []

st.title("⏰ Alarm-Based Sleep Quality")
st.markdown("ประเมินคุณภาพการนอนจากพฤติกรรมการใช้ **นาฬิกาปลุก**")

# --- ส่วนรับข้อมูล ---
with st.form("sleep_form"):
    col1, col2 = st.columns(2)
    with col1:
        bed_time = st.time_input("เวลาที่เข้านอนจริง", datetime.strptime("22:30", "%H:%M").time())
        alarm_set = st.time_input("เวลาที่ตั้งปลุกไว้", datetime.strptime("06:30", "%H:%M").time())
    
    with col2:
        actual_wake = st.time_input("เวลาที่กดปิดปลุก/ลุกจากเตียง", datetime.strptime("06:45", "%H:%M").time())
        snooze_count = st.number_input("กดเลื่อนปลุก (Snooze) กี่ครั้ง?", min_value=0, step=1)

    feeling = st.select_slider("ความรู้สึกหลังตื่น", options=["เพลียมาก", "งัวเงีย", "สดชื่น", "กระปรี้กระเปร่า"])
    submit = st.form_submit_button("วิเคราะห์การนอน")

# --- Logic การคำนวณ ---
if submit:
    # คำนวณระยะเวลา (Duration)
    fmt = "%H:%M:%S"
    d_bed = datetime.combine(datetime.today(), bed_time)
    d_alarm = datetime.combine(datetime.today(), alarm_set)
    d_wake = datetime.combine(datetime.today(), actual_wake)

    # จัดการกรณีข้ามคืน
    if d_alarm <= d_bed: d_alarm += timedelta(days=1)
    if d_wake <= d_bed: d_wake += timedelta(days=1)

    total_sleep = (d_wake - d_bed).total_seconds() / 3600
    # คำนวณความต่างระหว่างเวลาปลุกกับเวลาตื่นจริง (Snooze Time)
    oversleep_mins = (d_wake - d_alarm).total_seconds() / 60

    # คำนวณคะแนน (เต็ม 100)
    score = 100
    if total_sleep < 7: score -= 15 # นอนน้อย
    if oversleep_mins > 15: score -= 10 # ตื่นสายกว่าปลุกนานเกินไป
    score -= (snooze_count * 5) # ยิ่งเลื่อนปลุก คะแนนยิ่งลด (สะท้อนว่าหลับไม่ลึกพอ)
    
    mapping = {"เพลียมาก": -20, "งัวเงีย": -5, "สดชื่น": 5, "กระปรี้กระเปร่า": 10}
    score += mapping[feeling]
    score = max(0, min(100, score))

    # บันทึกประวัติ
    record = {
        "Date": datetime.now().strftime("%d/%m/%Y"),
        "Score": score,
        "Sleep_Hours": round(total_sleep, 1),
        "Snooze_Mins": oversleep_mins,
        "Feeling": feeling
    }
    st.session_state.history.append(record)

# --- ส่วนแสดงผลและเปรียบเทียบ ---
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    last = df.iloc[-1]
    
    st.divider()
    st.subheader(f"ผลการประเมินรอบล่าสุด: {last['Score']} คะแนน")
    
    # แสดง Metric เปรียบเทียบ
    if len(df) > 1:
        prev = df.iloc[-2]
        c1, c2, c3 = st.columns(3)
        c1.metric("คะแนน", f"{last['Score']}", f"{int(last['Score'] - prev['Score'])} pts")
        c2.metric("ชั่วโมงนอน", f"{last['Sleep_Hours']} ชม.", f"{round(last['Sleep_Hours'] - prev['Sleep_Hours'], 1)} ชม.")
        c3.metric("เวลาที่ตื่นสายกว่าปลุก", f"{int(last['Snooze_Mins'])} นาที", f"{int(last['Snooze_Mins'] - prev['Snooze_Mins'])} นาที", delta_color="inverse")
    
    

    # กราฟแสดงแนวโน้ม
    st.write("### แนวโน้มคุณภาพการนอนของคุณ")
    st.line_chart(df.set_index("Date")["Score"])
    
    with st.expander("🔍 คำแนะนำเชิงลึก"):
        if last['Snooze_Mins'] > 10:
            st.warning("คุณมีการ 'Snooze' หรือตื่นช้ากว่าเวลาปลุก การทำแบบนี้บ่อยๆ จะทำให้เกิดภาวะ **Sleep Inertia** (ความง่วงค้าง) ทำให้เพลียระหว่างวันได้ครับ")
        if last['Sleep_Hours'] < 7:
            st.info("ระยะเวลานอนสั้นกว่าเกณฑ์มาตรฐาน ลองขยับเวลาเข้านอนให้เร็วขึ้น 15 นาทีในคืนนี้ดูนะครับ")

    # ดาวน์โหลด Dataset
    st.download_button("Export to CSV", df.to_csv(index=False), "sleep_data.csv", "text/csv")
