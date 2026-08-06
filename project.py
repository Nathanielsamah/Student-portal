import streamlit as st
import pandas as pd
import plotly.express as px
import json
from io import BytesIO
from datetime import date
from streamlit_local_storage import LocalStorage

# --- CONFIGURATION: MASTER SECURITY ACCESS ---
MASTER_ID = "admin"
MASTER_PASSWORD = "school2026"

# --- CONFIGURATION: UNIVERSITY COURSE LIST ---
COURSES_LIST = [
    "Economics", "Mathematics 101", "Computer Science", 
    "Business Administration", "Accounting", "Data Analytics", 
    "Statistics", "Information Technology", "Corporate Finance", 
    "Software Engineering"
]

# 1. Page Configuration
st.set_page_config(
    page_title="University Grade Sheet Management Portal",
    page_icon="🎓",
    layout="wide"
)

# Maintain login state across refreshes
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 2. Sidebar Navigation and Authorization Control Panel
st.sidebar.title("🔐 Secure Login & Settings")

if not st.session_state.logged_in:
    input_id = st.sidebar.text_input("Enter Master ID:")
    input_password = st.sidebar.text_input("Enter Password:", type="password")
    login_button = st.sidebar.button("Login To System")

    if login_button:
        if input_id == MASTER_ID and input_password == MASTER_PASSWORD:
            st.session_state.logged_in = True
            st.sidebar.success("✅ Login Verified!")
            st.rerun()
        else:
            st.sidebar.error("❌ Invalid Credentials.")
else:
    st.sidebar.success(f"Active Session: {MASTER_ID}")
    st.sidebar.markdown("---")
    st.sidebar.subheader("⚙️ System Control Hub")
    
    # SYSTEM RESET TRIGGER
    if st.sidebar.button("🗑️ Wipe Entire Database", help="Irreversibly deletes all student profiles stored on this hardware."):
        st.session_state.student_db = pd.DataFrame()
        local_storage = LocalStorage()
        local_storage.setItem("uni_master_db", "")
        st.sidebar.warning("💥 Database fully cleared!")
        st.rerun()
        
    # AUTH CLEAR LOGOUT
    if st.sidebar.button("🚪 System Logout"):
        st.session_state.logged_in = False
        st.rerun()

# Halt processing if authentication state is false
if not st.session_state.logged_in:
    st.title("🎓 University Academic Record & Grade Sheet System")
    st.warning("🔒 Access Denied. Please input authentication credentials in the sidebar panel.")
    st.stop()

# 3. Main Application Workspace Header
st.title("🎓 University Academic Record & Grade Sheet System")
st.write("Six-Week Python Training Project: Automated Performance Assessment Engine.")
st.markdown("---")

# 4. Storage Controller Framework
local_storage = LocalStorage()
saved_json = local_storage.getItem("uni_master_db")

if 'student_db' not in st.session_state:
    if saved_json and saved_json.strip() != "":
        try:
            st.session_state.student_db = pd.DataFrame(json.loads(saved_json))
        except Exception:
            st.session_state.student_db = pd.DataFrame()
    else:
        st.session_state.student_db = pd.DataFrame()

# 5. Interface Split Layout Configuration
col_form, col_table = st.columns([1, 1], gap="large")

with col_form:
    st.subheader("📝 Entry Form: Student Academic Marks")
    
    with st.form("academic_entry_form", clear_on_submit=True):
        # Institutional Fields
        selected_uni = st.selectbox("Select University:", [
            "I.K. Gujral Punjab Technical University", 
            "Synetic Business School Campus", 
            "Punjab National Training University"
        ])
        
        selected_class = st.selectbox("Select Class / Cohort Group:", ["Class ABC"] + [f"Class {i}" for i in range(1, 13)])
        acad_year = st.selectbox("Academic Evaluation Term:", ["2025/2026", "2026/2027", "2027/2028"])
        issue_date = st.date_input("Date of Result Declaration:", date.today())
        
        # Student Biographic Fields
        student_name = st.text_input("Student Full Name:")
        roll_num = st.number_input("Registration / Roll Number:", min_value=1, step=1, value=2221757)
        
        st.markdown("---")
        st.write("📊 **Course Scores Input (Scale 0 - 100)**")
        
        # Iterative Input Processing Loops for the 10 Courses
        form_scores = {}
        sub_col1, sub_col2 = st.columns(2)
        
        for idx, course in enumerate(COURSES_LIST):
            target_col = sub_col1 if idx < 5 else sub_col2
            with target_col:
                form_scores[course] = st.number_input(f"{course}:", min_value=0, max_value=100, value=0, key=f"inp_{course}")
        
        submit_record = st.form_submit_button("💾 Save & Process Student Record")

    if submit_record:
        if not student_name.strip():
            st.error("⚠️ Record rejected: Student Full Name field cannot be empty.")
        elif not st.session_state.student_db.empty and int(roll_num) in st.session_state.student_db["Roll Num"].values:
            st.error(f"⚠️ Conflict: Roll Number {roll_num} already exists in the current cohort database.")
        else:
            # Mathematical Calculations Engine
            scores_series = pd.Series(form_scores)
            total_marks = int(scores_series.sum())
            calculated_avg = float(scores_series.mean())
            final_status = "Pass" if calculated_avg >= 40.0 else "Fail"
            
            # Formulating data entity schema row
            new_entry = {
                "University": selected_uni,
                "Class": selected_class,
                "Year": acad_year,
                "Date": str(issue_date),
                "Roll Num": int(roll_num),
                "Name": student_name,
                "Total Marks": total_marks,
                "Average (%)": round(calculated_avg, 2),
                "Status": final_status
            }
            # Inject course tracking fields dynamically
            for course, mark in form_scores.items():
                new_entry[course] = int(mark)
                
            st.session_state.student_db = pd.concat([st.session_state.student_db, pd.DataFrame([new_entry])], ignore_index=True)
            local_storage.setItem("uni_master_db", st.session_state.student_db.to_json(orient="records"))
            st.success(f"✅ Securely committed transcript profile for {student_name}!")
            st.rerun()

with col_table:
    st.subheader("📋 Centralized Master Transcript Ledger")
    
    if not st.session_state.student_db.empty:
        # Columns selection display grid view filter
        display_df = st.session_state.student_db[["University", "Class", "Roll Num", "Name", "Total Marks", "Average (%)", "Status"]]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Document Export Buffer Compilation Layer
        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            st.session_state.student_db.to_excel(writer, index=False, sheet_name="Master Transcripts Ledger")
            
        st.download_button(
            label="📥 Download Master Database Spreadsheet (.xlsx)",
            data=excel_buffer.getvalue(),
            file_name="University_Master_Transcripts.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.info("System memory pipeline is empty. Submit a transcript record to initialize ledger tracking.")

st.markdown("---")

# 6. Performance Evaluation Analytical Metrics Panel
st.subheader("📊 Analytical Class Performance Indicators Dashboard")

if not st.session_state.student_db.empty:
    db = st.session_state.student_db
    
    # Statistical Compilations
    total_records = len(db)
    passed_count = len(db[db["Status"] == "Pass"])
    failed_count = len(db[db["Status"] == "Fail"])
    global_average = pd.to_numeric(db["Average (%)"]).mean()
    
    # High-level Metrics Display Row
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("Total Available Students", f"{total_records} Active")
    m_col2.metric("Total Passed (🏅 ≥40%)", f"{passed_count} Students")
    m_col3.metric("Total Failed (❌ <40%)", f"{failed_count} Students")
    m_col4.metric("Cohort Cumulative Average", f"{global_average:.2f}%")
    
    st.markdown("---")
    st.write("📈 **Peak Academic Achievement Tracking Per Subject Course**")
    
    # Sub-component metrics mapping highest grade per subject dynamically
    sub_metrics = st.columns(5)
    for index, course in enumerate(COURSES_LIST):
        col_pos = sub_metrics[index % 5]
        with col_pos:
            highest_mark = int(pd.to_numeric(db[course]).max())
            st.metric(f"🥇 Highest {course}", f"{highest_mark}/100")
            
    # Chart Visualizations Layout
    chart_l, chart_r = st.columns(2)
    with chart_l:
        st.plotly_chart(px.pie(db, names="Status", title="Cohort Distribution: Pass vs Fail Ratio", hole=0.3, color="Status", color_discrete_map={"Pass":"#2ecc71","Fail":"#e74c3c"}), use_container_width=True)
    with chart_r:
        st.plotly_chart(px.histogram(db, x="Average (%)", title="Overall Percentage Grade Density Spectrum Map", nbins=10), use_container_width=True)
else:
    st.info("Awaiting academic profile uploads to populate live descriptive statistics diagrams.")
