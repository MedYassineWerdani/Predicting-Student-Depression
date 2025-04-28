from flask import Flask, request, jsonify
import joblib
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

# Create Flask app
app = Flask(__name__)

# Load models
base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
models_path = os.path.join(base_path, 'models')

# Load all three models
rf_model = joblib.load(os.path.join(models_path, 'random_forest.pkl'))
xgb_model = joblib.load(os.path.join(models_path, 'xgboost.pkl'))
lr_model = joblib.load(os.path.join(models_path, 'logistic_regression.pkl'))

# Load the saved scaler for Logistic Regression
scaler = joblib.load(os.path.join(models_path, 'standard_scaler.pkl'))

# Get the expected feature names
try:
    # For Random Forest, feature names should be available
    feature_names = rf_model.feature_names_in_
except AttributeError:
    # Fallback features based on the notebook
    feature_names = ['age', 'dietary_habits', 'degree', 'academic_pressure', 
                    'cgpa', 'study_satisfaction', 'work/study_hours', 
                    'sleep_duration', 'financial_stress', 'suicidal_thoughts', 
                    'illness_history', 'academic_stress_combo', 'burnout_index', 
                    'wellness_score']

# Preprocessing functions for each model
def preprocess_data_base(data_dict):
    """
    Base preprocessing function that handles common preprocessing steps.
    Returns a DataFrame with the proper structure based on the training data.
    """
    # Create feature map dictionaries
    sleep_map = {
        "Less than 5 hours": 0,
        "5-6 hours": 1,
        "7-8 hours": 2,
        "More than 8 hours": 3,
        "Others": 4
    }
    
    binary_map = {'Yes': 1, 'No': 0}
    
    dietary_map = {
        "Regular": 3,
        "Irregular": 1,
        "Vegetarian": 4,
        "Non-vegetarian": 2,
        "Vegan": 0
    }
    
    degree_map = {
        "Bachelor's": 0,
        "Master's": 1,
        "PhD": 2,
        "Others": 3
    }

    # Create feature dictionary with proper mapping and types
    features = {
        'age': data_dict.get('age'),
        'dietary_habits': dietary_map.get(data_dict.get('dietary_habits', ''), 0),
        'degree': degree_map.get(data_dict.get('degree', ''), 0),
        'academic_pressure': data_dict.get('academic_pressure'),
        'cgpa': data_dict.get('cgpa'),
        'study_satisfaction': data_dict.get('study_satisfaction'),
        'work/study_hours': data_dict.get('work_study_hours'),
        'sleep_duration': sleep_map.get(data_dict.get('sleep_duration', ''), 1),
        'financial_stress': data_dict.get('financial_stress'),
        'suicidal_thoughts': binary_map.get(data_dict.get('suicidal_thoughts', ''), 0),
        'illness_history': binary_map.get(data_dict.get('illness_history', ''), 0)
    }
    
    # Create derived features exactly as done in the notebook
    features['academic_stress_combo'] = features['academic_pressure'] * features['financial_stress']
    features['burnout_index'] = features['academic_pressure'] * features['work/study_hours']
    features['wellness_score'] = features['study_satisfaction'] + features['sleep_duration'] + features['dietary_habits']
    
    # Convert to DataFrame
    input_df = pd.DataFrame([features])
    
    # Ensure the column order matches the training order
    if isinstance(feature_names, np.ndarray) or isinstance(feature_names, list):
        # Ensure all required features are present
        for feat in feature_names:
            if feat not in input_df.columns:
                input_df[feat] = 0  # Default value for missing features
        # Reorder columns to match training order
        input_df = input_df[feature_names]
    
    return input_df

def preprocess_for_random_forest(data_dict):
    """
    Preprocessing pipeline for Random Forest model.
    Random Forest was trained on encoded but non-standardized features.
    """
    return preprocess_data_base(data_dict)

def preprocess_for_xgboost(data_dict):
    """
    Preprocessing pipeline for XGBoost model.
    XGBoost was trained on encoded but non-standardized features.
    """
    return preprocess_data_base(data_dict)

def preprocess_for_logistic_regression(data_dict):
    """
    Preprocessing pipeline for Logistic Regression model.
    Logistic Regression was trained on standardized features.
    """
    # First get the base preprocessing
    input_df = preprocess_data_base(data_dict)
    
    # Apply the saved scaler that was used during training
    input_scaled = scaler.transform(input_df)
    
    return input_scaled

@app.route('/health', methods=['GET'])
def health_check():
    # Also return the feature names for debugging
    return jsonify({'status': 'ok', 'message': 'API is running', 'features': feature_names.tolist() if hasattr(feature_names, 'tolist') else feature_names, 'test': 'auto-redeploy'})

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse JSON data from request
        data = request.get_json()
        
        # Get the selected model (defaults to ensemble if not specified)
        model_choice = data.get('model_choice', 'Ensemble (All Models)')
        
        app.logger.info(f"Selected model: {model_choice}")
        
        # Process data based on the selected model
        if model_choice == "Random Forest":
            # Process data for Random Forest
            rf_input = preprocess_for_random_forest(data)
            rf_pred = rf_model.predict_proba(rf_input)[0][1]
            
            # For completeness, calculate predictions from other models too
            xgb_input = preprocess_for_xgboost(data)
            xgb_pred = xgb_model.predict_proba(xgb_input)[0][1]
            
            lr_input = preprocess_for_logistic_regression(data)
            lr_pred = lr_model.predict_proba(lr_input)[0][1]
            
            # Primary prediction is from Random Forest
            primary_pred = rf_pred
            
        elif model_choice == "XGBoost":
            # Process data for XGBoost
            xgb_input = preprocess_for_xgboost(data)
            xgb_pred = xgb_model.predict_proba(xgb_input)[0][1]
            
            # For completeness, calculate predictions from other models too
            rf_input = preprocess_for_random_forest(data)
            rf_pred = rf_model.predict_proba(rf_input)[0][1]
            
            lr_input = preprocess_for_logistic_regression(data)
            lr_pred = lr_model.predict_proba(lr_input)[0][1]
            
            # Primary prediction is from XGBoost
            primary_pred = xgb_pred
            
        elif model_choice == "Logistic Regression":
            # Process data for Logistic Regression (with standardization)
            lr_input = preprocess_for_logistic_regression(data)
            lr_pred = lr_model.predict_proba(lr_input)[0][1]
            
            # For completeness, calculate predictions from other models too
            rf_input = preprocess_for_random_forest(data)
            rf_pred = rf_model.predict_proba(rf_input)[0][1]
            
            xgb_input = preprocess_for_xgboost(data)
            xgb_pred = xgb_model.predict_proba(xgb_input)[0][1]
            
            # Primary prediction is from Logistic Regression
            primary_pred = lr_pred
            
        else:  # Ensemble (All Models)
            # Process data for each model with its specific pipeline
            rf_input = preprocess_for_random_forest(data)
            rf_pred = rf_model.predict_proba(rf_input)[0][1]
            
            xgb_input = preprocess_for_xgboost(data)
            xgb_pred = xgb_model.predict_proba(xgb_input)[0][1]
            
            lr_input = preprocess_for_logistic_regression(data)
            lr_pred = lr_model.predict_proba(lr_input)[0][1]
            
            # Calculate ensemble prediction
            primary_pred = (rf_pred + xgb_pred + lr_pred) / 3
        
        # Calculate ensemble prediction (always calculate this for consistency)
        ensemble_pred = (rf_pred + xgb_pred + lr_pred) / 3
        
        # Determine risk level based on primary prediction
        if primary_pred < 0.3:
            risk_level = "Low"
            message = "Continue maintaining healthy habits!"
        elif primary_pred < 0.7:
            risk_level = "Moderate"
            message = "Consider talking to someone you trust about your feelings."
        else:
            risk_level = "High"
            message = "We recommend seeking professional help."

        # Return prediction results
        return jsonify({
            'rf_prediction': float(rf_pred),
            'xgb_prediction': float(xgb_pred),
            'lr_prediction': float(lr_pred),
            'ensemble_prediction': float(ensemble_pred),
            'primary_prediction': float(primary_pred),
            'selected_model': model_choice,
            'risk_level': risk_level,
            'message': message
        })
    
    except Exception as e:
        app.logger.error(f"Prediction error: {str(e)}")
        import traceback
        app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)