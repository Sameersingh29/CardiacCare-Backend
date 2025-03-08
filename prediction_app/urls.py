from django.urls import path
from . import views
from .views import PatientPredictionHistoryView, ClinicianPredictionsView

urlpatterns = [
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('predict/', views.predict, name='predict'),
    path('predict_cardiovascular/',views.predict_cardiovascular, name = 'predict_cardiovascular'),
    path('api/patient/predictions/', PatientPredictionHistoryView.as_view(), name='patient-predictions'),
    path('api/clinician/predictions/', ClinicianPredictionsView.as_view(), name='clinician-predictions'),
    # path('patients/', views.patient_list, name='patient-list'),
]