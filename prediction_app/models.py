from django.db import models
from django.contrib.auth.models import User

class ClinicianCardiovascularPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='clinician_predictions')
    
    # Patient information
    patient_name = models.CharField(max_length=255, default ="Unknown")
    patient_email = models.EmailField(null=True, blank=True)
    
    # Input fields
    age = models.FloatField()
    sex = models.IntegerField()
    chest_pain = models.IntegerField()
    resting_bp = models.FloatField()
    cholesterol = models.FloatField()
    fasting_bs = models.IntegerField()
    resting_ecg = models.IntegerField()
    max_heart_rate = models.FloatField()
    exercise_angina = models.IntegerField()
    oldpeak = models.FloatField()
    slope = models.IntegerField()
    major_vessels = models.IntegerField()
    
    # Prediction results
    prediction = models.IntegerField()
    risk_level = models.CharField(max_length=50)
    risk_probability = models.FloatField(null=True)
    
    # Risk factors (stored as JSON)
    risk_factors = models.JSONField(default=dict)  # Added default empty dictionary
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clinician_predictions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Prediction for {self.patient_name} by {self.user.username} on {self.created_at}"

class PatientPrediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predictions')
    
    # Patient input fields
    age = models.IntegerField()
    gender = models.IntegerField()
    height = models.FloatField()
    weight = models.FloatField()
    systolic_bp = models.FloatField()
    diastolic_bp = models.FloatField()
    cholesterol = models.IntegerField()
    glucose = models.IntegerField()
    smoking = models.BooleanField()
    alcohol = models.BooleanField()
    physical_activity = models.BooleanField()
    
    # Prediction results
    prediction = models.IntegerField()  # 0 or 1 for risk
    risk_level = models.CharField(max_length=50)
    risk_probability = models.FloatField()
    
    # Health metrics
    bmi = models.FloatField()
    bmi_category = models.CharField(max_length=50)
    blood_pressure_category = models.CharField(max_length=50)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'patient_predictions'
        ordering = ['-created_at']

    def __str__(self):
        return f"Prediction for {self.user.username} on {self.created_at}"