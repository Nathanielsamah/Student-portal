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

# --- CONFIGURATION: SUBJECTS WITH CODES & TYPES MATCHING THE IMAGE ---
SUBJECTS_DATA = [
    {"code": "UGCA1913", "name": "Computer Networks", "type": "Theory", "credits": 4},
    {"code": "UGCA1916", "name": "Computer Networks Laboratory", "type": "Practical", "credits": 2},
    {"code": "UGCA1927", "name": "Web Designing", "type": "Theory", "credits": 3},
    {"code": "UGCA1928", "name": "Web Designing Laboratory", "type": "Practical", "credits": 1},
    {"code": "UGCA1932", "name": "Programming in Java", "type": "Theory", "credits": 4},
    {"code": "UGCA1938", "name": "Programming in Java Laboratory", "type": "Practical", "credits": 2},
    {"code": "UGCA1961", "name": "Basic Accounting", "type": "Theory", "credits": 4},
    {"code": "UGCA1962", "name": "Basic Accounting Laboratory", "type": "Practical", "credits": 2},
    {"code": "BMPD402", "name": "Mentoring and Professional Development", "type": "Practical", "credits": 1}
]

# Automated Grading Function
def calculate_grade(score):
    if score >= 90: return "A+"
    elif score >= 80: return "A"
    elif score >= 70: return "B+"
    elif score >= 60: return "B"
    elif score >= 50: return "C"
    elif score >= 40: return "P"
    else: return "F"

# Grade Point calculation for SGPA estimation
def grade_to_points(grade):
    mapping = {"A+": 10, "A": 9, "B+": 8, "B": 7, "C": 6, "P": 5, "F": 0}
    return mapping.get(grade, 0)

# 1. Page Configuration
st.set_page_config(
    page_title="University Grade Sheet Management Portal",
    page_icon="🎓",
    layout="wide"
)

# Inject print optimization styles
st.markdown("""
<style>
@media print {
    .stApp > header, [data-testid="stSidebar"], [data-testid="stForm"], button, .no-print, [data-testid="stHeader"] {
        display: none !important;
    }
    .print-container {
        display: block !important;
        width: 100% !important;
        border: none !important;
        padding: 0 !important;
    }
}
</style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 2. Sidebar Navigation Control Panel
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
    
    if st.sidebar.button("🗑️ Wipe Entire Database"):
        st.session_state.student_db = pd.DataFrame()
        local_storage = LocalStorage()
        local_storage.setItem("uni_master_db_v2", "")
        st.sidebar.warning("💥 Database cleared!")
        st.rerun()
        
    if st.sidebar.button("🚪 System Logout"):
        st.session_state.logged_in = False
        st.rerun()

if not st.session_state.logged_in:
    st.title("🎓 University Academic Record & Grade Sheet System")
    st.warning("🔒 Access Denied. Please input authentication credentials in the sidebar panel.")
    st.stop()

# 3. Main Workspace Setup
st.title("🎓 University Academic Record & Grade Sheet System")
st.write("Six-Week Python Training Project: Automated Performance Assessment Engine.")
st.markdown("---")

local_storage = LocalStorage()
saved_json = local_storage.getItem("uni_master_db_v2")

if 'student_db' not in st.session_state:
    if saved_json and saved_json.strip() != "":
        try:
            st.session_state.student_db = pd.DataFrame(json.loads(saved_json))
        except Exception:
            st.session_state.student_db = pd.DataFrame()
    else:
        st.session_state.student_db = pd.DataFrame()

# 4. Interface Split Layout Configuration
col_form, col_table = st.columns(2, gap="large")

with col_form:
    st.subheader("I.K. Gujral Punjab Technical University Entry Form")
    
    with st.form("academic_entry_form", clear_on_submit=False):
        selected_uni = st.selectbox("Select University Header:", [
            "I.K. GUJRAL PUNJAB TECHNICAL UNIVERSITY"
        ])
        selected_college = st.selectbox("Name of the College/Institute:", [
            "Synetic Business School, Sahibana, Ludhiana"
        ])
        department = st.selectbox("Department / Course Stream:", [
            "Bachelor of Science (Information Technology)", 
            "Computer Science & Engineering", 
            "Business Administration"
        ])
        semester = st.selectbox("Semester:", ["FIRST Semester", "SECOND Semester", "THIRD Semester", "FOURTH Semester"])
        exam_session = st.text_input("Examination Session Date:", value="April-2025")
        issue_date = st.date_input("Date of Issue:", date.today())
        
        st.markdown("---")
        student_name = st.text_input("Student Full Name:")
        father_name = st.text_input("Father's Name:")
        mother_name = st.text_input("Mother's Name:")
        roll_num = st.number_input("Regn. cum Roll No:", min_value=1, step=1, value=2221757)
        
        st.markdown("---")
        st.write("📊 **Enter Subject Marks (0 - 100)**")
        
        form_scores = {}
        for sub in SUBJECTS_DATA:
            form_scores[sub["name"]] = st.number_input(f"{sub['name']} ({sub['code']}):", min_value=0, max_value=100, value=0)
            
        submit_record = st.form_submit_button("💾 Save Student Record")

    if submit_record:
        if not student_name.strip():
            st.error("⚠️ Record rejected: Student Full Name field cannot be empty.")
        else:
            # Calculation operations 
            total_credits = sum([sub["credits"] for sub in SUBJECTS_DATA])
            weighted_points = 0
            pass_status = "Pass"
            
            new_entry = {
                "University": selected_uni,
                "College": selected_college,
                "Department": department,
                "Semester": semester,
                "Session": exam_session,
                "Date": str(issue_date),
                "Roll Num": int(roll_num),
                "Name": student_name,
                "Father Name": father_name,
                "Mother Name": mother_name
            }
            
            for sub in SUBJECTS_DATA:
                score = form_scores[sub["name"]]
                grade = calculate_grade(score)
                if grade == "F": pass_status = "Fail"
                
                new_entry[f"{sub['name']}_Score"] = int(score)
                new_entry[f"{sub['name']}_Grade"] = grade
                weighted_points += grade_to_points(grade) * sub["credits"]
                
            sgpa = weighted_points / total_credits
            new_entry["SGPA"] = round(sgpa, 2)
            new_entry["Status"] = pass_status
            
            st.session_state.student_db = pd.concat([st.session_state.student_db, pd.DataFrame([new_entry])], ignore_index=True)
            local_storage.setItem("uni_master_db_v2", st.session_state.student_db.to_json(orient="records"))
            st.success(f"✅ Securely committed transcript profile for {student_name}!")
            st.rerun()

with col_table:
    st.subheader("📋 Centralized Master Transcript Ledger")
    
    if not st.session_state.student_db.empty:
        display_df = st.session_state.student_db[["Department", "Roll Num", "Name", "SGPA", "Status"]]
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Target Selection for Certificate Print Preview
        st.markdown("---")
        st.subheader("🖨️ Select Student To Print Grade Sheet")
        target_student = st.selectbox("Choose Student Profile:", st.session_state.student_db["Name"].unique())
        
        # FIX: Added .iloc[0] to fetch the single active data matching row safely
        student_row = st.session_state.student_db[st.session_state.student_db["Name"] == target_student].iloc[0]
    else:
        st.info("System ledger pipeline is empty. Submit a transcript record to view printable output sheets.")

st.markdown("---")

# 5. PRINTABLE REPORT CARD CODE COMPONENT (SAFE LIST-JOIN SOLUTION)
if not st.session_state.student_db.empty:
    st.subheader("🖨️ Grade Sheet Print Preview")
    st.info("💡 Pro Tip: To print this sheet cleanly, press Ctrl+P (or Cmd+P on Mac). The application layout will disappear automatically, leaving only the official document sheet template visible.")
    
    # Compile rows layout for the dynamic HTML transcript table
    table_rows_html = ""
    for sub in SUBJECTS_DATA:
        grade_val = student_row[f"{sub['name']}_Grade"]
        table_rows_html += f"""
        <tr>
            <td style="border: 1px solid black; padding: 6px; text-align: center;">{sub['code']}</td>
            <td style="border: 1px solid black; padding: 6px; text-align: left;">{sub['name']}</td>
            <td style="border: 1px solid black; padding: 6px; text-align: center;">{sub['type']}</td>
            <td style="border: 1px solid black; padding: 6px; text-align: center;">{sub['credits']}</td>
            <td style="border: 1px solid black; padding: 6px; text-align: center; font-weight: bold;">{grade_val}</td>
        </tr>
        """
        
    # Crash-proof single line list join composition instead of a multi-line literal string block
    html_lines = [
