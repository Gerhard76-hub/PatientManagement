import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from fpdf import FPDF

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# Function to get the file path for a specific user
def get_data_file():
    if st.session_state.logged_in_user:
        return f"{st.session_state.logged_in_user}_patients_data.json"
    return "patients_data.json"

# Load patient data from file
def load_data():
    data_file = get_data_file()
    if os.path.exists(data_file):
        with open(data_file, "r") as file:
            return json.load(file)
    return {}


# Initialize session state
if "patients" not in st.session_state:
    st.session_state.patients = load_data()
if "selected_patient" not in st.session_state:
    st.session_state.selected_patient = None


# Save patient data to file
def save_data():
    data_file = get_data_file()
    with open(data_file, "w") as file:
        json.dump(st.session_state.patients, file)





# Dummy user database
USER_CREDENTIALS = {
    "admin": "password123",
    "doctor1": "securepass",
}

# Generate PDF report
def generate_pdf(patient_name):
    patient_data = st.session_state.patients[patient_name]
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style='B', size=16)
    pdf.cell(200, 10, patient_name, ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Age: {patient_data['Age']}", ln=True)
    pdf.cell(200, 10, f"Weight: {patient_data['Weight']} kg", ln=True)
    pdf.cell(200, 10, f"Gender: {patient_data['Gender']}", ln=True)
    pdf.cell(200, 10, f"Height: {patient_data['Height']} cm", ln=True)
    pdf.cell(200, 10, f"Social Insurance Number: {patient_data['SV_Number']}", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", style='B', size=14)
    pdf.cell(200, 10, "Medication Logs", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    for med in patient_data["Medications"]:
        pdf.cell(200, 10, f"{med['Timestamp']} - {med['Medication']} - {med['Dosage']}", ln=True)
    pdf_output = f"{patient_name}_medication_report.pdf"
    pdf.output(pdf_output)
    return pdf_output

def login(username, password):
    if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
        st.session_state.logged_in_user = username
        st.session_state.patients = load_data()
        st.rerun()
    else:
        st.error("Invalid username or password.")

def logout():
    st.session_state.logged_in_user = None
    st.rerun()

def navigate_to_patient(patient_name):
    st.session_state.selected_patient = patient_name
    st.rerun()

def go_back():
    st.session_state.selected_patient = None
    st.rerun()

def add_patient(name, age, weight, gender, height, sv_number):
    if name in st.session_state.patients:
        st.error("Patient already exists.")
        return
    st.session_state.patients[name] = {
        "Age": age,
        "Weight": weight,
        "Gender": gender,
        "Height": height,
        "SV_Number": sv_number,
        "Medications": []
    }
    save_data()
    st.success(f"Patient {name} added successfully.")
    st.rerun()

def remove_patient(patient_name):
    if patient_name in st.session_state.patients:
        del st.session_state.patients[patient_name]
        save_data()
        st.success(f"Patient {patient_name} removed successfully.")
        st.rerun()
    else:
        st.error("Patient does not exist.")

def add_medication(patient_name, medication, dosage, timestamp):
    if patient_name not in st.session_state.patients:
        st.error("Patient does not exist.")
        return
    st.session_state.patients[patient_name]["Medications"].append(
        {
            "Medication": medication,
            "Dosage": dosage,
            "Timestamp": timestamp
        }
    )
    save_data()
    st.success(f"Medication added for {patient_name}.")
    st.rerun()

# Login screen
if st.session_state.logged_in_user is None:
    st.title("Login to Patient Management System")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login(username, password)
    st.stop()

# Main app
st.sidebar.write(f"Logged in as: {st.session_state.logged_in_user}")
if st.sidebar.button("Logout"):
    logout()

if st.session_state.selected_patient is None:
    st.title("Patient Management System")
    st.header("Select or Add a Patient")
    selected_patient = st.selectbox(
        "Choose a patient:",
        options=[""] + list(st.session_state.patients.keys()),
        format_func=lambda x: "Select a patient" if x == "" else x
    )
    if selected_patient and st.button("Manage Patient"):
        navigate_to_patient(selected_patient)

    st.header("Add a New Patient")
    with st.form("add_patient_form"):
        name = st.text_input("Name")
        age = st.number_input("Age", min_value=0, max_value=120, step=1)
        weight = st.number_input("Weight (kg)", min_value=0.0, step=0.1)
        gender = st.selectbox("Gender", options=["Male", "Female", "Other"])
        height = st.number_input("Height (cm)", min_value=0.0, step=0.1)
        sv_number = st.text_input("Social Insurance Number")
        submitted = st.form_submit_button("Add Patient")
        if submitted:
            add_patient(name, age, weight, gender, height, sv_number)
else:
    patient_name = st.session_state.selected_patient
    st.title(f"Manage Patient: {patient_name}")
    patient_data = st.session_state.patients[patient_name]
    st.header("Patient Details")
    st.write(f"**Age:** {patient_data['Age']}")
    st.write(f"**Weight:** {patient_data['Weight']} kg")
    st.write(f"**Gender:** {patient_data['Gender']}")
    st.write(f"**Height:** {patient_data['Height']} cm")
    st.write(f"**Social Insurance Number:** {patient_data['SV_Number']}")

    st.header("Add Medication")
    with st.form("add_medication_form"):
        medication = st.selectbox("Medication", options=["Medication A", "Medication B", "Medication C"])
        dosage = st.selectbox("Dosage", options=["100mg", "500mg", "1000mg"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        submitted_med = st.form_submit_button("Add Medication")
        if submitted_med:
            add_medication(patient_name, medication, dosage, timestamp)

    st.header("Medication Logs")
    if patient_data["Medications"]:
        for med in patient_data["Medications"]:
            st.write(f"{med['Timestamp']} - {med['Medication']} - {med['Dosage']}")
    else:
        st.write("No medications recorded.")


    if st.button("Generate PDF Report"):
        pdf_file = generate_pdf(patient_name)
        with open(pdf_file, "rb") as file:
            st.download_button("Download PDF", file, file_name=pdf_file, mime="application/pdf")

    if st.button("Remove Patient"):
        print("Aktuelle Patienten:", st.session_state.patients)
        print("Ausgewählter Patient:", patient_name)
        remove_patient(patient_name)

    if st.button("Back to Patient Selection"):
        go_back()

# How to start the webapp: (.venv) PS C:\GitProjects\musclecare> streamlit run PatientManagement.py --server.port 55442
