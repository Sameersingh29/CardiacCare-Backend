from django import forms

class CADPatient(forms.Form):
    # id = forms.IntegerField(label='ID', min_value=0, required=False)
    age = forms.IntegerField(label='Age', min_value=0, max_value=120)
    gender = forms.ChoiceField(label='Gender', choices=[(1, 'Male'), (2, 'Female')])
    height = forms.FloatField(label='Height (cm)', min_value=50, max_value=250)
    weight = forms.FloatField(label='Weight (kg)', min_value=10, max_value=300)
    ap_hi = forms.FloatField(label='Systolic Blood Pressure', min_value=0, max_value=300)
    ap_lo = forms.FloatField(label='Diastolic Blood Pressure', min_value=0, max_value=200)
    cholesterol = forms.ChoiceField(label='Cholesterol Level', choices=[
        (1, 'Normal'), 
        (2, 'Above Normal'), 
        (3, 'Well Above Normal')
    ])
    gluc = forms.ChoiceField(label='Glucose Level', choices=[
        (1, 'Normal'), 
        (2, 'Above Normal'), 
        (3, 'Well Above Normal')
    ])
    smoke = forms.ChoiceField(label='Smoking Status', choices=[(0, 'No'), (1, 'Yes')])
    alco = forms.ChoiceField(label='Alcohol Intake', choices=[(0, 'No'), (1, 'Yes')])
    active = forms.ChoiceField(label='Physical Activity', choices=[(0, 'No'), (1, 'Yes')])
    cardio = forms.ChoiceField(label='Cardiovascular Disease', choices=[(0, 'No'), (1, 'Yes')], required=False)
    def clean_age(self):
        age_in_years = self.cleaned_data['age']
        # Convert age in years to age in days
        age_in_days = age_in_years * 365.25
        return age_in_days

class CADPredictionForm(forms.Form):
    age = forms.FloatField(label='Age', min_value=0, max_value=120)
    sex = forms.ChoiceField(label='Sex', choices=[(0, 'Female'), (1, 'Male')])
    chest_pain = forms.ChoiceField(label='Chest Pain Type', choices=[
        (0, 'Typical Angina'), 
        (1, 'Atypical Angina'), 
        (2, 'Non-Anginal Pain'), 
        (3, 'Asymptomatic')
    ])
    resting_bp = forms.FloatField(label='Resting Blood Pressure', min_value=0, max_value=300)
    cholesterol = forms.FloatField(label='Cholesterol', min_value=0, max_value=600)
    fasting_bs = forms.ChoiceField(label='Fasting Blood Sugar', choices=[(0, '<120 mg/dl'), (1, '>120 mg/dl')])
    resting_ecg = forms.ChoiceField(label='Resting ECG', choices=[
        (0, 'Normal'), 
        (1, 'ST-T Wave Abnormality'), 
        (2, 'Left Ventricular Hypertrophy')
    ])
    max_heart_rate = forms.FloatField(label='Max Heart Rate', min_value=0, max_value=300)
    exercise_angina = forms.ChoiceField(label='Exercise Induced Angina', choices=[(0, 'No'), (1, 'Yes')])
    oldpeak = forms.FloatField(label='Oldpeak ST', min_value=-10, max_value=10)
    slope = forms.ChoiceField(label='Slope of Peak Exercise ST', choices=[
        (0, 'Upsloping'), 
        (1, 'Flat'), 
        (2, 'Downsloping')
    ])
    major_vessels = forms.ChoiceField(label='Number of Major Vessels Colored', choices=[
        (0, '0'), 
        (1, '1'), 
        (2, '2'), 
        (3, '3')
    ])
