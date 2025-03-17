
import bcrypt  # Library for hashing passwords
import streamlit as st  # Library for creating interactive web applications
import pandas as pd  # Library for data manipulation and analysis
import sqlite3  # Library for interacting with SQLite databases

# Function to initialize the database
def init_db():
    with sqlite3.connect("medical.db") as conn:  # Connect to the SQLite database
        cursor = conn.cursor()  # Create a cursor object to interact with the database
        # Create the users table if it does not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier for each user
                email TEXT UNIQUE,  -- User's email must be unique
                password TEXT  -- User's password
            )
        """)
        # Create the doctors table if it does not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Unique identifier for each doctor
                name TEXT,  -- Doctor's name
                specialty TEXT,  -- Doctor's specialty
                rating REAL,  -- Doctor's rating
                image_url TEXT  -- URL for the doctor's image
            )
        """)
        conn.commit()  # Commit the changes to the database
# Function to register a new user
def register(email, password):
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()  # Hash the password
    try:
        with sqlite3.connect("medical.db") as conn:  # Connect to the database
            cursor = conn.cursor()  # Create a cursor object
            # Insert user data into the users table
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hashed_password))
            conn.commit()  # Commit the changes
        return True  # Registration successful
    except sqlite3.IntegrityError:
        return False  # Email already exists

# Function to log in a user
def login(email, password):
    with sqlite3.connect("medical.db") as conn:  # Connect to the database
        cursor = conn.cursor()  # Create a cursor object
        # Retrieve the stored password for the given email
        cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()  # Get the result of the query
    # Check if the entered password matches the stored password
    if user and bcrypt.checkpw(password.encode(), user[0].encode()):
        st.session_state.logged_in = True  # Set login state to True
        st.session_state.email = email  # Store the email in session state
        return True  # Login successful
    return False  # Login failed

# Function to load doctors from the database
def load_doctors():
    with sqlite3.connect("medical.db") as conn:  # Connect to the database
        return pd.read_sql("SELECT * FROM doctors", conn)  # Retrieve all doctor data

# Function to save a new doctor in the database
def save_doctor(name, specialty, rating, image_url):
    if not image_url:  # If no image URL is provided, use a default image
        image_url = "https://th.bing.com/th/id/OIP.1NS2gzdox57ZsKIz1URtGwHaIe?rs=1&pid=ImgDetMain"
    with sqlite3.connect("medical.db") as conn:  # Connect to the database
        cursor = conn.cursor()  # Create a cursor object
        # Insert doctor data into the doctors table
        cursor.execute("INSERT INTO doctors (name, specialty, rating, image_url) VALUES (?, ?, ?, ?)",
                       (name, specialty, rating, image_url))
        conn.commit()  # Commit the changes

# Function to update an existing doctor's information
def update_doctor(doctor_id, name, specialty, rating, image_url):
    if not image_url:  # If no image URL is provided, use a default image
        image_url = "https://th.bing.com/th/id/OIP.1NS2gzdox57ZsKIz1URtGwHaIe?rs=1&pid=ImgDetMain"
    with sqlite3.connect("medical.db") as conn:  # Connect to the database
        cursor = conn.cursor()  # Create a cursor object
        # Update doctor data in the doctors table
        cursor.execute("UPDATE doctors SET name = ?, specialty = ?, rating = ?, image_url = ? WHERE id = ?",
                       (name, specialty, rating, image_url, doctor_id))
        conn.commit()  # Commit the changes

# Function to display available doctors
def show_doctors(search_query=""):
    doctors = load_doctors()  # Load doctor data
    if search_query:  # If there is a search query, filter the doctors
        doctors = doctors[doctors['name'].str.contains(search_query, case=False, na=False) |
                          doctors['specialty'].str.contains(search_query, case=False, na=False)]
    
    st.subheader("👨‍⚕️ Available Doctors")  # Section title
    if doctors.empty:  # If no doctors are found
        st.warning("No doctors found.")  # Warning message
        return
    
    # Display information for each doctor
    for _, row in doctors.iterrows():
        with st.container():  # Create a new container for each doctor
            col1, col2 = st.columns([1, 3])  # Split the page into two columns
            with col1:
                # Display the doctor's image
                st.image(row['image_url'] or "https://th.bing.com/th/id/OIP.1NS2gzdox57ZsKIz1URtGwHaIe?rs=1&pid=ImgDetMain", width=120)
            with col2:
                # Display the doctor's name, specialty, and rating
                st.markdown(f"**{row['name']}**")
                st.markdown(f"*{row['specialty']}*")
                st.markdown(f"⭐ {row['rating']}")
                # Button to edit the doctor's information
                if st.button(f"Edit {row['name']}", key=row['id']):
                    set_edit_state(row)
                # Button to book an appointment with the doctor
                if st.button(f"Book with {row['name']}"):
                    st.session_state.selected_doctor = row['name']  # Store the selected doctor's name
                    st.session_state.page = "Book Appointment"  # Navigate to the booking page
                    st.rerun()  # Rerun the app

# Function to set the edit state for a doctor
def set_edit_state(row):
    st.session_state.editing_doctor = row['id']  # Store the ID of the doctor being edited
    st.session_state.edit_name = row['name']  # Store the doctor's name
    st.session_state.edit_specialty = row['specialty']  # Store the doctor's specialty
    st.session_state.edit_rating = row['rating']  # Store the doctor's rating
    st.session_state.edit_image_url = row['image_url']  # Store the doctor's image URL
    st.session_state.page = "Edit Doctor"  # Navigate to the edit doctor page
    st.rerun()  # Rerun the app

# Function to add a new doctor
def add_doctor():
    st.subheader("➕ Add a New Doctor")  # Section title
    name = st.text_input("Doctor's Name")  # Input field for the doctor's name
    specialty = st.selectbox("Specialty", ["Dentistry", "Surgery", "Physiotherapy", "Internal Medicine"])  # Dropdown for specialty
    rating = st.slider("Rating", 1.0, 5.0, 4.5, 0.1)  # Slider for rating
    image_url = st.text_input("Doctor's Image URL")  # Input field for the doctor's image URL
    if st.button("Add Doctor"):  # Button to add the doctor
        save_doctor(name, specialty, rating, image_url)  # Save the doctor's data
        st.success(f"Doctor {name} added successfully!")  # Success message
        st.session_state.show_add_doctor = False  # Hide the add doctor form
        st.rerun()  # Rerun the app

# Function to edit an existing doctor's information
def edit_doctor():
    st.subheader("✏️ Edit Doctor Information")  # Section title
    name = st.text_input("Doctor's Name", st.session_state.edit_name)  # Input field for the doctor's name with default value
    specialty = st.selectbox("Specialty", ["Dentistry", "Surgery", "Physiotherapy", "Internal Medicine"], 
                               index=["Dentistry", "Surgery", "Physiotherapy", "Internal Medicine"].index(st.session_state.edit_specialty))  # Dropdown for specialty with default value
    rating = st.slider("Rating", 1.0, 5.0, st.session_state.edit_rating, 0.1)  # Slider for rating with default value
    image_url = st.text_input("Doctor's Image URL", st.session_state.edit_image_url)  # Input field for the doctor's image URL with default value
    
    if st.button("Update Doctor"):  # Button to update the doctor's information
        update_doctor(st.session_state.editing_doctor, name, specialty, rating, image_url)  # Update the doctor's data
        st.success("Doctor information updated successfully!")  # Success message
        st.session_state.page = "Home"  # Navigate back to the home page
        st.rerun()  # Rerun the app

# Function to display the home page
def home():
    st.title("🏥 Medical Appointment Booking")  # Page title
    search_query = st.text_input("🔍 Search for a specialty or doctor")  # Input field for search query
    
    if st.button("➕ Add Doctor"):  # Button to add a doctor
        st.session_state.show_add_doctor = not st.session_state.show_add_doctor  # Toggle the add doctor form
    
    if st.session_state.show_add_doctor:  # If the add doctor form is shown
        add_doctor()  # Call the add doctor function
    
    show_doctors(search_query)  # Display available doctors

# Function to display the booking page
def booking():
    st.title("📅 Book an Appointment")  # Page title
    if not st.session_state.selected_doctor:  # If no doctor is selected
        st.warning("Please select a doctor first.")  # Warning message
        return
    
    st.subheader(f"Book an appointment with **{st.session_state.selected_doctor}**")  # Section title
    date = st.date_input("📆 Select Date")  # Input field for selecting the date
    time = st.time_input("⏰ Select Time")  # Input field for selecting the time
    
    if st.button("Confirm Booking"):  # Button to confirm the booking
        st.success(f"✅ Appointment booked successfully with **{st.session_state.selected_doctor}** on {date} at {time}.")  # Success message

    if st.button("🔙 Back to Home"):  # Button to go back to the home page
        st.session_state.page = "Home"  # Navigate back to the home page
        st.session_state.selected_doctor = None  # Reset the selected doctor
        st.rerun()  # Rerun the app
def show_login():
    st.title("🔑 Login / Sign Up")  # Title of the page for login or account creation
    tab1, tab2 = st.tabs(["Login", "Create Account"])  # Create tabs for login and account creation
    
    with tab1:  # Login tab
        email = st.text_input("Email")  # Input field for email
        password = st.text_input("Password", type="password")  # Input field for password (hidden)
        if st.button("Login"):  # Button to log in
            if login(email, password):  # Attempt to log in using the login function
                st.success("Login successful!")  # Success message upon successful login
                st.rerun()  # Rerun the app to update the state
            else:
                st.error("Invalid email or password.")  # Error message if the entered data is incorrect
    
    with tab2:  # Create Account tab
        new_email = st.text_input("New Email")  # Input field for new email
        new_password = st.text_input("New Password", type="password")  # Input field for new password (hidden)
        if st.button("Register"):  # Button to register
            if register(new_email, new_password):  # Attempt to register the new user using the register function
                st.success("Account created successfully! You can now log in.")  # Success message upon account creation
            else:
                st.error("Email already exists! Please try again.")  # Error message if the email already exists

# Initialize the database and session state
init_db()  # Call the function to initialize the database and create tables if they do not exist
if "logged_in" not in st.session_state:  # If there is no login state in the session
    st.session_state.logged_in = False  # Set login state to not logged in
    st.session_state.selected_doctor = None  # Reset the selected doctor
    st.session_state.page = "Home"  # Set the current page to home
    st.session_state.show_add_doctor = False  # Set the state to not show the add doctor form
    st.session_state.editing_doctor = None  # Reset the editing doctor state

# Main application logic
if not st.session_state.logged_in:  # If the user is not logged in
    show_login()  # Show the login page
else:  # If the user is logged in
    if st.session_state.page == "Home":  # If the current page is home
        home()  # Call the home function
    elif st.session_state.page == "Book Appointment":  # If the current page is the booking page
        booking()  # Call the booking function
    elif st.session_state.page == "Edit Doctor":  # If the current page is the edit doctor page
        edit_doctor()  # Call the edit doctor function