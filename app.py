import streamlit as st
import nltk
from transformers import pipeline
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import smtplib
import sqlite3
import time
# Initialize SQLite database
conn = sqlite3.connect("reminders.db")
cursor = conn.cursor()

# Create the reminders table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS reminders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        time TEXT NOT NULL
    )
""")
conn.commit()
conn.close()



# Initialize chatbot
chatbot = pipeline("text-generation", model="distilgpt2")

# Function to handle chatbot responses
def  healthcare_chatbot(user_input):
    
    if "symptom" in user_input:
        return "Please consult Doctor for accurate advice"
    elif "appointment" in user_input:
        return "Would you like to schedule appointment with the Doctor? "
    elif "medication" in user_input or "pill" in user_input or "medicine" in user_input:
        return "It's important to take prescribed medicines regularly. If you have concerns, consult your doctor."
    elif "prescription" in user_input:
        return "Please follow your doctor's prescription instructions carefully."
    else:
        response = chatbot(user_input, max_length=500, num_return_sequences=1)
        return response[0]['generated_text']
    

# Function to add a reminder
def add_reminder(time):
    conn = sqlite3.connect("reminders.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reminders (time) VALUES (?)", (time,))
    conn.commit()
    conn.close()

# Function to check reminders
def check_reminders():
    conn = sqlite3.connect("reminders.db")
    cursor = conn.cursor()
    
    # Get the current time in HH:MM format
    current_time = datetime.now().strftime("%H:%M")

    # Fetch reminders matching current time
    cursor.execute("SELECT * FROM reminders WHERE time = ?", (current_time,))
    reminders = cursor.fetchall()

    # If reminders match the current time, show notifications
    for reminder in reminders:
        st.warning(f"⏰ Reminder Alert: Take your medication at {reminder[1]}!")

    conn.close()


# Start Background Scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(check_reminders, "interval", minutes=1)
scheduler.start()



# Function to handle user authentication
def authenticate(username, password):
    # Simple authentication logic (replace with a real authentication mechanism)
    if username == "user" and password == "pass":
        return True
    return False


# Main function
def main():
    st.title("💊 HealthCare Assistant Chatbot ")

    # User authentication
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.session_state.chat_history = []
            else:
                st.error(" ❌ Invalid username or password")
        return


    # Chatbot interaction
    user_input=st.text_input("Hello! How can I assist you today?")
    if st.button("Submit"):
        if user_input:
            st.write("User:", user_input)
            with st.spinner("processing..."):
                 response=healthcare_chatbot(user_input)
                 st.write("HealthAssistant:", response)
            
            print(response)
        else:
            st.write("⚠️ Please enter your query.")

    # Display chat history
    if st.session_state.chat_history:
        st.write("📜 **Chat History:**")
        for user_input, response in st.session_state.chat_history:
            st.write(f"👤 **User:** {user_msg}")
            st.write(f"🤖 **HealthAssistant:** {response}")
    
    # Logout button
    if st.button("Logout"):
        st.session_state.authenticated = False

    # Additional features
    st.sidebar.title("📌 Additional Features")

    # Appointment scheduling
    if st.sidebar.button(" 📅 Schedule Appointment"):
        appointment_date = st.sidebar.date_input(" 📅 Select Date", datetime.now())
        appointment_time = st.sidebar.time_input(" ⏰Select Time", datetime.now().time())
        st.sidebar.write(f" ✅Appointment scheduled for 📅 {appointment_date} at ⏰{appointment_time}")

    # Medication reminders
    if st.sidebar.button("⏰ Set Medication Reminder"):
        reminder_time = st.sidebar.time_input(" ⏰ Reminder Time", datetime.now().time())
        st.sidebar.write(f" ✅ Medication reminder set for {reminder_time}")
 

    # Health tips
    if st.sidebar.button("💡 Get Health Tip"):
        st.sidebar.write("🩺 **Tip:** Drink plenty of water and stay hydrated!")


    
main()