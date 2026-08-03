import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# --- 1. SECURE LOGIN SYSTEM & BRANDING AT THE ABSOLUTE TOP ---
ADMIN_USER = "professor"
ADMIN_PASSWORD = "liberia2029"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# If the user is NOT logged in, show ONLY the login form and your name
if not st.session_state.logged_in:
    st.set_page_config(page_title="Secure Login", page_icon="🔐", layout="centered")
    
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>🔐 Secure Academic Portal Access</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Please authenticate to access the data management system.</p>", unsafe_allow_html=True)
    
    # 🌟 Your Developer Branding is joined right here inside the gate
    st.markdown("<p style='text-align: center; color: #FFD700; font-weight: bold; font-size: 20px;'>Developed by: Mr Nathaniel Samah (IT Specialist)</p>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username_input = st.text_input("Username")
        password_input = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Authenticate Access")
        
        if login_submit:
            if username_input == ADMIN_USER and password_input == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("❌ Invalid Username or Password. Access Denied.")
    st.stop()  # Freeze everything below this line for unauthorized users
# --- END OF SECURITY GATE ---

# 1. Page Configuration
st.set_page_config(
    page_title="Professor's Student Records Portal",
    page_icon="🎓",
    layout="wide"
)

# 2. Header Section
st.title("🎓 Professor's Student Records & Analytics Portal")
st.write("An administrative database dashboard designed for educators to record student details, track marks, and monitor performance trends.")
st.markdown("---")

# 3.# 3. Session State Initialization (In-Memory Database per Session)
if 'student_db' not in st.session_state:
    # Creating an empty table with defined columns so every user starts completely fresh
    st.session_state.student_db = pd.DataFrame(columns=[
        "Roll Num", "Name", "Department", "Marks (%)", "Grade"
    ])


# 4. Layout Columns
col_form, col_table = st.columns(2, gap="large")

# --- LEFT COLUMN: TEACHER INPUT FORM ---
with col_form:
    st.subheader("➕ Add New Student Record")
    
    with st.form("student_entry_form", clear_on_submit=True):
        roll_num = st.number_input("Roll Number", min_value=1, step=1, value=104)
        student_name = st.text_input("Student Full Name", placeholder="Enter name here")
        department = st.selectbox("Department", ["IT", "Cyber Security", "Cloud Computing", "Computer Science", "Medical Lab Science"])
        marks = st.slider("Total Marks (%)", min_value=0, max_value=100, value=75)
        grade = st.selectbox("Final Grade", ["A+", "A", "B+", "B", "C", "Fail"])
        
        submit_button = st.form_submit_button("Save Student Record")

    if submit_button:
        if student_name.strip() == "":
            st.error("⚠️ Please enter a valid student name.")
        elif roll_num in st.session_state.student_db["Roll Num"].values:
            st.error(f"⚠️ Roll Number {roll_num} already exists in the system.")
        else:
            new_student = {
                "Roll Num": roll_num,
                "Name": student_name,
                "Department": department,
                "Marks (%)": marks,
                "Grade": grade
            }
            st.session_state.student_db = pd.concat(
                [st.session_state.student_db, pd.DataFrame([new_student])], 
                ignore_index=True
            )
            st.success(f"✅ Successfully added {student_name} to the database!")

# --- RIGHT COLUMN: DATABASE VIEW & EXPORT ---
with col_table:
    st.subheader("📊 Current Student Database")
    st.dataframe(st.session_state.student_db, use_container_width=True, hide_index=True)
    
    # Process Excel Download Data Safely
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        st.session_state.student_db.to_excel(writer, index=False, sheet_name="Student Records")
    excel_data = excel_buffer.getvalue()
    
    st.download_button(
        label="📥 Download Database as Excel Spreadsheet",
        data=excel_data,
        file_name="student_records.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        help="Click here to save this database as an official Microsoft Excel file (.xlsx)"
    )

st.markdown("---")

# 5. Bottom Section: Automated Analytics Dashboard
st.subheader("📈 Class Performance Analytics")

if not st.session_state.student_db.empty:
    total_students = len(st.session_state.student_db)
    average_score = st.session_state.student_db["Marks (%)"].mean()
    
    stat_col1, stat_col2, stat_col3 = st.columns(3)
    stat_col1.metric("Total Enrolled Students", f"{total_students} Students")
    stat_col2.metric("Class Average Marks", f"{average_score:.1f}%")
    stat_col3.metric("Highest Class Score", f"{st.session_state.student_db['Marks (%)'].max()}%")
    
    st.write("")
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        grade_counts = st.session_state.student_db["Grade"].value_counts().reset_index()
        grade_counts.columns = ["Grade", "Count"]
        fig_bar = px.bar(
            grade_counts, x="Grade", y="Count", 
            title="Distribution of Student Grades", color="Grade", text_auto=True
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with chart_col2:
        dept_counts = st.session_state.student_db["Department"].value_counts().reset_index()
        dept_counts.columns = ["Department", "Count"]
        fig_pie = px.pie(
            dept_counts, values="Count", names="Department", 
            title="Student Enrollment by Department", hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)
