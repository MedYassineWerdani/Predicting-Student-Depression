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
        return False, None
    cursor = conn.cursor(dictionary=True) # Fetch as dict
    try:
        # Check if the identifier matches either username or email
        query = "SELECT * FROM users WHERE (username=%s OR email=%s) AND password=%s"
        cursor.execute(query, (identifier, identifier, password)) # Use identifier for both username and email check
        user = cursor.fetchone()
        if user:
            # Simple plain text comparison (as used in registration)
            # NOTE: In a real app, verify hashed password here
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
                else:
                    success, user = login_user(identifier, password) # Pass identifier to login_user
                    if success:
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = user['username']
                        st.session_state['user_id'] = user['id'] # Store user ID for database operations
                        
                        # Load prediction history from database
                        st.session_state['prediction_history'] = load_prediction_history(user['id'])
                        
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
    
    # Use tabs for different sections of the app
    tab1, tab2, tab3 = st.tabs(["Predict Depression", "About", "History"])
    
    with tab1:
        st.header("🧠 Student Depression Prediction")
        st.write("Fill in the form below to predict your risk of depression.")
        
        # Make model selection more obvious above the form
        st.subheader("Step 1: Select Prediction Model")
        model_choice = st.selectbox(
            "Which model would you like to use for prediction?",
            options=["Ensemble (All Models)", "Random Forest", "XGBoost", "Logistic Regression"],
            index=0,
            help="Choose which machine learning model to use for your depression prediction"
        )
        
        st.write(f"You selected: **{model_choice}**")
        st.divider()
        
        # Create the prediction form
        st.subheader("Step 2: Enter Your Information")
        with st.form("prediction_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                age = st.number_input("Age", min_value=15, max_value=100, value=20)
                sleep_duration = st.selectbox(
                    "Sleep Duration", 
                    options=["Less than 5 hours", "5-6 hours", "7-8 hours", "More than 8 hours", "Others"],
                    index=1
                )
                dietary_habits = st.selectbox(
                    "Dietary Habits",
                    options=["Regular", "Irregular", "Vegetarian", "Non-vegetarian", "Vegan"],
                    index=0
                )
                academic_pressure = st.slider("Academic Pressure (1-10)", 1, 10, 5)
                cgpa = st.slider("CGPA (0-10)", 0.0, 10.0, 7.0, 0.1)
                
            with col2:
                study_satisfaction = st.slider("Study Satisfaction (1-10)", 1, 10, 5)
                work_study_hours = st.number_input("Work/Study Hours per day", min_value=1, max_value=24, value=8)
                financial_stress = st.slider("Financial Stress (1-10)", 1, 10, 5)
                suicidal_thoughts = st.radio("Have you ever had suicidal thoughts?", ["No", "Yes"])
                illness_history = st.radio("Family history of mental illness?", ["No", "Yes"])
                degree = st.selectbox(
                    "Degree Program",
                    options=["Bachelor's", "Master's", "PhD", "Others"],
                    index=0
                )
            
            # Remind user of their model choice
            st.info(f"You will be using the **{model_choice}** for prediction.")
            submit_button = st.form_submit_button("Predict")
            
            if submit_button:
                try:
                    # Import necessary libraries for API requests
                    import requests
                    import json
                    
                    # Prepare data for API request
                    api_data = {
                        'age': age,
                        'dietary_habits': dietary_habits,
                        'degree': degree,
                        'academic_pressure': academic_pressure,
                        'cgpa': cgpa,
                        'study_satisfaction': study_satisfaction,
                        'work_study_hours': work_study_hours,
                        'sleep_duration': sleep_duration,
                        'financial_stress': financial_stress,
                        'suicidal_thoughts': suicidal_thoughts,
                        'illness_history': illness_history,
                        'model_choice': model_choice  # Add the model choice to API data
                    }
                    
                    # API endpoint (using localhost, adjust as needed for production)
                    api_url = "http://localhost:5000/predict"
                    
                    # Show loading spinner while waiting for API response
                    with st.spinner("Getting prediction results..."):
                        # Send POST request to API
                        response = requests.post(api_url, json=api_data, timeout=10)
                        
                        # Verify response
                        if response.status_code == 200:
                            result = response.json()
                            
                            # Extract prediction values
                            rf_pred = result.get('rf_prediction', 0)
                            xgb_pred = result.get('xgb_prediction', 0)
                            lr_pred = result.get('lr_prediction', 0)
                            ensemble_pred = result.get('ensemble_prediction', 0)
                            primary_pred = result.get('primary_prediction', ensemble_pred)  # Get the primary prediction
                            risk_level = result['risk_level']
                            message = result['message']
                            
                            # Display results
                            st.subheader("Prediction Results")
                            
                            # If selected a specific model, highlight that one
                            if model_choice == "Random Forest":
                                st.metric(label="📊 Random Forest (Selected)", value=f"{rf_pred:.2%}")
                                st.divider()
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric(label="XGBoost", value=f"{xgb_pred:.2%}")
                                with col2:
                                    st.metric(label="Logistic Regression", value=f"{lr_pred:.2%}")
                            elif model_choice == "XGBoost":
                                st.metric(label="📊 XGBoost (Selected)", value=f"{xgb_pred:.2%}")
                                st.divider()
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric(label="Random Forest", value=f"{rf_pred:.2%}")
                                with col2:
                                    st.metric(label="Logistic Regression", value=f"{lr_pred:.2%}")
                            elif model_choice == "Logistic Regression":
                                st.metric(label="📊 Logistic Regression (Selected)", value=f"{lr_pred:.2%}")
                                st.divider()
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.metric(label="Random Forest", value=f"{rf_pred:.2%}")
                                with col2:
                                    st.metric(label="XGBoost", value=f"{xgb_pred:.2%}")
                            else:
                                # Show all models with equal weight (Ensemble option)
                                col1, col2, col3, col4 = st.columns(4)
                                with col1:
                                    st.metric(label="Random Forest", value=f"{rf_pred:.2%}")
                                with col2:
                                    st.metric(label="XGBoost", value=f"{xgb_pred:.2%}")
                                with col3:
                                    st.metric(label="Logistic Regression", value=f"{lr_pred:.2%}")
                                with col4:
                                    st.metric(label="📊 Ensemble", value=f"{ensemble_pred:.2%}")
                            
                            # Add interpretation
                            st.subheader("Interpretation")
                            
                            if risk_level == "Low":
                                st.success(f"Low risk of depression detected. {message}")
                            elif risk_level == "Moderate":
                                st.warning(f"Moderate risk of depression detected. {message}")
                            else:
                                st.error(f"High risk of depression detected. {message}")
                                st.info("If you're experiencing a mental health emergency, please contact a mental health professional or crisis helpline immediately.")
                            
                            # Save result to history
                            prediction_data = {
                                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'model_used': model_choice,
                                'ensemble_prediction': ensemble_pred,
                                'rf_prediction': rf_pred,
                                'xgb_prediction': xgb_pred,
                                'lr_prediction': lr_pred,
                                'primary_prediction': primary_pred,
                                'risk_level': risk_level,
                                'features': api_data
                            }
                            
                            if 'prediction_history' not in st.session_state:
                                st.session_state.prediction_history = []
                            
                            # Add to session state
                            st.session_state.prediction_history.append(prediction_data)
                            
                            # Save prediction to database
                            if save_prediction_to_db(st.session_state['user_id'], prediction_data):
                                st.success("Prediction saved to your history!")
                            else:
                                st.warning("Could not save prediction to history. Your results may not appear after logging out.")
                        else:
                            st.error(f"API Error: {response.status_code} - {response.text}")
                            
                except requests.exceptions.ConnectionError:
                    st.error("Failed to connect to the API server. Please ensure the Flask API is running at http://localhost:5000")
                except Exception as e:
                    st.error(f"An error occurred: {e}")
    
    with tab2:
        st.header("About Student Depression Prediction")
        st.write("""
        ### What This App Does
        This app uses machine learning models trained on a dataset of student characteristics to predict the likelihood of depression.
        
        ### The Models
        We've trained three different models:
        - **Random Forest**: A powerful ensemble learning method that builds multiple decision trees.
        - **XGBoost**: An optimized gradient boosting library designed for efficiency and performance.
        - **Logistic Regression**: A statistical model that uses a logistic function to model a binary dependent variable.
        
        ### Important Features
        Our models found these factors most predictive of student depression:
        - Academic pressure and stress
        - Sleep quality and duration
        - History of suicidal thoughts
        - Family history of mental illness
        - Academic satisfaction and performance
        
        ### Disclaimer
        This tool is for educational purposes only and is not a substitute for professional medical advice, diagnosis, or treatment.
        """)
        
        st.info("If you're experiencing thoughts of harming yourself or others, please contact a mental health professional or crisis helpline immediately.")
    
    with tab3:
        st.header("Your Prediction History")
        if 'prediction_history' in st.session_state and st.session_state.prediction_history:
            for i, pred in enumerate(st.session_state.prediction_history):
                with st.expander(f"Prediction {i+1} - {pred['timestamp']}"):
                    st.write(f"**Depression Risk:** {pred['ensemble_prediction']:.2%}")
                    st.write(f"Risk Level: {pred.get('risk_level', 'Unknown')}")
                    st.write(f"Random Forest: {pred['rf_prediction']:.2%}, XGBoost: {pred['xgb_prediction']:.2%}, Logistic Regression: {pred['lr_prediction']:.2%}")
                    
                    # Show feature values
                    st.write("**Input Features:**")
                    # Filter out derived features
                    base_features = {k: v for k, v in pred['features'].items()}
                    st.json(base_features)
        else:
            st.write("No prediction history yet. Make a prediction to see it here.")
            
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
