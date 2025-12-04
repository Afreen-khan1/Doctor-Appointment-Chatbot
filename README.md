## Overview
The **Doctor Appointment Chatbot** is a web-based application designed to help users book, reschedule, or cancel appointments with doctors. It also provides medical information based on user queries. The chatbot uses a **symptom-to-specialty mapping** to recommend the right type of doctor for the user’s condition. Built using **Python** and **Streamlit**, the chatbot offers a user-friendly interface and efficient backend processing.

## Live Demo
You can access the live demo of Doctor Appointment Chatbot here:
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://doctor-appointment-chatbot-9ob25eg32ofzswfwde7k5q.streamlit.app/)

## Features
- **Appointment Management**: Book, reschedule, or cancel appointments seamlessly.
- **Symptom-Based Recommendations**: The chatbot recommends the appropriate specialist based on the user’s symptoms.
- **Email Notifications**: Users receive confirmation emails for their appointments.
- **Data Validation**: Ensures that user inputs like email, phone number, and dates are valid before proceeding.
- **User-Friendly Interface**: Simple and clean design with clear visual indicators for different actions.

## Technology Stack
- **Streamlit**: For building the interactive web interface.
- **Pandas**: For handling the dataset of doctors and their specialties.
- **SMTP Library**: For sending email notifications.
- **Regex**: For validating user inputs like email, phone numbers, and dates.

## Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Afreen-khan1/Doctor-Appointment-Chatbot.git
   cd Doctor-Appointment-Chatbot
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   streamlit run infosys.py
   ```

4. **Access the Chatbot**:
   Open your web browser and navigate to `http://localhost:8501`.

## Usage
1. **Book an Appointment**:
   - Select the option to book an appointment.
   - Enter your details (name, email, phone number, age, gender, and symptoms).
   - The chatbot will recommend a specialist based on your symptoms.
   - Choose a doctor, date, and time for your appointment.
   - Confirm the appointment to receive a confirmation email.

2. **Reschedule an Appointment**:
   - Select the option to reschedule an appointment.
   - Enter your email address to view your current appointments.
   - Choose the appointment you want to reschedule.
   - Select a new date and time for the appointment.
   - Confirm the rescheduling to receive a confirmation email.

3. **Cancel an Appointment**:
   - Select the option to cancel an appointment.
   - Enter your email address to view your current appointments.
   - Choose the appointment you want to cancel.
   - Confirm the cancellation to receive a confirmation email.

4. **Medical Information**:
   - Select the option to get medical information.
   - Enter the disease you want information about.
   - The chatbot will provide statistics and information about the disease.

## Dataset
The dataset is stored in a CSV file inside the project and contains doctor names and specialties.

## Future Enhancements
- **Integration with Calendar APIs**: To sync appointments with Google Calendar or Outlook.
- **Multilingual Support**: To make the chatbot accessible to a wider audience.
- **AI-Powered Recommendations**: Using machine learning to provide more accurate doctor recommendations based on user history.
- **Voice Input**: Allowing users to interact with the chatbot using voice commands.


## Developer
Afreen Ahamed

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

