import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import pandas as pd
import random
import re
import os
from difflib import get_close_matches
import streamlit as st
import kagglehub
path = kagglehub.dataset_download("niksaurabh/doctors-speciality")

print("Path to dataset files:", path)

# Load the dataset into a Pandas DataFrame
csv_files = [file for file in os.listdir(path) if file.endswith('.csv')]

if csv_files:
    file_path = os.path.join(path, csv_files[0])
    df = pd.read_csv(file_path)

# Dictionary to store doctors by specialty
doctors_by_specialty = df.groupby('speciality')['Doctor\'s Name'].apply(list).to_dict()

# Mapping of symptoms to specialties
symptom_to_specialty = {
    "fever": "General Physician",
    "cough": "Pulmonologist",
    "chest pain": "Cardiologist",
    "skin rash": "Dermatologist",
    "eye pain": "Ophthalmologist",
    "toothache": "Dentist",
    "joint pain": "Orthopedic",
    "stomach pain": "Gastroenterologist"
}

# Initialize session state for appointments and user appointments
if "appointments" not in st.session_state:
    st.session_state["appointments"] = {}
if "user_appointments" not in st.session_state:
    st.session_state["user_appointments"] = {}

def send_email(to_email, subject, body):
    sender_email = "doctorappointmentchatbot@gmail.com"
    password = "tpvb nebt xkak azog"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, to_email, msg.as_string())
        st.success("Email sent successfully!")
    except Exception as e:
        st.error(f"Error sending email: {e}")

def validate_mobile(mobile):
    return re.match(r'^\d{10}$', mobile) is not None

def validate_name(name):
    return re.match(r'^[A-Za-z\s]+$', name) is not None

def parse_date(date_str):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return None

def parse_time(time_str):
    try:
        return datetime.strptime(time_str, "%I:%M %p").strftime("%I:%M %p")
    except ValueError:
        return None

def correct_spelling(input_word, word_list):
    matches = get_close_matches(input_word, word_list, n=1, cutoff=0.6)
    return matches[0] if matches else input_word

def is_past_date(date_str):
    today = datetime.today().strftime("%Y-%m-%d")
    return date_str < today

def is_past_time(date_str, time_str):
    if date_str == datetime.today().strftime("%Y-%m-%d"):
        current_time = datetime.now().strftime("%I:%M %p")
        return time_str < current_time
    return False

def is_same_day(date_str):
    return date_str == datetime.today().strftime("%Y-%m-%d")

def is_time_slot_available(date_str, time_str, doctor):
    if date_str in st.session_state["appointments"]:
        for booked_time, booked_doctor in st.session_state["appointments"][date_str].items():
            if booked_doctor == doctor:
                booked_time_dt = datetime.strptime(booked_time, "%I:%M %p")
                new_time_dt = datetime.strptime(time_str, "%I:%M %p")
                if abs((new_time_dt - booked_time_dt).total_seconds()) < 1200:  # 20 minutes in seconds
                    return False
    return True

def handle_chat():
    if "step" not in st.session_state:
        st.session_state["step"] = None
    if "appointment_details" not in st.session_state:
        st.session_state["appointment_details"] = {}

    user_input = st.chat_input("Type your message here...")

    if user_input:
        if st.session_state["step"] is None:
            st.session_state["step"] = "welcome"
            st.session_state["messages"] = []

        if st.session_state["step"] == "welcome":
            st.session_state["messages"].append({"role": "assistant", "content": "Welcome to the Hospital Appointment System! How can I assist you today?"})
            st.session_state["messages"].append({"role": "assistant", "content": "Please choose an option by typing the number:\n1. Book Appointment\n2. Reschedule Appointment\n3. Cancel Appointment\n4. Medical Info\n5. Exit"})
            st.session_state["step"] = "options"

        elif st.session_state["step"] == "options":
            if user_input == "1":
                st.session_state["step"] = "name"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Sure! Let's book an appointment. What's your name?"})
            elif user_input == "2":
                st.session_state["step"] = "reschedule_email"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Sure! Let's reschedule your appointment. What's your email address?"})
            elif user_input == "3":
                st.session_state["step"] = "cancel_email"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Sure! Let's cancel your appointment. What's your email address?"})
            elif user_input == "4":
                st.session_state["step"] = "medical_info"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Sure! What disease are you looking for information about?"})
            elif user_input == "5":
                st.session_state["messages"].append({"role": "assistant", "content": "Thank you for using the Hospital Appointment System. Goodbye!"})
                st.session_state["step"] = None
            else:
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Invalid option. Please choose a number from 1 to 5."})

        elif st.session_state["step"] == "name":
            if user_input.lower() == "back":
                st.session_state["step"] = "options"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the main menu. Please choose an option by typing the number:\n1. Book Appointment\n2. Reschedule Appointment\n3. Cancel Appointment\n4. Medical Info\n5. Exit"})
            else:
                st.session_state["appointment_details"]["name"] = user_input
                st.session_state["step"] = "email"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Got it! What's your email address?"})

        elif st.session_state["step"] == "email":
            if user_input.lower() == "back":
                st.session_state["step"] = "name"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. What's your name?"})
            else:
                st.session_state["appointment_details"]["email"] = user_input
                st.session_state["step"] = "mobile"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Great! What's your mobile number?"})

        elif st.session_state["step"] == "mobile":
            if user_input.lower() == "back":
                st.session_state["step"] = "email"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. What's your email address?"})
            elif not validate_mobile(user_input):
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Invalid mobile number. Please enter a 10-digit number."})
            else:
                st.session_state["appointment_details"]["mobile"] = user_input
                st.session_state["step"] = "age"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Thanks! What's your age?"})

        elif st.session_state["step"] == "age":
            if user_input.lower() == "back":
                st.session_state["step"] = "mobile"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. What's your mobile number?"})
            elif not user_input.isdigit():
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Invalid age. Please enter a number."})
            else:
                st.session_state["appointment_details"]["age"] = user_input
                st.session_state["step"] = "gender"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Got it! What's your gender? (Male/Female/Transgender)"})

        elif st.session_state["step"] == "gender":
            if user_input.lower() == "back":
                st.session_state["step"] = "age"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. What's your age?"})
            elif user_input.lower() not in ["male", "female", "transgender"]:
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Invalid gender. Please enter Male, Female, or Transgender."})
            else:
                st.session_state["appointment_details"]["gender"] = user_input
                st.session_state["step"] = "symptoms"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Thanks! What symptoms are you experiencing?"})

        elif st.session_state["step"] == "symptoms":
            if user_input.lower() == "back":
                st.session_state["step"] = "gender"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. What's your gender?"})
            else:
                corrected_symptoms = correct_spelling(user_input, symptom_to_specialty.keys())
                if corrected_symptoms != user_input:
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": f"Did you mean '{corrected_symptoms}'?"})
                    st.session_state["appointment_details"]["symptoms"] = corrected_symptoms
                else:
                    st.session_state["appointment_details"]["symptoms"] = user_input

                suggested_specialty = symptom_to_specialty.get(st.session_state["appointment_details"]["symptoms"], "General Physician")
                st.session_state["messages"].append({"role": "assistant", "content": f"Based on your symptoms, we recommend a {suggested_specialty}."})

                if suggested_specialty not in doctors_by_specialty:
                    st.session_state["messages"].append({"role": "assistant", "content": "No doctors available for the suggested specialty."})
                    st.session_state["step"] = None
                else:
                    doctors = doctors_by_specialty[suggested_specialty]
                    st.session_state["appointment_details"]["doctors"] = doctors
                    st.session_state["step"] = "select_doctor"
                    st.session_state["messages"].append({"role": "assistant", "content": "Here are the available doctors:"})
                    for idx, doctor in enumerate(doctors):
                        st.session_state["messages"].append({"role": "assistant", "content": f"{idx + 1}. {doctor}"})
                    st.session_state["messages"].append({"role": "assistant", "content": "Please select a doctor by typing the number."})

        elif st.session_state["step"] == "select_doctor":
            if user_input.lower() == "back":
                st.session_state["step"] = "symptoms"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. What symptoms are you experiencing?"})
            else:
                try:
                    doctor_choice = int(user_input) - 1
                    if doctor_choice < 0 or doctor_choice >= len(st.session_state["appointment_details"]["doctors"]):
                        st.session_state["messages"].append({"role": "user", "content": user_input})
                        st.session_state["messages"].append({"role": "assistant", "content": "Invalid selection. Please try again."})
                    else:
                        st.session_state["appointment_details"]["selected_doctor"] = st.session_state["appointment_details"]["doctors"][doctor_choice]
                        st.session_state["step"] = "appointment_date"
                        st.session_state["messages"].append({"role": "user", "content": user_input})
                        st.session_state["messages"].append({"role": "assistant", "content": "Great! When would you like to book the appointment? (YYYY-MM-DD or DD-MM-YYYY or MM/DD/YYYY or DD/MM/YYYY)"})
                except ValueError:
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Invalid input. Please enter a number."})

        elif st.session_state["step"] == "appointment_date":
            if user_input.lower() == "back":
                st.session_state["step"] = "select_doctor"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. Please select a doctor by typing the number."})
            else:
                parsed_date = parse_date(user_input)
                if not parsed_date:
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Invalid date format. Please use YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY, or DD/MM/YYYY."})
                elif is_past_date(parsed_date):
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Cannot book an appointment for a past date!"})
                else:
                    st.session_state["appointment_details"]["appointment_date"] = parsed_date
                    st.session_state["step"] = "appointment_time"
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Got it! What time would you like to book the appointment? (HH:MM AM/PM)"})

        elif st.session_state["step"] == "appointment_time":
            if user_input.lower() == "back":
                st.session_state["step"] = "appointment_date"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. When would you like to book the appointment? (YYYY-MM-DD or DD-MM-YYYY or MM/DD/YYYY or DD/MM/YYYY)"})
            else:
                parsed_time = parse_time(user_input)
                if not parsed_time:
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Invalid time format. Please use HH:MM AM/PM."})
                elif is_past_time(st.session_state["appointment_details"]["appointment_date"], parsed_time):
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Cannot book an appointment for a past time!"})
                elif not is_time_slot_available(st.session_state["appointment_details"]["appointment_date"], parsed_time, st.session_state["appointment_details"]["selected_doctor"]):
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "This time slot is already booked. Please choose another time."})
                else:
                    st.session_state["appointment_details"]["appointment_time"] = parsed_time
                    st.session_state["step"] = "confirm_appointment"
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Great! Here are your appointment details:"})
                    st.session_state["messages"].append({"role": "assistant", "content": f"Name: {st.session_state['appointment_details']['name']}"})
                    st.session_state["messages"].append({"role": "assistant", "content": f"Email: {st.session_state['appointment_details']['email']}"})
                    st.session_state["messages"].append({"role": "assistant", "content": f"Mobile: {st.session_state['appointment_details']['mobile']}"})
                    st.session_state["messages"].append({"role": "assistant", "content": f"Age: {st.session_state['appointment_details']['age']}"})
                    st.session_state["messages"].append({"role": "assistant", "content": f"Gender: {st.session_state['appointment_details']['gender']}"})
                    st.session_state["messages"].append({"role": "assistant", "content": f"Symptoms: {st.session_state['appointment_details']['symptoms']}"})
                    st.session_state["messages"].append({"role": "assistant", "content": f"Doctor: {st.session_state['appointment_details']['selected_doctor']}"})
                    st.session_state["messages"].append({"role": "assistant", "content": f"Date: {st.session_state['appointment_details']['appointment_date']}"})
                    st.session_state["messages"].append({"role": "assistant", "content": f"Time: {st.session_state['appointment_details']['appointment_time']}"})
                    st.session_state["messages"].append({"role": "assistant", "content": "Type 'confirm' to book the appointment or 'back' to go back."})

        elif st.session_state["step"] == "confirm_appointment":
            if user_input.lower() == "back":
                st.session_state["step"] = "appointment_time"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. What time would you like to book the appointment? (HH:MM AM/PM)"})
            elif user_input.lower() == "confirm":
                email = st.session_state["appointment_details"]["email"]
                selected_doctor = st.session_state["appointment_details"]["selected_doctor"]
                parsed_date = st.session_state["appointment_details"]["appointment_date"]
                appointment_time = st.session_state["appointment_details"]["appointment_time"]

                if not is_time_slot_available(parsed_date, appointment_time, selected_doctor):
                    st.session_state["messages"].append({"role": "assistant", "content": "This time slot is already booked. Please choose another time."})
                    st.session_state["step"] = "appointment_time"
                else:
                    if parsed_date not in st.session_state["appointments"]:
                        st.session_state["appointments"][parsed_date] = {}
                    st.session_state["appointments"][parsed_date][appointment_time] = selected_doctor

                    if email not in st.session_state["user_appointments"]:
                        st.session_state["user_appointments"][email] = set()
                    st.session_state["user_appointments"][email].add((parsed_date, selected_doctor))

                    appointment_id = f"APPT{len(st.session_state['user_appointments'])}"

                    user_body = f"""Hello {st.session_state['appointment_details']['name']},

Your appointment with {selected_doctor} has been successfully booked.

Appointment Date: {parsed_date}
Appointment Time: {appointment_time}
Appointment ID: {appointment_id}

Regards,
Hospital Management
"""
                    send_email(email, "Appointment Confirmation", user_body)
                    st.session_state["messages"].append({"role": "assistant", "content": "Appointment booked successfully! Confirmation email sent."})
                    st.session_state["step"] = None
            else:
                st.session_state["messages"].append({"role": "assistant", "content": "Invalid input. Type 'confirm' to book the appointment or 'back' to go back."})

        elif st.session_state["step"] == "reschedule_email":
            if user_input.lower() == "back":
                st.session_state["step"] = "options"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the main menu. Please choose an option by typing the number:\n1. Book Appointment\n2. Reschedule Appointment\n3. Cancel Appointment\n4. Medical Info\n5. Exit"})
            elif user_input not in st.session_state["user_appointments"] or not st.session_state["user_appointments"][user_input]:
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "No existing appointments found for this email. Please try again."})
            else:
                st.session_state["appointment_details"]["email"] = user_input
                st.session_state["step"] = "reschedule_select"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Here are your current appointments:"})
                appointment_list = list(st.session_state["user_appointments"][user_input])
                for idx, (date, doctor) in enumerate(appointment_list):
                    st.session_state["messages"].append({"role": "assistant", "content": f"{idx + 1}. {doctor} on {date}"})
                st.session_state["messages"].append({"role": "assistant", "content": "Please select an appointment to reschedule by typing the number."})

        elif st.session_state["step"] == "reschedule_select":
            if user_input.lower() == "back":
                st.session_state["step"] = "reschedule_email"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. What's your email address?"})
            else:
                try:
                    choice = int(user_input) - 1
                    appointment_list = list(st.session_state["user_appointments"][st.session_state["appointment_details"]["email"]])
                    if choice < 0 or choice >= len(appointment_list):
                        st.session_state["messages"].append({"role": "user", "content": user_input})
                        st.session_state["messages"].append({"role": "assistant", "content": "Invalid selection. Please try again."})
                    else:
                        st.session_state["appointment_details"]["old_date"], st.session_state["appointment_details"]["doctor"] = appointment_list[choice]
                        st.session_state["step"] = "reschedule_date"
                        st.session_state["messages"].append({"role": "user", "content": user_input})
                        st.session_state["messages"].append({"role": "assistant", "content": "Got it! What's the new appointment date? (YYYY-MM-DD or DD-MM-YYYY or MM/DD/YYYY or DD/MM/YYYY)"})
                except ValueError:
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Invalid input. Please enter a number."})

        elif st.session_state["step"] == "reschedule_date":
            if user_input.lower() == "back":
                st.session_state["step"] = "reschedule_select"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. Please select an appointment to reschedule by typing the number."})
            else:
                parsed_new_date = parse_date(user_input)
                if not parsed_new_date:
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Invalid date format. Please use YYYY-MM-DD, DD-MM-YYYY, MM/DD/YYYY, or DD/MM/YYYY."})
                elif is_past_date(parsed_new_date):
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Cannot reschedule to a past date!"})
                else:
                    st.session_state["appointment_details"]["new_date"] = parsed_new_date
                    st.session_state["step"] = "reschedule_time"
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Great! What's the new appointment time? (HH:MM AM/PM)"})

        elif st.session_state["step"] == "reschedule_time":
            if user_input.lower() == "back":
                st.session_state["step"] = "reschedule_date"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. What's the new appointment date? (YYYY-MM-DD or DD-MM-YYYY or MM/DD/YYYY or DD/MM/YYYY)"})
            else:
                parsed_new_time = parse_time(user_input)
                if not parsed_new_time:
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Invalid time format. Please use HH:MM AM/PM."})
                elif is_past_time(st.session_state["appointment_details"]["new_date"], parsed_new_time):
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Cannot reschedule to a past time!"})
                elif not is_time_slot_available(st.session_state["appointment_details"]["new_date"], parsed_new_time, st.session_state["appointment_details"]["doctor"]):
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "This time slot is already booked. Please choose another time."})
                else:
                    old_time = None
                    for time, doc in st.session_state["appointments"].get(st.session_state["appointment_details"]["old_date"], {}).items():
                        if doc == st.session_state["appointment_details"]["doctor"]:
                            old_time = time
                            break

                    st.session_state["appointments"][st.session_state["appointment_details"]["old_date"]].pop(old_time, None)
                    st.session_state["appointments"].setdefault(st.session_state["appointment_details"]["new_date"], {})[parsed_new_time] = st.session_state["appointment_details"]["doctor"]
                    st.session_state["user_appointments"][st.session_state["appointment_details"]["email"]].remove((st.session_state["appointment_details"]["old_date"], st.session_state["appointment_details"]["doctor"]))
                    st.session_state["user_appointments"][st.session_state["appointment_details"]["email"]].add((st.session_state["appointment_details"]["new_date"], st.session_state["appointment_details"]["doctor"]))

                    st.session_state["messages"].append({"role": "assistant", "content": "Appointment rescheduled successfully! Confirmation email sent."})
                    reschedule_body = f"""Hello,

Your appointment with {st.session_state['appointment_details']['doctor']} has been rescheduled.

New Appointment Date: {st.session_state['appointment_details']['new_date']}
New Appointment Time: {parsed_new_time}

Regards,
Hospital Management
"""
                    send_email(st.session_state["appointment_details"]["email"], "Appointment Rescheduled", reschedule_body)
                    st.session_state["step"] = None

        elif st.session_state["step"] == "cancel_email":
            if user_input.lower() == "back":
                st.session_state["step"] = "options"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the main menu. Please choose an option by typing the number:\n1. Book Appointment\n2. Reschedule Appointment\n3. Cancel Appointment\n4. Medical Info\n5. Exit"})
            elif user_input not in st.session_state["user_appointments"] or not st.session_state["user_appointments"][user_input]:
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "No existing appointments found for this email. Please try again."})
            else:
                st.session_state["appointment_details"]["email"] = user_input
                st.session_state["step"] = "cancel_select"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Here are your current appointments:"})
                appointment_list = list(st.session_state["user_appointments"][user_input])
                for idx, (date, doctor) in enumerate(appointment_list):
                    st.session_state["messages"].append({"role": "assistant", "content": f"{idx + 1}. {doctor} on {date}"})
                st.session_state["messages"].append({"role": "assistant", "content": "Please select an appointment to cancel by typing the number."})

        elif st.session_state["step"] == "cancel_select":
            if user_input.lower() == "back":
                st.session_state["step"] = "cancel_email"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the previous step. What's your email address?"})
            else:
                try:
                    choice = int(user_input) - 1
                    appointment_list = list(st.session_state["user_appointments"][st.session_state["appointment_details"]["email"]])
                    if choice < 0 or choice >= len(appointment_list):
                        st.session_state["messages"].append({"role": "user", "content": user_input})
                        st.session_state["messages"].append({"role": "assistant", "content": "Invalid selection. Please try again."})
                    else:
                        cancel_date, doctor = appointment_list[choice]
                        for time, doc in st.session_state["appointments"].get(cancel_date, {}).items():
                            if doc == doctor:
                                del st.session_state["appointments"][cancel_date][time]
                                break
                        st.session_state["user_appointments"][st.session_state["appointment_details"]["email"]].remove((cancel_date, doctor))

                        st.session_state["messages"].append({"role": "assistant", "content": "Appointment canceled successfully! Confirmation email sent."})
                        cancel_body = f"""Hello,

Your appointment with {doctor} on {cancel_date} has been successfully canceled.

Regards,
Hospital Management
"""
                        send_email(st.session_state["appointment_details"]["email"], "Appointment Cancellation", cancel_body)
                        st.session_state["step"] = None
                except ValueError:
                    st.session_state["messages"].append({"role": "user", "content": user_input})
                    st.session_state["messages"].append({"role": "assistant", "content": "Invalid input. Please enter a number."})

        elif st.session_state["step"] == "medical_info":
            if user_input.lower() == "back":
                st.session_state["step"] = "options"
                st.session_state["messages"].append({"role": "user", "content": user_input})
                st.session_state["messages"].append({"role": "assistant", "content": "Returning to the main menu. Please choose an option by typing the number:\n1. Book Appointment\n2. Reschedule Appointment\n3. Cancel Appointment\n4. Medical Info\n5. Exit"})
            else:
                disease = user_input
                today = datetime.today().strftime("%Y-%m-%d")
                simulated_count = random.randint(100, 5000)
                st.session_state["messages"].append({"role": "assistant", "content": f"As of {today}, approximately {simulated_count} patients are affected by {disease} in India."})
                st.session_state["step"] = None

    # Display chat messages
    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"]):
            st.write(message["content"])
import time

import streamlit as st

import streamlit as st

def main():
    st.markdown(
        """
        <style>
        /* Background with animated carousel of HD images */
        .stApp {
            background-size: cover;
            background-position: center;
            animation: changeBackground 20s infinite;
        }
        @keyframes changeBackground {
            0% { background-image: url('https://images.unsplash.com/photo-1576091160550-2173dba999ef?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); }
            33% { background-image: url('https://images.unsplash.com/photo-1629909613654-28e377c37b09?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); }
            66% { background-image: url('https://images.unsplash.com/photo-1532938911079-1b06ac7ceec7?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); }
            100% { background-image: url('https://images.unsplash.com/photo-1576091160550-2173dba999ef?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D'); }
        }

        /* Title with cartoon-style font and animation */
        .title {
            font-family: 'Poppins', sans-serif;
            font-size: 48px;
            font-weight: bold;
            color: #ffffff;
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, rgb(7, 4, 4), #fad0c4);
            border-radius: 15px;
            margin-bottom: 20px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        /* Chat bubbles with gradients and animations */
        .stChatMessage {
            background: linear-gradient(135deg, rgb(163, 190, 240), #c2e9fb);
            border-radius: 20px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            animation: slideIn 0.5s ease-in-out;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }

        /* User chat bubble */
        .user-message {
            background: linear-gradient(135deg, #84fab0, #8fd3f4);
            border-radius: 20px;
            padding: 15px;
            margin: 10px 0;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
            animation: slideIn 0.5s ease-in-out;
        }

        /* Typing animation for chatbot */
        .typing {
            display: inline-block;
            animation: typing 1s infinite;
        }
        @keyframes typing {
            0%, 100% { opacity: 0; }
            50% { opacity: 1; }
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Display the heading with emojis and cartoon-style font
    st.markdown(
        '<div class="title"> Doctor Appointment Chatbot </div>',
        unsafe_allow_html=True
    )

    # Run the chat
    handle_chat()

if __name__ == "__main__":
    main()