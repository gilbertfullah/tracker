from django import forms
from .models import IndicatorData, CitizenPrioritiesData
from django.db import transaction

    
    
class IndicatorDataForm(forms.ModelForm):
    class Meta:
        model = IndicatorData
        fields = ['indicator_value']  # Include all fields from the IndicatorData model
        # You can also exclude fields if necessary: exclude = ['field_to_exclude']
        
class CitizenPrioritiesForm(forms.ModelForm):
    class Meta:
        model = CitizenPrioritiesData
        fields = '__all__'
        
class IndicatorStatusDataForm(forms.ModelForm):
    class Meta:
        model = IndicatorData
        fields = ['status']
        
class IndicatorDataEditForm(forms.ModelForm):
    class Meta:
        model = IndicatorData
        fields = ['indicator', 'district', 'service_type', 'media_outlets', 'answer_choice_trust', 'answer_choice_comm_stability', 'bribery_services', 'indicator_value', 'status']

class IndicatorDataCreateForm(forms.ModelForm):
    class Meta:
        model = IndicatorData
        fields = ['district', 'service_type', 'media_outlets', 'answer_choice_trust', 'answer_choice_comm_stability', 'bribery_services', 'indicator_value', 'status']