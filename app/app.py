import streamlit as st
import mysql.connector
from mysql.connector import Error
from streamlit_option_menu import option_menu
import os # Import os module
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- UI Enhancements ---
st.set_page_config(page_title="Login & Register", page_icon="🧠", layout="wide") # Changed icon, wider layout

# Inject custom CSS for better styling
st.markdown("""
<style>
    /* General page styling */
    .main {
        background-color: #f0f2f6; /* Light grey background */
        padding: 2rem;
    }
    /* Center the main content block */
    [data-testid="stAppViewContainer"] > .main {
        max-width: 600px; /* Limit width for better readability */
        margin: auto;
        background-color: #ffffff; /* White card background */
        padding: 2rem 3rem;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    /* Input fields */
    .stTextInput > div > div > input {
        background-color: #f0f2f6; /* Light background for input */
        color: #333; /* Dark text color */
        border: 1px solid #ced4da;
        border-radius: 5px;
    }
    .stTextInput > label {
        font-weight: bold;
        color: #495057;
    }
    /* Button styling */
    .stButton > button {
        width: 100%;
        border: none;
        border-radius: 5px;
        padding: 0.75rem;
        font-weight: bold;
        color: white;
        background-color: #007bff; /* Primary blue */
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #0056b3; /* Darker blue on hover */
    }
    /* Option Menu styling */
    .st-emotion-cache-13ln4jf.ef3psqc7 {
        background-color: #e9ecef; /* Light background for menu */
        border-radius: 5px;
        padding: 0.5rem;
    }
    /* Title and headers */
    h1, h3 {
        color: #343a40; /* Dark grey for titles */
        text-align: center;
    }
    /* Center the image */
    div[data-testid="stImage"] { 
        text-align: center; 
    }
</style>
""", unsafe_allow_html=True)

# --- Database Connection ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"), # Use environment variable
            database=os.getenv("DB_DATABASE"), # Use environment variable
            user=os.getenv("DB_USER"), # Use environment variable
            password=os.getenv("DB_PASSWORD") # Use environment variable
        )
        # Create table if it doesn't exist (simple check)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
        cursor.close()
        return conn
    except Error as e:
        st.error(f"Database connection failed: {e}")
        return None

# --- User Registration ---
def register_user(email, username, password):
    conn = get_db_connection()
    if conn is None:
        return False, "Database connection error."
    cursor = conn.cursor()
    try:
        # Check if username or email already exists
        cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
        if cursor.fetchone():
            return False, "Username or Email already exists."
        
        # Basic validation (add more robust validation as needed)
        if not email or '@' not in email or '.' not in email:
            return False, "Invalid email format."
        if not username or len(username) < 3:
            return False, "Username must be at least 3 characters long."
        if not password or len(password) < 6:
             return False, "Password must be at least 6 characters long."

        # Hash password before storing (IMPORTANT for security - using plain text here for simplicity)
        # In a real app, use libraries like passlib: pip install passlib bcrypt
        # from passlib.context import CryptContext
        # pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # hashed_password = pwd_context.hash(password)
        # cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", (email, username, hashed_password))
        
        cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", (email, username, password))
        conn.commit()
        return True, "Account created successfully! You can now log in."
    except Error as e:
        return False, f"Registration failed: {e}"
    finally:
        cursor.close()
        conn.close()

# --- User Login ---
def login_user(identifier, password): # Changed parameter name from username to identifier
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor(dictionary=True) # Fetch as dict
    try:
        # Check if the identifier matches either username or email
        query = "SELECT * FROM users WHERE (username=%s OR email=%s) AND password=%s"
        cursor.execute(query, (identifier, identifier, password)) # Use identifier for both username and email check
        user = cursor.fetchone()
        if user:
            # Simple plain text comparison (as used in registration)
            # NOTE: In a real app, verify hashed password here
            return True # User found and password matches
        else:
            return False # User not found or password incorrect
    except Error as e:
        st.error(f"Login error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- Main App Layout ---
def main():
    # Check if we just successfully registered and show toast
    if st.session_state.get('registration_success', False):
        st.toast("Account created successfully! Please log in.", icon="✅")
        del st.session_state['registration_success'] # Clear the flag immediately
        # Don't set menu_selection here, use the force_login_tab flag below

    # Centered image and title
    st.image("https://cdn-icons-png.flaticon.com/512/1048/1048948.png", width=100) # Brain icon
    st.title("Student Depression Prediction")
    st.markdown("<p style='text-align: center; color: #6c757d;'>Login or Register to continue</p>", unsafe_allow_html=True)
    st.divider()

    # Determine the default index for the menu based on session state
    # Force Login tab if registration was just successful
    if st.session_state.get('force_login_tab', False):
        st.session_state['menu_selection'] = 0
        del st.session_state['force_login_tab'] # Clear the flag

    # Defaults to 0 (Login) if not set
    default_menu_index = st.session_state.get('menu_selection', 0)

    selected = option_menu(
        menu_title=None,
        options=["Login", "Register"],
        icons=["box-arrow-in-right", "person-plus-fill"],
        orientation="horizontal",
        default_index=default_menu_index, # Use the index from session state
        key='option_menu', # Assign a key
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff"}, # White background for menu container
            "icon": {"color": "#007bff", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#007bff", "color": "white", "font-weight": "bold"},
        }
    )

    # Store the *currently selected* index back into session state
    # This ensures if the user manually clicks a tab, it's remembered
    selected_index = ["Login", "Register"].index(selected)
    st.session_state['menu_selection'] = selected_index

    st.write("") # Add some space

    if selected == "Login":
        st.subheader("Login")
        with st.form("login_form"):
            identifier = st.text_input("Username or Email", key="login_identifier") # Changed label
            password = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login")
            if submitted:
                if not identifier or not password:
                    st.warning("Please enter both username/email and password.")
                elif login_user(identifier, password): # Pass identifier to login_user
                    st.session_state['logged_in'] = True
                    # Fetch username if identifier was email (optional, but good for display)
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor(dictionary=True)
                        cursor.execute("SELECT username FROM users WHERE username=%s OR email=%s", (identifier, identifier))
                        user_data = cursor.fetchone()
                        if user_data:
                            st.session_state['username'] = user_data['username']
                        else: 
                            st.session_state['username'] = identifier # Fallback if fetch fails
                        cursor.close()
                        conn.close()
                    else:
                         st.session_state['username'] = identifier # Fallback if DB connection fails
                         
                    st.success(f"Welcome back, {st.session_state['username']}!")
                    st.balloons()
                    st.snow() # Add snow animation
                    st.rerun() # Rerun to update the page state immediately
                else:
                    st.error("Invalid username/email or password.")

    elif selected == "Register":
        st.subheader("Create Account")
        with st.form("register_form"):
            email = st.text_input("Email", key="reg_email")
            username = st.text_input("Username", key="reg_user")
            password = st.text_input("Password", type="password", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm_pass")
            submitted = st.form_submit_button("Register")
            if submitted:
                if not email or not username or not password or not confirm_password:
                    st.warning("Please fill in all fields.")
                elif password != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(email, username, password)
                    if ok:
                        # Set flags for toast message and forcing login tab on rerun
                        st.session_state['registration_success'] = True
                        st.session_state['force_login_tab'] = True # Set the flag
                        st.balloons() # Add balloons animation
                        st.rerun() # Rerun to switch tab and show toast
                    else:
                        st.error(msg) # Show error on registration page

# --- Logged-in View (Simplified) ---
def show_main_app():
    st.sidebar.success(f"Logged in as {st.session_state.get('username', 'User')}")
    st.header("🧠 Student Depression Prediction App")
    st.success("You are successfully logged in!") # Confirmation message
    st.write("Welcome! The main application content will be built here.") # Simple placeholder text

    # Logout button remains in the sidebar
    if st.sidebar.button("Logout"):
        # Clear session state more robustly
        keys_to_delete = list(st.session_state.keys())
        for key in keys_to_delete:
            del st.session_state[key]
        st.rerun()

# --- Main Execution Logic ---
if __name__ == "__main__":
    if st.session_state.get('logged_in', False): # More robust check
        show_main_app() # Show the simplified main application page
    else:
        main() # Show the login/register UI
