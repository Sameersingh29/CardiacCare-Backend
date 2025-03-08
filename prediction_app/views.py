from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import CADPredictionForm, CADPatient
from .recommendations import generate_recommendations
from .ml_model_2 import CAD_MODEL_2, FEATURE_NAMES_2
from .ml_model import CAD_MODEL, FEATURE_NAMES
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.db import models
from django.contrib.auth import authenticate
import numpy as np
import pandas as pd
import json
from rest_framework.permissions import IsAuthenticated
from .models import PatientPrediction,ClinicianCardiovascularPrediction
from django.contrib.auth.models import AnonymousUser
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.views import APIView
from .models import PatientPrediction
from rest_framework.authentication import TokenAuthentication

# User Profile Model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=[('patient', 'Patient'), ('clinician', 'Clinician')])

    class Meta:
        db_table = 'api'


# Signup View
class SignupView(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            email = request.data.get('email')
            user_type = request.data.get('userType')

            if user_type not in ['patient', 'clinician']:
                return Response({'error': 'Invalid user type'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(username=username).exists():
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email).exists():
                return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.create_user(username=username, password=password, email=email)
            UserProfile.objects.create(user=user, user_type=user_type)

            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_type': user_type
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Login View
class LoginView(APIView):
    def post(self, request):
        try:
            username = request.data.get('username')
            password = request.data.get('password')

            user = authenticate(username=username, password=password)
            if user:
                try:
                    profile = UserProfile.objects.get(user=user)
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({
                        'token': token.key,
                        'user_type': profile.user_type
                    }, status=status.HTTP_200_OK)
                except UserProfile.DoesNotExist:
                    return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def predict(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            
            # Check if user is authenticated and is a clinician
            # if not request.user.is_authenticated:
            #     return JsonResponse({
            #         'error': 'Authentication required'
            #     }, status=401)
            
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                if user_profile.user_type != 'clinician':
                    return JsonResponse({
                        'error': 'Only clinicians can make predictions'
                    }, status=403)
            except UserProfile.DoesNotExist:
                return JsonResponse({
                    'error': 'User profile not found'
                }, status=403)
            
            # Convert JSON data to form data
            form_data = {
                'age': float(data.get('age', 0) or 0),
                'resting_bp': float(data.get('resting_bp', 0) or 0),
                'cholesterol': float(data.get('cholesterol', 0) or 0),
                'max_heart_rate': float(data.get('max_heart_rate', 0) or 0),
                'oldpeak': float(data.get('oldpeak', 0) or 0),


                # 'age': float(data.get('age')),
                'sex': int(data.get('sex')),
                'chest_pain': int(data.get('chest_pain')),
                # 'resting_bp': float(data.get('resting_bp')),
                # 'cholesterol': float(data.get('cholesterol')),
                'fasting_bs': int(data.get('fasting_bs')),
                'resting_ecg': int(data.get('resting_ecg')),
                # 'max_heart_rate': float(data.get('max_heart_rate')),
                'exercise_angina': int(data.get('exercise_angina')),
                # 'oldpeak': float(data.get('oldpeak')),
                'slope': int(data.get('slope')),
                'major_vessels': int(data.get('major_vessels'))
            }
            
            # Optional patient details for clinician
            patient_name = data.get('patient_name')
            patient_email = data.get('patient_email')
            
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
            
            # Generate personalized recommendations
            recommendations = generate_recommendations(form_data, is_patient_form=False)
            
            # Prepare risk factors
            risk_factors = {
                'high_bp': form_data['resting_bp'] >= 140,
                'high_cholesterol': form_data['cholesterol'] >= 200,
                'abnormal_ecg': form_data['resting_ecg'] != 0,
                'exercise_angina': form_data['exercise_angina'] == 1,
                'significant_vessels': form_data['major_vessels'] > 0
            }
            
            # Save prediction for clinician
            try:
                clinician_prediction = ClinicianCardiovascularPrediction.objects.create(
                    user=request.user,
                    patient_name=patient_name,
                    patient_email=patient_email,
                    age=form.cleaned_data['age'],
                    sex=form.cleaned_data['sex'],
                    chest_pain=form.cleaned_data['chest_pain'],
                    resting_bp=form.cleaned_data['resting_bp'],
                    cholesterol=form.cleaned_data['cholesterol'],
                    fasting_bs=form.cleaned_data['fasting_bs'],
                    resting_ecg=form.cleaned_data['resting_ecg'],
                    max_heart_rate=form.cleaned_data['max_heart_rate'],
                    exercise_angina=form.cleaned_data['exercise_angina'],
                    oldpeak=form.cleaned_data['oldpeak'],
                    slope=form.cleaned_data['slope'],
                    major_vessels=form.cleaned_data['major_vessels'],
                    prediction=int(prediction),
                    risk_level="High Risk" if prediction == 1 else "Low Risk",
                    risk_probability=positive_prob,
                    risk_factors=risk_factors
                )
            except Exception as save_error:
                print(f"Error saving clinician prediction: {save_error}")
            
            # Detailed interpretation with recommendations
            return JsonResponse({
                'prediction': int(prediction),
                'risk_level': "High Risk" if prediction == 1 else "Low Risk",
                'risk_probability': round(positive_prob, 2) if positive_prob is not None else None,
                'input_data': form_data,
                'recommendations': recommendations,
                'risk_factors': risk_factors
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

class ClinicianPredictionsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # First, verify the token is valid
            if not request.user.is_authenticated:
                return Response({
                    'error': 'Authentication required'
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Then verify user is a clinician
            try:
                user_profile = UserProfile.objects.get(user=request.user)
                if user_profile.user_type != 'clinician':
                    return Response({
                        'error': 'Only clinicians can access patient predictions'
                    }, status=status.HTTP_403_FORBIDDEN)
            except UserProfile.DoesNotExist:
                return Response({
                    'error': 'User profile not found'
                }, status=status.HTTP_403_FORBIDDEN)

            # Get search parameters
            search_query = request.GET.get('search', '').strip()
            
            # Base query for all predictions
            predictions = ClinicianCardiovascularPrediction.objects.all()
            
            # Apply search if provided
            if search_query:
                predictions = predictions.filter(
                    models.Q(patient_name__icontains=search_query) |
                    models.Q(patient_email__icontains=search_query)
                )
            
            # Serialize the predictions
            prediction_data = [{
                'id': pred.id,
                'patient_name': pred.patient_name,
                'patient_email': pred.patient_email,
                'created_at': pred.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'age': pred.age,
                'sex': pred.sex,
                'chest_pain': pred.chest_pain,
                'resting_bp': pred.resting_bp,
                'cholesterol': pred.cholesterol,
                'fasting_bs': pred.fasting_bs,
                'resting_ecg': pred.resting_ecg,
                'max_heart_rate': pred.max_heart_rate,
                'exercise_angina': pred.exercise_angina,
                'oldpeak': pred.oldpeak,
                'slope': pred.slope,
                'major_vessels': pred.major_vessels,
                'prediction': pred.prediction,
                'risk_level': pred.risk_level,
                'risk_probability': pred.risk_probability,
                'risk_factors': pred.risk_factors
            } for pred in predictions]
            
            return Response(prediction_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PatientPredictionHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Fetch predictions for the logged-in user, ordered by most recent first
        predictions = PatientPrediction.objects.filter(user=request.user).order_by('-created_at')
        
        # Serialize the predictions
        prediction_data = [{
            'id': pred.id,
            'created_at': pred.created_at,
            'age': pred.age,
            'gender': pred.gender,
            'height': pred.height,
            'weight': pred.weight,
            'systolic_bp': pred.systolic_bp,
            'diastolic_bp': pred.diastolic_bp,
            'cholesterol': pred.cholesterol,
            'glucose': pred.glucose,
            'smoking': pred.smoking,
            'alcohol': pred.alcohol,
            'physical_activity': pred.physical_activity,
            'prediction': pred.prediction,
            'risk_level': pred.risk_level,
            'risk_probability': pred.risk_probability,
            'bmi': pred.bmi,
            'bmi_category': pred.bmi_category,
            'blood_pressure_category': pred.blood_pressure_category
        } for pred in predictions]
        
        return Response(prediction_data, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict_cardiovascular(request):
    if request.method == 'POST':
        try:
            # Print authentication status at the start
            print(f"User authenticated: {request.user.is_authenticated}")
            print(f"User: {request.user}")
            
            # Parse JSON data from the request body
            data = json.loads(request.body)
            
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
            
            # Validate the data using the form
            form = CADPatient(form_data)
            if not form.is_valid():
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
            
            # Predict
            prediction = CAD_MODEL_2.predict(input_data)[0]
            prediction_proba = CAD_MODEL_2.predict_proba(input_data)[0]
            positive_prob = prediction_proba[1] * 100
            
            # Generate personalized recommendations
            recommendations = generate_recommendations(form_data, is_patient_form=True)
            
            # Calculate BMI
            height_m = form_data['height'] / 100
            weight_kg = form_data['weight']
            bmi = weight_kg / (height_m * height_m)
            
            # Determine BMI and BP categories
            bmi_category = get_bmi_category(bmi)
            bp_category = get_bp_category(form_data['ap_hi'], form_data['ap_lo'])
            
            response_data = {
                'prediction': int(prediction),
                'risk_level': "High Cardiovascular Risk" if prediction == 1 else "Low Cardiovascular Risk",
                'risk_probability': round(positive_prob, 2),
                'input_data': form_data,
                'recommendations': recommendations,
                'health_metrics': {
                    'bmi': round(bmi, 1),
                    'bmi_category': bmi_category,
                    'blood_pressure_category': bp_category,
                    'lifestyle_factors': {
                        'smoking': form_data['smoke'] == 1,
                        'alcohol': form_data['alco'] == 1,
                        'physical_activity': form_data['active'] == 1
                    }
                }
            }
            
            # Explicitly check for non-anonymous user
            if not isinstance(request.user, AnonymousUser) and request.user.is_authenticated:
                try:
                    prediction_obj = PatientPrediction.objects.create(
                        user=request.user,
                        age=form_data['age'],
                        gender=form_data['gender'],
                        height=form_data['height'],
                        weight=form_data['weight'],
                        systolic_bp=form_data['ap_hi'],
                        diastolic_bp=form_data['ap_lo'],
                        cholesterol=form_data['cholesterol'],
                        glucose=form_data['gluc'],
                        smoking=form_data['smoke'] == 1,
                        alcohol=form_data['alco'] == 1,
                        physical_activity=form_data['active'] == 1,
                        prediction=prediction,
                        risk_level=response_data['risk_level'],
                        risk_probability=response_data['risk_probability'],
                        bmi=round(bmi, 1),
                        bmi_category=bmi_category,
                        blood_pressure_category=bp_category
                    )
                    print(f"Prediction saved successfully: {prediction_obj.id}")
                except Exception as save_error:
                    print(f"Error saving prediction: {save_error}")
                    import traceback
                    traceback.print_exc()
            else:
                print("User is not authenticated or is anonymous")
            
            return JsonResponse(response_data)
        
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return JsonResponse({
                'error': str(e)
            }, status=500)
    
    return JsonResponse({
        'error': 'Only POST method is allowed'
    }, status=405)


def get_bmi_category(bmi):
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal weight"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"

def get_bp_category(systolic, diastolic):
    if systolic < 120 and diastolic < 80:
        return "Normal"
    elif systolic < 130 and diastolic < 80:
        return "Elevated"
    elif systolic < 140 or diastolic < 90:
        return "Stage 1 Hypertension"
    else:
        return "Stage 2 Hypertension"