def generate_recommendations(input_data, is_patient_form=True):
    """
    Generate personalized recommendations based on input data and form type.
    
    Args:
        input_data (dict): Dictionary containing the form input data
        is_patient_form (bool): True if using patient form, False if using clinician form
    
    Returns:
        dict: Dictionary containing general and specific recommendations
    """
    recommendations = {
        'general': [],
        'specific': [],
        'urgent_actions': [],
        'lifestyle': [],
        'monitoring': []
    }
    
    if is_patient_form:
        # Process patient form specific inputs
        
        # Blood pressure recommendations
        systolic = float(input_data.get('ap_hi', 0))
        diastolic = float(input_data.get('ap_lo', 0))
        
        if systolic >= 140 or diastolic >= 90:
            recommendations['urgent_actions'].append("Schedule an appointment with your healthcare provider to discuss your blood pressure.")
            recommendations['specific'].append("Consider the DASH diet which is specifically designed for blood pressure management.")
        
        # BMI-based recommendations
        height_m = float(input_data.get('height', 170)) / 100
        weight_kg = float(input_data.get('weight', 70))
        bmi = weight_kg / (height_m * height_m)
        
        if bmi > 25:
            recommendations['specific'].append(f"Your BMI is {bmi:.1f}. Consider working with a nutritionist to develop a personalized weight management plan.")
            recommendations['lifestyle'].append("Aim for 45-60 minutes of moderate exercise most days of the week.")
        
        # Lifestyle factors
        if input_data.get('smoke') == '1':
            recommendations['urgent_actions'].append("Consult with your healthcare provider about smoking cessation programs and nicotine replacement therapy.")
            recommendations['specific'].append("Consider joining a smoking cessation support group.")
        
        if input_data.get('alco') == '1':
            recommendations['lifestyle'].append("Limit alcohol consumption to no more than 1-2 drinks per day.")
        
        if input_data.get('active') == '0':
            recommendations['lifestyle'].append("Start with short 10-minute walks and gradually increase duration and intensity.")
            recommendations['lifestyle'].append("Consider joining a guided exercise program or working with a physical trainer.")
        
        # Cholesterol and glucose recommendations
        if input_data.get('cholesterol') in ['2', '3']:
            recommendations['specific'].append("Schedule a detailed lipid panel test.")
            recommendations['lifestyle'].append("Incorporate heart-healthy foods like olive oil, nuts, and fatty fish into your diet.")
        
        if input_data.get('gluc') in ['2', '3']:
            recommendations['monitoring'].append("Monitor your blood sugar regularly and keep a log.")
            recommendations['specific'].append("Consider consulting with a diabetes educator.")
    
    else:
        # Process clinician form specific inputs
        
        # Chest pain evaluation
        if input_data.get('chest_pain') in ['0', '1']:
            recommendations['urgent_actions'].append("Consider immediate stress test and coronary evaluation.")
            recommendations['specific'].append("Evaluate need for antianginal medication.")
        
        # ECG abnormalities
        if input_data.get('resting_ecg') in ['1', '2']:
            recommendations['specific'].append("Schedule follow-up ECG in 4-6 weeks.")
            recommendations['monitoring'].append("Consider 24-hour Holter monitoring.")
        
        # Exercise angina
        if input_data.get('exercise_angina') == '1':
            recommendations['urgent_actions'].append("Evaluate need for coronary angiography.")
            recommendations['specific'].append("Consider stress imaging studies.")
        
        # Major vessels
        if int(input_data.get('major_vessels', 0)) > 0:
            recommendations['urgent_actions'].append(f"Consider coronary intervention given {input_data['major_vessels']} affected vessels.")
        
        # ST depression
        oldpeak = float(input_data.get('oldpeak', 0))
        if oldpeak > 2:
            recommendations['urgent_actions'].append("Significant ST depression warrants immediate attention.")
            recommendations['specific'].append("Consider myocardial perfusion imaging.")
    
    # Common recommendations for both forms
    recommendations['monitoring'].extend([
        "Schedule regular blood pressure checks",
        "Get comprehensive bloodwork every 6 months",
        "Keep a symptom diary to track any changes"
    ])
    
    return recommendations