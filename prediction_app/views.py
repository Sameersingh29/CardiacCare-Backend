from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import CADPredictionForm
from .forms import CADPatient
from .ml_model_2 import CAD_MODEL_2, FEATURE_NAMES_2
from .ml_model import CAD_MODEL, FEATURE_NAMES
import numpy as np
import pandas as pd
import json

@csrf_exempt
def predict(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            
            # Convert JSON data to form data
            form_data = {
                'age': float(data.get('age')),
                'sex': int(data.get('sex')),
                'chest_pain': int(data.get('chest_pain')),
                'resting_bp': float(data.get('resting_bp')),
                'cholesterol': float(data.get('cholesterol')),
                'fasting_bs': int(data.get('fasting_bs')),
                'resting_ecg': int(data.get('resting_ecg')),
                'max_heart_rate': float(data.get('max_heart_rate')),
                'exercise_angina': int(data.get('exercise_angina')),
                'oldpeak': float(data.get('oldpeak')),
                'slope': int(data.get('slope')),
                'major_vessels': int(data.get('major_vessels'))
            }
            
            # Validate the data using the form
            form = CADPredictionForm(form_data)
            if not form.is_valid():
                # Return form validation errors
                return JsonResponse({
                    'error': 'Validation failed',
                    'details': form.errors
                }, status=400)
            
            # Convert form data to numpy array in correct order
            input_data = np.array([
                form.cleaned_data['age'],
                form.cleaned_data['sex'],
                form.cleaned_data['chest_pain'],
                form.cleaned_data['resting_bp'],
                form.cleaned_data['cholesterol'],
                form.cleaned_data['fasting_bs'],
                form.cleaned_data['resting_ecg'],
                form.cleaned_data['max_heart_rate'],
                form.cleaned_data['exercise_angina'],
                form.cleaned_data['oldpeak'],
                form.cleaned_data['slope'],
                form.cleaned_data['major_vessels']
            ]).reshape(1, -1)

            # Predict
            prediction = CAD_MODEL.predict(input_data)[0]
            
            # Probability prediction (if your model supports it)
            try:
                prediction_proba = CAD_MODEL.predict_proba(input_data)[0]
                positive_prob = prediction_proba[1] * 100  # Assuming binary classification
            except AttributeError:
                positive_prob = None
            
            # Detailed interpretation
            return JsonResponse({
                'prediction': int(prediction),
                'risk_level': "High Risk" if prediction == 1 else "Low Risk",
                'risk_probability': round(positive_prob, 2) if positive_prob is not None else None,
                'input_data': form_data
            })
        
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON'
            }, status=400)
        
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    # If not a POST request
    return JsonResponse({
        'error': 'Only POST method is allowed'
    }, status=405)

@csrf_exempt
def predict_cardiovascular(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            print("Received data:", data)
           
            # Convert JSON data to form data
            form_data = {
                'age': int(data.get('age', 0)),
                'gender': int(data.get('gender', 1)),
                'height': float(data.get('height', 0.0)),
                'weight': float(data.get('weight', 0.0)),
                'ap_hi': float(data.get('ap_hi', 0.0)),
                'ap_lo': float(data.get('ap_lo', 0.0)),
                'cholesterol': int(data.get('cholesterol', 1)),
                'gluc': int(data.get('gluc', 1)),
                'smoke': int(data.get('smoke', 0)),
                'alco': int(data.get('alco', 0)),
                'active': int(data.get('active', 0)),
            }
            print("Processed form_data:", form_data)
           
            # Validate the data using the form
            form = CADPatient(form_data)
            if not form.is_valid():
                # Return form validation errors
                return JsonResponse({
                    'error': 'Validation failed',
                    'details': form.errors
                }, status=400)
           
            # Convert form data to DataFrame in correct order
            input_data = pd.DataFrame([[
                form.cleaned_data['age'],
                form.cleaned_data['gender'],
                form.cleaned_data['height'],
                form.cleaned_data['weight'],
                form.cleaned_data['ap_hi'],
                form.cleaned_data['ap_lo'],
                form.cleaned_data['cholesterol'],
                form.cleaned_data['gluc'],
                form.cleaned_data['smoke'],
                form.cleaned_data['alco'],
                form.cleaned_data['active']
            ]], columns=FEATURE_NAMES_2)

            # Ensure all columns are numerical
            input_data = input_data.astype(float)
            print("Input DataFrame:", input_data)
            print("DataFrame dtypes:", input_data.dtypes)
            
            # Predict
            prediction = CAD_MODEL_2.predict(input_data)[0]
           
            # Probability estimation
            prediction_proba = CAD_MODEL_2.predict_proba(input_data)[0]
            positive_prob = prediction_proba[1] * 100
           
            # Detailed interpretation
            return JsonResponse({
                'prediction': int(prediction),
                'risk_level': "High Cardiovascular Risk" if prediction == 1 else "Low Cardiovascular Risk",
                'risk_probability': round(positive_prob, 2),
                'input_data': form_data
            })
       
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON'
            }, status=400)
       
        except Exception as e:
            return JsonResponse({
                'error': str(e)
            }, status=500)
   
    # If not a POST request
    return JsonResponse({
        'error': 'Only POST method is allowed'
    }, status=405)