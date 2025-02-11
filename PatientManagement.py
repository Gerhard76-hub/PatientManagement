import streamlit as st
import pandas as pd
from datetime import datetime

# Initialize session state
if "patients" not in st.session_state:
    st.session_state.patients = {}
if "selected_patient" not in st.session_state:
    st.session_state.selected_patient = None

def navigate_to_patient(patient_name):
    st.session_state.selected_patient = patient_name

def go_back():
    st.session_state.selected_patient = None

# Add a new patient
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
    st.success(f"Patient {name} added successfully.")

# Add a medication log
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
    st.success(f"Medication added for {patient_name}.")

# Main app
if st.session_state.selected_patient is None:
    st.title("Patient Management System")

    # Patient selection
    st.header("Select or Add a Patient")
    selected_patient = st.selectbox(
        "Choose a patient:",
        options=[""] + list(st.session_state.patients.keys()),
        format_func=lambda x: "Select a patient" if x == "" else x
    )

    if selected_patient:
        if st.button("Manage Patient"):
            navigate_to_patient(selected_patient)

    # Add patient section
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
    # Patient details and medications
    patient_name = st.session_state.selected_patient
    st.title(f"Manage Patient: {patient_name}")

    patient_data = st.session_state.patients[patient_name]

    st.header("Patient Details")
    st.write(f"**Age:** {patient_data['Age']}")
    st.write(f"**Weight:** {patient_data['Weight']} kg")
    st.write(f"**Gender:** {patient_data['Gender']}")
    st.write(f"**Height:** {patient_data['Height']} cm")
    st.write(f"**Social Insurance Number:** {patient_data['SV_Number']}")

    # Add medication section
    st.header("Add Medication")
    with st.form("add_medication_form"):
        medication = st.selectbox("Medication", options=["Medication A", "Medication B", "Medication C"])
        dosage = st.selectbox("Dosage", options=["100mg", "500mg", "1000mg"])
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        submitted_med = st.form_submit_button("Add Medication")
        if submitted_med:
            add_medication(patient_name, medication, dosage, timestamp)

    # Show medication logs
    st.header("Medication Logs")
    meds = patient_data["Medications"]
    if meds:
        df = pd.DataFrame(meds)
        st.dataframe(df)
        if st.button("Print Medication Logs"):
            st.download_button(
                label="Download Medication Logs as CSV",
                data=df.to_csv(index=False),
                file_name=f"{patient_name}_medication_logs.csv",
                mime="text/csv"
            )
    else:
        st.info("No medications logged yet.")

    if st.button("Back to Patient Selection"):
        go_back()



#How to start the webapp: (.venv) PS C:\GitProjects\musclecare> streamlit run PatientManagement.py --server.port 55442