from django.shortcuts import render, redirect, get_object_or_404
from .forms import IndicatorDataForm
from .models import Indicator, IndicatorData, TrustInLocalAuthorities
import os
from django.conf import settings
import calendar
from django.db.models.functions import ExtractMonth, ExtractHour, ExtractDay
from django.db.models import Count, CharField, Value
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncDate, Cast
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from functools import wraps
from schools.models import School, District, ServiceType
from django.db.models import Avg
from django.db.models import Count, F, ExpressionWrapper, FloatField
from decimal import Decimal
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.forms import modelformset_factory
from django.http import JsonResponse



def satisfaction_data_form(request):
    if request.method == 'POST':
        # Handle form submission
        form = IndicatorDataForm(request.POST)
        if form.is_valid():
            # Save the form data to the database
            form.save()
            return redirect('/')  # Redirect to the same page after submission
    else:
        form = IndicatorDataForm()
    
    context = {'form': form}
    return render(request, 'satisfaction_data_form.html', context)

def satisfaction_data_display(request):
    # Get all available districts and service types for filtering
    all_districts = District.objects.all()
    all_service_types = ServiceType.objects.all()
    
    # Calculate average percentages for all districts and service types
    all_districts_avg = IndicatorData.objects.values('district').annotate(avg=Avg('indicator_value'))
    all_service_types_avg = IndicatorData.objects.values('service_type').annotate(avg=Avg('indicator_value'))

    selected_district = request.GET.get('district')
    selected_service_type = request.GET.get('service_type')

    if selected_district:
        district_avg = all_districts_avg.filter(district=selected_district)
    else:
        district_avg = None

    if selected_service_type:
        service_type_avg = all_service_types_avg.filter(service_type=selected_service_type)
    else:
        service_type_avg = None

    context = {
        'all_districts': all_districts,
        'all_service_types': all_service_types,
        'all_districts_avg': all_districts_avg,
        'all_service_types_avg': all_service_types_avg,
        'selected_district': selected_district,
        'selected_service_type': selected_service_type,
        'district_avg': district_avg,
        'service_type_avg': service_type_avg,
    }

    return render(request, 'satisfaction_data_display.html', context)


def satisfaction_indicator_view(request):
    health_service_type = ServiceType.objects.get(name='Health')
    edu_service_type = ServiceType.objects.get(name='Education')
    agri_service_type = ServiceType.objects.get(name='Agriculture')
    # Calculate the average indicator_value for Health
    health_avg = Decimal(IndicatorData.objects.filter(service_type=health_service_type).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    health_avg = round(health_avg, 2)

    # Calculate the average indicator_value for Education
    education_avg = Decimal(IndicatorData.objects.filter(service_type=edu_service_type).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    education_avg = round(education_avg, 2) 

    # Calculate the average indicator_value for Agriculture
    agriculture_avg = Decimal(IndicatorData.objects.filter(service_type=agri_service_type).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    agriculture_avg = round(agriculture_avg, 2)

    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_value):
        if avg_value <= 34:
            return 'red', 'down'
        elif 35 <= avg_value <= 49:
            return 'orange', 'right'
        else:
            return 'green', 'up'


    health_color, health_arrow = get_color_and_arrow(health_avg)
    education_color, education_arrow = get_color_and_arrow(education_avg)
    agriculture_color, agriculture_arrow = get_color_and_arrow(agriculture_avg)

    context = {
        'health_avg': health_avg,
        'education_avg': education_avg,
        'agriculture_avg': agriculture_avg,
        'health_color': health_color,
        'education_color': education_color,
        'agriculture_color': agriculture_color,
        'health_arrow': health_arrow,
        'education_arrow': education_arrow,
        'agriculture_arrow': agriculture_arrow,
    }

    return render(request, 'satisfaction_data_display.html', context)


def manage_indicator(request, indicator_id):
    indicator = get_object_or_404(Indicator, pk=indicator_id)
    
    # Query all indicator values for the selected indicator
    indicator_data = IndicatorData.objects.filter(indicator=indicator_id)
    
    IndicatorDataFormSet = modelformset_factory(IndicatorData, fields=('indicator_value',), extra=0)

    if request.method == 'POST':
        form = IndicatorDataForm(request.POST)
        if form.is_valid():
            # Process the form data to update indicator values
            for data in indicator_data.all():
                data_id = data.id
                field_name = f'indicator_value_{data_id}'
                new_value = form.cleaned_data.get(field_name)
                
                if new_value is not None:
                    data.indicator_value = new_value
                    data.status = 'pending'
                    data.save()
    else:
        indicator_data = indicator_data.all()
        initial_data = {f'indicator_value_{data.id}': data.indicator_value for data in indicator_data}
        form = IndicatorDataForm(initial=initial_data)

    
    context = {
        'indicator': indicator,
        'indicator_data': indicator_data,
        'form': form,
    }
    
    return render(request, 'manage_indicator.html', context)


def manage_indicator_view(request, indicator_id):
    indicator = get_object_or_404(IndicatorData, id=indicator_id)

    if request.method == 'POST':
        form = IndicatorDataForm(request.POST, instance=indicator)
        if form.is_valid():
            indicator = form.save(commit=False)
            if request.user.is_superuser:
                # Superuser approval
                indicator.status = form.cleaned_data['status']
            else:
                # Manager update, set status to "pending"
                indicator.status = 'pending'
            indicator.save()
            return redirect('dashboard')

    else:
        form = IndicatorDataForm(instance=indicator)

    context = {'form': form, 'indicator': indicator}
    return render(request, 'manage_indicator.html', context)


def trust_in_local_authorities(request):
    answer_choices = TrustInLocalAuthorities.objects.values_list('answer_choice', flat=True).distinct()
    
    # Get the distinct dates
    dates = TrustInLocalAuthorities.objects.values_list('date_submitted', flat=True).distinct().order_by('date_submitted')
    
    # Create a dictionary to store data for each service type
    data_by_answer_choice = {choice: [] for choice in answer_choices}
    
    for date in dates:
        for choice in answer_choices:
            queryset = TrustInLocalAuthorities.objects.filter(date_submitted=date, answer_choice=choice)
            avg_value = queryset.aggregate(Avg('indicator_value'))['indicator_value__avg']
            data_by_answer_choice[choice].append(avg_value)
    
    context = {
        'answer_choices': answer_choices,
        'dates': dates,
        'data_by_answer_choice': data_by_answer_choice,
    }
    
    return render(request, 'trust_in_local_authorities.html', context)


def indicator_list(request):
    indicators = IndicatorData.objects.values_list('indicator', flat=True).distinct()
    #indicators = IndicatorData.objects.all()
    return render(request, 'list_indicators.html', {'indicators': indicators})

def update_indicator_value(request, id):
    indicator = IndicatorData.objects.get(id=id)
    
    if request.method == 'POST':
        form = IndicatorDataForm(request.POST, instance=indicator)
        if form.is_valid():
            indicator = form.save(commit=False)
            indicator.status = 'pending'  # Set status to "pending"
            indicator.save()
            
            messages.success(request, 'Indicator value updated successfully.')

    else:
        messages.error(request, 'Error updating indicator value. Please check your input.')
        form = IndicatorDataForm(instance=indicator)
        
    context = {
        'form': form,
    }

    return render(request, 'update_indicator_value.html', context)


def indicator_detail(request, indicator_id):
    indicator = get_object_or_404(Indicator, pk=indicator_id)
    
    # Query all indicator values for the selected indicator
    indicator_data = IndicatorData.objects.filter(indicator=indicator_id)
    
    return render(request, 'indicator_details.html', {'indicator_data': indicator_data})