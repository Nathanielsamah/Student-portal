import streamlit as st
import pandas as pd
import plotly.express as px
import json
from io import BytesIO  # Handles file memory for the Excel download
from streamlit_local_storage import LocalStorage  # Saves data directly to browser hard drive

# --- CONFIGURATION: SET YOUR MASTER CREDENTIALS HERE ---


# 1. Page Configuration and Theme Styling
st.set_page_config(
    page_title="Professor's Student Records Portal",
    page_icon="🎓",
    layout="wide"
)

# Initialize login state across refreshes
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 2. Sidebar Login & Management Panel
st.sidebar.title("🔐 System Panel")

if not st.session_state.logged_in:
    # Show Login form if not logged in
    input_id = st.sidebar.text_input("Enter Master ID:")
    input_password = st.sidebar.text_input("Enter Password:", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        if input_id == MASTER_ID and input_password == MASTER_PASSWORD:
            st.session_state.logged_in = True
            st.sidebar.success("✅ Login Successful!")
            st.rerun()
        else:
            st.sidebar.error("❌ Incorrect ID or Password.")
else:
    # Show Control buttons if already logged in
    st.sidebar.success(f"Logged in as: **{MASTER_ID}**")
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("🛠️ Administrative Controls")
    
    # CLEAR ALL DATA BUTTON
    if st.sidebar.button("🗑️ Clear All Student Data", help="This will permanently delete all records saved on this device."):
        # 1. Wipe local memory dataframe
        st.session_state.student_db = pd.DataFrame(columns=["Roll Num", "Name", "Department", "Marks (%)", "Grade"])
        # 2. Clear browser hard drive cache
        local_storage = LocalStorage()
        local_storage.setItem("permanent_student_db_master", "")
        st.sidebar.warning("💥 All local student data has been wiped!")
        st.rerun()
        
    # LOGOUT BUTTON
    if st.sidebar.button("🚪 Log Out"):
        st.session_state.logged_in = False
        st.rerun()

# Check if user is authenticated
if not st.session_state.logged_in:
    st.title("🎓 Professor's Student Records & Analytics Portal")
    st.warning("🔒 Access Denied. Please enter the correct Master ID and Password in the sidebar to unlock the portal.")
    st.stop()  # Stops execution right here if credentials don't match

# 3. Header Section (Only shows AFTER successful login)
st.title("🎓 Professor's Student Records & Analytics Portal")
st.write("An administrative database dashboard designed for educators to record student details, track marks, and monitor performance trends.")
st.markdown("---")

# 4. PERMANENT LOCAL STORAGE INITIALIZATION
local_storage = LocalStorage()

# Fetch data from the teacher's browser hard drive
saved_json = local_storage.getItem("permanent_student_db_master")

# Initialize the central session table
if 'student_db' not in st.session_state:
    if saved_json and saved_json.strip() != "":
        try:
            data_dict = json.loads(saved_json)
            st.session_state.student_db = pd.DataFrame(data_dict)
        except Exception:
            st.session_state.student_db = pd.DataFrame(columns=["Roll Num", "Name", "Department", "Marks (%)", "Grade"])
    else:
        st.session_state.student_db = pd.DataFrame(columns=["Roll Num", "Name", "Department", "Marks (%)", "Grade"])

# 5. Layout: Split Screen into Input Form (Left) and Data View (Right)
col_form, col_table = st.columns([1, 2], gap="large")

# --- LEFT COLUMN: TEACHER INPUT FORM ---
with col_form:
    st.subheader("➕ Add New Student Record")
    
    with st.form("student_entry_form", clear_on_submit=True):
        roll_num = st.number_input("Roll Number", min_value=1, step=1, value=104)
        student_name = st.text_input("Student Full Name", placeholder="Enter name here")
        department = st.selectbox("Department", ["IT", "Cyber Security", "Cloud Computing", "Computer Science"])
        marks = st.slider("Total Marks (%)", min_value=0, max_value=100, value=75)
        grade = st.selectbox("Final Grade", ["A+", "A", "B+", "B", "C", "Fail"])
        
        submit_button = st.form_submit_button("Save Student Record")

    # --- SAVE LOGIC ---
    if submit_button:
        if student_name.strip() == "":
            st.error("⚠️ Please enter a valid student name.")
        elif not st.session_state.student_db.empty and roll_num in st.session_state.student_db["Roll Num"].values:
            st.error(f"⚠️ Roll Number {roll_num} already exists in the system.")
        else:
            new_student = {
                "Roll Num": int(roll_num),
                "Name": student_name,
                "Department": department,
                "Marks (%)": int(marks),
                "Grade": grade
            }
            # Add directly into running session dataframe
            st.session_state.student_db = pd.concat(
                [st.session_state.student_db, pd.DataFrame([new_student])], 
                ignore_index=True
            )
            
            # Save permanently to the browser hard drive
            updated_json = st.session_state.student_db.to_json(orient="records")
            local_storage.setItem("permanent_student_db_master", updated_json)
            
            st.success(f"✅ Successfully saved {student_name} permanently to your device!")

# --- RIGHT COLUMN: DATABASE VIEW & EXPORT ---
with col_table:
    st.subheader("📊 Current Student Database")
    
    # Display the interactive spreadsheet table
    st.dataframe(st.session_state.student_db, use_container_width=True, hide_index=True)
    
    # --- PROCESS DATA INTO EXCEL FORMAT ---
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        st.session_state.student_db.to_excel(writer, index=False, sheet_name="Student Records")
    excel_data = excel_buffer.getvalue()
    
    # Download Button configured for Excel (.xlsx)
    st.download_button(
        label="📥 Download Database as Excel Spreadsheet",
        data=excel_data,
        file_name="student_records.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Click here to save this database as an official Microsoft Excel file (.xlsx)"
    )

st.markdown("---")

# 6. Bottom Section: Automated Analytics Dashboard
st.subheader("📈 Class Performance Analytics")

if not st.session_state.student_db.empty:
    # Calculations
    total_students = len(st.session_state.student_db)
    average_score = pd.to_numeric(st.session_state.student_db["Marks (%)"]).mean()
    
    # Summary Display Cards
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    stat_col1.metric("Total Enrolled Students", f"{total_students} Students")
    stat_col2.metric("Class Average Marks", f"{average_score:.1f}%")
    stat_col3.metric("Highest Class Score", f"{pd.to_numeric(st.session_state.student_db['Marks (%)']).max()}%")
    
    # Graphical Charting via Plotly
    st.write("")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Grade Count Bar Chart
        grade_counts = st.session_state.student_db["Grade"].value_counts().reset_index()
        grade_counts.columns = ["Grade", "Count"]
        
        fig_bar = px.bar(
            grade_counts, 
            x="Grade", 
            y="Count", 
            title="Distribution of Student Grades",
            color="Grade",
            text_auto=True
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with chart_col2:
        # Department Wise Distribution
        dept_counts = st.session_state.student_db["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        
        fig_pie = px.pie(
            dept_counts, 
            values="Count", 
            names="Department", 
            title="Student Enrollment by Department",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
else:
    st.info("The database is currently empty. Add student records to generate live analytics.")
