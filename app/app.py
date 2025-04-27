import streamlit as st
import mysql.connector
from mysql.connector import Error
from streamlit_option_menu import option_menu
import os # Import os module
from dotenv import load_dotenv # Import load_dotenv
import datetime # Added datetime import

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
    /* Compact sidebar user info */
    .user-info-sidebar {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 0.75rem;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        font-size: 0.9rem;
        border-left: 3px solid #007bff;
    }
    .user-icon {
        background-color: #007bff;
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
    }
    /* Step indicator styling */
    .step-container {
        margin: 20px 0;
        border-left: 3px solid #007bff;
        padding-left: 15px;
    }
    .step-number {
        background-color: #007bff;
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .step-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #343a40;
        display: inline;
        vertical-align: middle;
    }
    /* Form section styling */
    .form-section {
        background-color: #212529; /* Dark background for form sections */
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        border-left: 3px solid #6c757d;
        transition: all 0.3s ease;
    }
    .form-section:hover {
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        border-left: 3px solid #007bff;
    }
    /* Ensure text in form sections is light enough for contrast on dark background */
    .form-section p, .form-section li {
        color: #e9ecef; /* Light text color for dark background */
        font-size: 1rem;
        line-height: 1.5;
    }
    .form-section strong {
        color: #ffffff; /* Bright white for emphasis */
    }
    .form-section h3 {
        color: #ffffff; /* White for headings */
    }
    .metric-item {
        flex: 1;
        min-width: 120px;
        background-color: #343a40; /* Dark background for metric items */
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        text-align: center;
        transition: transform 0.2s ease;
    }
    .metric-item:hover {
        transform: scale(1.03);
        background-color: #3e444a; /* Slightly lighter on hover */
    }
    .metric-item div {
        color: #e9ecef; /* Light text for metric items */
    }
    .metric-item p {
        color: #e9ecef; /* Light text color for better readability on dark */
    }
    .primary-metric {
        border-left: 3px solid #007bff;
        background-color: rgba(0, 123, 255, 0.15); /* Slightly transparent blue on dark */
    }
    /* Progress bar */
    .progress-bar-container {
        width: 100%;
        height: 8px;
        background-color: #e9ecef;
        border-radius: 4px;
        margin: 15px 0;
        overflow: hidden;
    }
    .progress-bar-fill {
        height: 100%;
        background-color: #007bff;
        border-radius: 4px;
        transition: width 0.8s ease;
    }
    /* Result card styling */
    .result-card {
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .result-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 15px rgba(0,0,0,0.15);
    }
    /* Prediction metrics styling */
    .metric-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 10px;
    }
    /* Enhanced animation for tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px; /* Increased from 8px to add more spacing between tabs */
        padding: 10px 0;
    }
    .stTabs [data-baseweb="tab"] {
        transition: background-color 0.3s ease, color 0.3s ease;
        border-radius: 4px 4px 0 0;
        padding: 10px 20px; /* Add padding for larger hit area */
    }
    /* History item styling */
    .history-item {
        border-left: 3px solid #6c757d;
        padding-left: 15px;
        margin-bottom: 10px;
        transition: border-left-color 0.3s ease;
    }
    .history-item:hover {
        border-left-color: #007bff;
    }
    /* Tooltip styling */
    .tooltip {
        position: relative;
        display: inline-block;
        border-bottom: 1px dotted #ccc;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
</style>

<!-- Custom HTML for animated elements -->
<div id="animations"></div>
<script>
    // Simple animation functions - these will be triggered by Streamlit components
    function fadeIn(elementId) {
        const element = document.getElementById(elementId);
        if(element) {
            element.style.opacity = 0;
            let opacity = 0;
            const timer = setInterval(() => {
                if(opacity >= 1) {
                    clearInterval(timer);
                }
                element.style.opacity = opacity;
                opacity += 0.05;
            }, 20);
        }
    }
    
    // Animation for progress bar
    document.addEventListener('DOMContentLoaded', () => {
        const progressBars = document.querySelectorAll('.progress-bar-fill');
        progressBars.forEach(bar => {
            const targetWidth = bar.getAttribute('data-width');
            bar.style.width = '0%';
            setTimeout(() => {
                bar.style.width = targetWidth + '%';
            }, 300);
        });
    });
</script>
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
        
        # Create prediction_history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                model_used VARCHAR(50),
                rf_prediction FLOAT,
                xgb_prediction FLOAT,
                lr_prediction FLOAT,
                ensemble_prediction FLOAT,
                risk_level VARCHAR(20),
                features JSON,
                FOREIGN KEY (user_id) REFERENCES users(id)
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
        return False, None
    cursor = conn.cursor(dictionary=True) # Fetch as dict
    try:
        # Check if the identifier matches either username or email
        query = "SELECT * FROM users WHERE (username=%s OR email=%s) AND password=%s"
        cursor.execute(query, (identifier, identifier, password)) # Use identifier for both username and email check
        user = cursor.fetchone()
        if user:
            return True, user # User found and password matches
        else:
            return False, None # User not found or password incorrect
    except Error as e:
        st.error(f"Login error: {e}")
        return False, None
    finally:
        cursor.close()
        conn.close()

# --- Save prediction to database ---
def save_prediction_to_db(user_id, prediction_data):
    conn = get_db_connection()
    if conn is None:
        return False
    cursor = conn.cursor()
    try:
        # Convert features to JSON string
        import json
        features_json = json.dumps(prediction_data['features'])
        # Insert prediction into database
        query = """
            INSERT INTO prediction_history 
            (user_id, model_used, rf_prediction, xgb_prediction, lr_prediction, 
             ensemble_prediction, risk_level, features)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            user_id,
            prediction_data['model_used'],
            prediction_data['rf_prediction'],
            prediction_data['xgb_prediction'],
            prediction_data['lr_prediction'],
            prediction_data['ensemble_prediction'],
            prediction_data['risk_level'],
            features_json
        ))
        conn.commit()
        return True
    except Error as e:
        st.error(f"Failed to save prediction: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# --- Load prediction history from database ---
def load_prediction_history(user_id):
    conn = get_db_connection()
    if conn is None:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        # Get all predictions for this user
        query = """
            SELECT * FROM prediction_history 
            WHERE user_id = %s
            ORDER BY timestamp DESC
        """
        cursor.execute(query, (user_id,))
        predictions = cursor.fetchall()
        # Process predictions
        history = []
        for pred in predictions:
            # Convert JSON string back to dictionary
            import json
            features = json.loads(pred['features'])
            # Format for consistency with session state format
            history.append({
                'timestamp': pred['timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                'model_used': pred['model_used'],
                'rf_prediction': pred['rf_prediction'],
                'xgb_prediction': pred['xgb_prediction'],
                'lr_prediction': pred['lr_prediction'],
                'ensemble_prediction': pred['ensemble_prediction'],
                'risk_level': pred['risk_level'],
                'features': features
            })
        return history
    except Error as e:
        st.error(f"Failed to load prediction history: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

# --- Main App Layout ---
def main():
    # Check if we just successfully registered and show toast
    if st.session_state.get('registration_success', False):
        st.toast("Account created successfully! Please log in.", icon="✅")
        del st.session_state['registration_success'] # Clear the flag immediately
    # Centered image and title
    st.image("https://cdn-icons-png.flaticon.com/512/1048/1048948.png", width=100) # Brain icon
    st.title("Student Depression Prediction")
    st.markdown("<p style='text-align: center; color: #6c757d;'>Login or Register to continue</p>", unsafe_allow_html=True)
    st.divider()
    # Determine the default index for the menu based on session state
    if st.session_state.get('force_login_tab', False): 
        st.session_state['menu_selection'] = 0
        del st.session_state['force_login_tab'] # Clear the flag
    default_menu_index = st.session_state.get('menu_selection', 0)
    selected = option_menu(
        menu_title=None,
        options=["Login", "Register"],
        icons=["box-arrow-in-right", "person-plus-fill"],
        orientation="horizontal",
        default_index=default_menu_index, 
        key='option_menu', 
        styles={
            "container": {"padding": "0!important", "background-color": "#ffffff"}, 
            "icon": {"color": "#007bff", "font-size": "18px"}, 
            "nav-link": {"font-size": "16px", "text-align": "center", "margin":"0px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#007bff", "color": "white", "font-weight": "bold"},
        }
    )
    selected_index = ["Login", "Register"].index(selected)
    st.session_state['menu_selection'] = selected_index
    st.write("")
    if selected == "Login":
        st.subheader("Login")
        with st.form("login_form"):
            identifier = st.text_input("Username or Email", key="login_identifier") 
            password = st.text_input("Password", type="password", key="login_pass")
            submitted = st.form_submit_button("Login")
            if submitted: 
                if not identifier or not password:
                    st.warning("Please enter both username/email and password.")
                else:
                    success, user = login_user(identifier, password) 
                    if success:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = user['username']
                        st.session_state['user_id'] = user['id'] 
                        st.session_state['prediction_history'] = load_prediction_history(user['id'])
                        st.success(f"Welcome back, {st.session_state['username']}!")
                        st.balloons()
                        st.snow() 
                        st.rerun()
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
                        st.session_state['registration_success'] = True
                        st.session_state['force_login_tab'] = True 
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(msg)

# --- Logged-in View (Enhanced UI/UX) ---
def show_main_app():
    username = st.session_state.get('username', 'User')
    with st.sidebar:
        st.markdown(f"""
        <div class="user-info-sidebar">
            <div class="user-icon">{username[0].upper()}</div>
            <div>Welcome, <strong>{username}</strong></div>
        </div>
        """, unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🔍 Predict Depression", "ℹ️ About", "📊 History"])
    with tab1:
        st.header("🧠 Student Depression Prediction")
        st.markdown("""
        <div class="progress-bar-container">
            <div class="progress-bar-fill" data-width="0" id="prediction-progress"></div>
        </div>
        <script>
            document.getElementById("prediction-progress").setAttribute("data-width", "30");
        </script>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="step-container">
            <span class="step-number">1</span>
            <h3 class="step-title">Enter Your Information</h3>
        </div>
        """, unsafe_allow_html=True)
        with st.container():
            with st.form("prediction_form"):
                col1, col2 = st.columns(2)
                with col1:
                    age = st.number_input("Age", min_value=15, max_value=100, value=20, 
                                         help="Your current age")
                    sleep_duration = st.selectbox(
                        "Sleep Duration", 
                        options=["Less than 5 hours", "5-6 hours", "7-8 hours", "More than 8 hours", "Others"],
                        index=1,
                        help="Your typical sleep duration per day"
                    )
                    dietary_habits = st.selectbox(
                        "Dietary Habits",
                        options=["Regular", "Irregular", "Vegetarian", "Non-vegetarian", "Vegan"],
                        index=0,
                        help="Your typical eating habits"
                    )
                    academic_pressure = st.slider("Academic Pressure (1-10)", 1, 10, 5, 
                                                help="Rate the academic pressure you feel, 1 being minimal and 10 being extreme")
                    academic_performance = st.slider("Academic Performance (0-10)", 0.0, 10.0, 7.0, 0.1,
                                                   help="Rate your academic performance, 0 being poor and 10 being excellent")
                with col2:
                    study_satisfaction = st.slider("Study Satisfaction (1-10)", 1, 10, 5,
                                                 help="How satisfied are you with your studies?")
                    work_study_hours = st.number_input("Work/Study Hours per day", min_value=1, max_value=24, value=8,
                                                     help="Total hours spent on work and study per day")
                    financial_stress = st.slider("Financial Stress (1-10)", 1, 10, 5,
                                                help="Rate your financial stress level")
                    suicidal_thoughts = st.radio("Have you ever had suicidal thoughts?", ["No", "Yes"],
                                               help="This information is confidential and used only for prediction")
                    illness_history = st.radio("Family history of mental illness?", ["No", "Yes"],
                                             help="Whether any immediate family members have history of mental illness")
                    degree = st.selectbox(
                        "Degree Program",
                        options=["Bachelor's", "Master's", "PhD", "Others"],
                        index=0,
                        help="Your current degree program"
                    )
                st.markdown("""
                <div class="step-container">
                    <span class="step-number">2</span>
                    <h3 class="step-title">Predict Your Result</h3>
                </div>
                """, unsafe_allow_html=True)
                model_choice = st.selectbox(
                    "Choose Prediction Model",
                    options=["Ensemble (All Models)", "Random Forest", "XGBoost", "Logistic Regression"],
                    index=0,
                    help="Choose which machine learning model to use for your depression prediction"
                )
                if model_choice == "Ensemble (All Models)":
                    st.markdown("""
                    <div class="metric-container">
                        <div class="metric-item primary-metric">Random Forest</div>
                        <div class="metric-item primary-metric">XGBoost</div>
                        <div class="metric-item primary-metric">Logistic Regression</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif model_choice == "Random Forest":
                    st.markdown("""
                    <div class="metric-container">
                        <div class="metric-item primary-metric">Random Forest</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif model_choice == "XGBoost":
                    st.markdown("""
                    <div class="metric-container">
                        <div class="metric-item primary-metric">XGBoost</div>
                    </div>
                    """, unsafe_allow_html=True)
                elif model_choice == "Logistic Regression":
                    st.markdown("""
                    <div class="metric-container">
                        <div class="metric-item primary-metric">Logistic Regression</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Add vertical space before the button
                st.write("")  # This adds some vertical space
                st.write("")  # Adding another line for more space
                
                # Adjust column proportions for better centering
                submit_col1, submit_col2, submit_col3 = st.columns([1.2,1,1.2])
                with submit_col2:
                    # Apply custom CSS for button positioning
                    st.markdown("""
                        <style>
                            div[data-testid="stFormSubmitButton"] > button {
                                margin-top: 15px;
                                display: block;
                                width: 100%;
                                text-align: center;
                            }
                        </style>
                    """, unsafe_allow_html=True)
                    submit_button = st.form_submit_button("Predict Depression Risk")
            
            if submit_button:
                try:
                    st.markdown("""
                    <script>
                        document.getElementById("prediction-progress").setAttribute("data-width", "70");
                    </script>
                    """, unsafe_allow_html=True)
                    import requests
                    import json
                    api_data = {
                        'age': age,
                        'dietary_habits': dietary_habits,
                        'degree': degree,
                        'academic_pressure': academic_pressure,
                        'cgpa': academic_performance, 
                        'study_satisfaction': study_satisfaction,
                        'work_study_hours': work_study_hours,
                        'sleep_duration': sleep_duration,
                        'financial_stress': financial_stress,
                        'suicidal_thoughts': suicidal_thoughts,
                        'illness_history': illness_history,
                        'model_choice': model_choice, 
                    }
                    api_url = "http://localhost:5000/predict"
                    with st.spinner("📊 Analyzing your data..."):
                        import time
                        time.sleep(0.5)
                        st.markdown("""
                        <script>
                            document.getElementById("prediction-progress").setAttribute("data-width", "90");
                        </script>
                        """, unsafe_allow_html=True)
                        response = requests.post(api_url, json=api_data, timeout=10)
                        st.markdown(""" 
                        <script>
                            document.getElementById("prediction-progress").setAttribute("data-width", "100");
                        </script>
                        """, unsafe_allow_html=True)
                        if response.status_code == 200:
                            result = response.json()
                            rf_pred = result.get('rf_prediction', 0)
                            xgb_pred = result.get('xgb_prediction', 0)
                            lr_pred = result.get('lr_prediction', 0)
                            ensemble_pred = result.get('ensemble_prediction', 0)
                            primary_pred = result.get('primary_prediction', ensemble_pred)
                            risk_level = result['risk_level']
                            message = result['message']
                            st.markdown('<div class="result-card">', unsafe_allow_html=True)
                            st.subheader("📊 Prediction Results")
                            risk_color = "#28a745" if risk_level == "Low" else "#ffc107" if risk_level == "Moderate" else "#dc3545"
                            st.markdown(f"""
                            <div style="text-align:center; margin:20px 0; padding:15px; 
                                        border-radius:10px; background-color:{risk_color}20; 
                                        border-left:4px solid {risk_color}">
                                <h2 style="color:{risk_color}; margin:0">{risk_level} Risk</h2>
                                <p style="font-size:1.1rem; margin:10px 0 0 0">{message}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            if model_choice == "Random Forest":
                                st.markdown(f"""
                                <div class="metric-container">
                                    <div class="metric-item primary-metric">
                                        <div style="font-weight:bold">Random Forest</div>
                                        <div style="font-size:1.5rem; margin:10px 0">{rf_pred:.2%}</div>
                                        <div style="font-size:0.8rem; color:#6c757d">Selected Model</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            elif model_choice == "XGBoost":
                                st.markdown(f"""
                                <div class="metric-container">
                                    <div class="metric-item primary-metric">
                                        <div style="font-weight:bold">XGBoost</div>
                                        <div style="font-size:1.5rem; margin:10px 0">{xgb_pred:.2%}</div>
                                        <div style="font-size:0.8rem; color:#6c757d">Selected Model</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            elif model_choice == "Logistic Regression":
                                st.markdown(f"""
                                <div class="metric-container">
                                    <div class="metric-item primary-metric">
                                        <div style="font-weight:bold">Logistic Regression</div>
                                        <div style="font-size:1.5rem; margin:10px 0">{lr_pred:.2%}</div>
                                        <div style="font-size:0.8rem; color:#6c757d">Selected Model</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            else:  # This is the "Ensemble (All Models)" case
                                st.markdown(f"""
                                <div class="metric-container">
                                    <div class="metric-item">
                                        <div>Random Forest</div>
                                        <div style="font-size:1.2rem; margin:10px 0">{rf_pred:.2%}</div>
                                    </div>
                                    <div class="metric-item">
                                        <div>XGBoost</div>
                                        <div style="font-size:1.2rem; margin:10px 0">{xgb_pred:.2%}</div>
                                    </div>
                                    <div class="metric-item">
                                        <div>Logistic Regression</div>
                                        <div style="font-size:1.2rem; margin:10px 0">{lr_pred:.2%}</div>
                                    </div>
                                    <div class="metric-item primary-metric">
                                        <div style="font-weight:bold">Ensemble</div>
                                        <div style="font-size:1.5rem; margin:10px 0">{ensemble_pred:.2%}</div>
                                        <div style="font-size:0.8rem; color:#6c757d">Combined Models</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                            st.subheader("💡 What This Means")
                            if risk_level == "Low":
                                st.success("Your responses indicate a low risk of depression. Continue maintaining healthy habits and self-care routines.")
                                st.markdown("""
                                <ul>
                                    <li>Continue with your current positive habits</li>
                                    <li>Practice regular self-care and stress management</li>
                                    <li>Maintain social connections and support systems</li>
                                </ul>
                                """, unsafe_allow_html=True)
                            elif risk_level == "Moderate":
                                st.warning("Your responses suggest a moderate risk of depression. Consider reaching out to a mental health professional.")
                                st.markdown("""
                                <ul>
                                    <li>Consider speaking with a counselor or therapist</li>
                                    <li>Focus on sleep quality, physical activity, and stress reduction</li>
                                    <li>Build your support network and practice mindfulness techniques</li>
                                </ul>
                                """, unsafe_allow_html=True)
                            else:
                                st.error("Your responses indicate a high risk of depression. We strongly recommend consulting a mental health professional.")
                                st.markdown("""
                                <ul>
                                    <li><strong>Important:</strong> Consult with a mental health professional as soon as possible</li>
                                    <li>Reach out to trusted friends or family members for support</li>
                                    <li>National Suicide Prevention Lifeline: 988 (call or text)</li>
                                </ul>
                                """, unsafe_allow_html=True)
                                st.info("If you're experiencing a mental health emergency, please contact a mental health professional or crisis helpline immediately.")
                            st.markdown('</div>', unsafe_allow_html=True)
                            prediction_data = {
                                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'model_used': model_choice,
                                'ensemble_prediction': ensemble_pred,
                                'rf_prediction': rf_pred,
                                'xgb_prediction': xgb_pred,
                                'lr_prediction': lr_pred,
                                'primary_prediction': primary_pred,
                                'risk_level': risk_level,
                                'features': api_data,
                            }
                            if 'prediction_history' not in st.session_state:
                                st.session_state.prediction_history = []
                            st.session_state.prediction_history.append(prediction_data)
                            with st.spinner("Saving your results..."):
                                if save_prediction_to_db(st.session_state['user_id'], prediction_data):
                                    st.success("✅ Prediction saved to your history!")
                                else:
                                    st.warning("⚠️ Could not save prediction to history. Your results may not appear after logging out.")
                        else:
                            st.error(f"API Error: {response.status_code} - {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("Failed to connect to the API server. Please ensure the Flask API is running at http://localhost:5000")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    with tab2:
        st.header("About Student Depression Prediction")
        st.markdown("""     
        <div class="form-section" style="border-left-color: #17a2b8;">
            <h3>📱 What This App Does</h3>
            <p style="color: #e9ecef;">This application uses machine learning models trained on a dataset of student characteristics to predict the likelihood of depression.</p>
            <p style="color: #e9ecef;">By analyzing various factors related to your academic life, personal habits, and mental health history, our models can identify patterns associated with depression risk.</p>
        </div>
        
        <div class="form-section" style="border-left-color: #28a745;">
            <h3>🤖 The Models</h3>
            <p style="color: #e9ecef;">We've trained three different machine learning models:</p>
            <div class="metric-container">
                <div class="metric-item">
                    <strong style="color: #ffffff;">Random Forest</strong>
                    <p style="color: #e9ecef;">A powerful ensemble learning method that builds multiple decision trees.</p>
                </div>
                <div class="metric-item">
                    <strong style="color: #ffffff;">XGBoost</strong>
                    <p style="color: #e9ecef;">An optimized gradient boosting library designed for efficiency and performance.</p>
                </div>
                <div class="metric-item">
                    <strong style="color: #ffffff;">Logistic Regression</strong>
                    <p style="color: #e9ecef;">A statistical model that uses a logistic function to model a binary dependent variable.</p>
                </div>
            </div>
        </div>
        
        <div class="form-section" style="border-left-color: #ffc107;">
            <h3>📊 Important Features</h3>
            <p style="color: #e9ecef;">Our models found these factors most predictive of student depression:</p>
            <ul style="color: #e9ecef;">
                <li><strong style="color: #ffffff;">Academic pressure and stress</strong></li>
                <li><strong style="color: #ffffff;">Sleep quality and duration</strong></li>
                <li><strong style="color: #ffffff;">History of suicidal thoughts</strong></li>
                <li><strong style="color: #ffffff;">Family history of mental illness</strong></li>
                <li><strong style="color: #ffffff;">Academic satisfaction and performance</strong></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        st.info("⚠️ This tool is for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.")
        st.warning("If you're experiencing thoughts of harming yourself or others, please contact a mental health professional or crisis helpline immediately.")
    with tab3:
        st.header("Your Prediction History")
        if 'prediction_history' in st.session_state and st.session_state.prediction_history:
            sorted_history = sorted(st.session_state.prediction_history, 
                                   key=lambda x: datetime.datetime.strptime(x['timestamp'], "%Y-%m-%d %H:%M:%S"),
                                   reverse=True)
            for i, pred in enumerate(sorted_history):
                timestamp = datetime.datetime.strptime(pred['timestamp'], "%Y-%m-%d %H:%M:%S")
                formatted_date = timestamp.strftime("%b %d, %Y")
                formatted_time = timestamp.strftime("%I:%M %p")
                risk_level = pred.get('risk_level', 'Unknown')
                if risk_level == "Low":
                    risk_color = "#28a745"
                elif risk_level == "Moderate":
                    risk_color = "#ffc107"
                else:
                    risk_color = "#dc3545"
                with st.expander(f"📅 {formatted_date} at {formatted_time} - {risk_level} Risk"):
                    st.markdown(f"""
                    <div style="border-left: 3px solid {risk_color}; padding-left: 10px; margin-bottom: 15px;">
                        <h4 style="margin:0">Depression Risk: <span style="color:{risk_color}">{pred['ensemble_prediction']:.2%}</span></h4>
                        <p>Model Used: <strong>{pred['model_used']}</strong></p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("""
                    <div class="metric-container">
                        <div class="metric-item">
                            <div>Random Forest</div>
                            <div style="font-size:1.2rem; margin:5px 0">{:.2%}</div>
                        </div>
                        <div class="metric-item">
                            <div>XGBoost</div>
                            <div style="font-size:1.2rem; margin:5px 0">{:.2%}</div>
                        </div>
                        <div class="metric-item">
                            <div>Logistic Regression</div>
                            <div style="font-size:1.2rem; margin:5px 0">{:.2%}</div>
                        </div>
                    </div>
                    """.format(pred['rf_prediction'], pred['xgb_prediction'], pred['lr_prediction']), 
                    unsafe_allow_html=True)
                    st.subheader("Your Responses:")
                    features = {k: v for k, v in pred['features'].items() if k not in ['model_choice']}
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Demographics:**")
                        st.write(f"• Age: {features.get('age')}")
                        st.write(f"• Degree: {features.get('degree')}")
                        st.write("**Lifestyle:**")
                        st.write(f"• Sleep: {features.get('sleep_duration')}")
                        st.write(f"• Diet: {features.get('dietary_habits')}")
                        st.write(f"• Study/Work Hours: {features.get('work_study_hours')}")
                    with col2:
                        st.write("**Academic Factors:**")
                        st.write(f"• Academic Pressure: {features.get('academic_pressure')}/10")
                        st.write(f"• Academic Performance: {features.get('cgpa')}/10")
                        st.write(f"• Study Satisfaction: {features.get('study_satisfaction')}/10")
                        st.write("**Mental Health:**")
                        st.write(f"• Financial Stress: {features.get('financial_stress')}/10")
                        st.write(f"• Suicidal Thoughts: {features.get('suicidal_thoughts')}")
                        st.write(f"• Family History: {features.get('illness_history')}")
        else:
            st.info("📝 No prediction history yet. Make a prediction to see it here.")
            st.markdown("""
            <div style="text-align:center; margin-top:30px;">
                <img src="https://cdn-icons-png.flaticon.com/512/6119/6119820.png" width="100">
                <p style="margin-top:15px;">Make your first prediction to start tracking your mental health</p>
            </div>
            """, unsafe_allow_html=True)
    with st.sidebar:
        if st.button("Logout", key="logout_btn"):
            keys_to_delete = list(st.session_state.keys())
            for key in keys_to_delete:
                del st.session_state[key]
            st.rerun()

# --- Main Execution Logic ---
if __name__ == "__main__":
    if st.session_state.get('logged_in', False): 
        show_main_app() 
    else:
        main()
