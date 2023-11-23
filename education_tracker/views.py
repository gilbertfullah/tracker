from django.shortcuts import render
from schools.models import School, District, ServiceType
from django.db.models import Avg, Sum, Case, When, Value, DecimalField
from django.db.models import Count, F, ExpressionWrapper, FloatField
from decimal import Decimal
from indicators.models import IndicatorData, CitizenPrioritiesData, CitizenPrioritiesData, TrustInLocalAuthorities, NPSEResults, CommunityStability, \
    BudgetAllocation, BriberyReductionData, SatisfactionData
from datetime import datetime
import json
from django.db.models.functions import ExtractYear
from collections import defaultdict
from django.db.models import Q

def index(request):
    ##############Trust Section Start##################
    avg_values_by_year = defaultdict(list)

    indicator_values = IndicatorData.objects.annotate(trust_group=Case(When(answer_choice_trust__in=["A lot", "Somewhat"], then=Value("A lot/Somewhat")),
        When(answer_choice_trust__in=["Just a little", "Not at all"], then=Value("Just a little/Not at all")), default=F('answer_choice_trust'),),
    year=ExtractYear('date_submitted')).values('year', 'trust_group').annotate(avg=Sum('indicator_value') / Count('indicator_value', output_field=DecimalField()))

    # Populate the dictionary
    for entry in indicator_values:
        year = entry['year']
        trust_group = entry['trust_group']
        avg_value = float(entry['avg'])
        avg_values_by_year[year].append({'trust_group': trust_group, 'avg_value': avg_value})

    trust_group_alot_somewhat = []
    avg_alot_somewhat = []

    trust_group_justalittle_notatall = []
    avg_justalittle_notatall = []
    
    distinct_years_alot_somewhat = set()
    distinct_years_justalittle_notatall = set()
    
    sum_by_year_alot_somewhat = {}
    count_by_year_alot_somewhat = {}
    sum_by_year_justalittle_notatall = {}
    count_by_year_justalittle_notatall = {}
    
    for year, values in avg_values_by_year.items():
        for entry in values:
            if entry['trust_group'] == "A lot/Somewhat":
                trust_group_alot_somewhat.append(entry['trust_group'])
                avg_alot_somewhat.append(entry['avg_value'])
                distinct_years_alot_somewhat.add(year)

                # Update the sum and count for A lot/Somewhat
                sum_by_year_alot_somewhat[year] = sum_by_year_alot_somewhat.get(year, 0) + entry['avg_value']
                count_by_year_alot_somewhat[year] = count_by_year_alot_somewhat.get(year, 0) + 1

            if entry['trust_group'] == "Just a little/Not at all":
                trust_group_justalittle_notatall.append(entry['trust_group'])
                avg_justalittle_notatall.append(entry['avg_value'])
                distinct_years_justalittle_notatall.add(year)

                # Update the sum and count for Just a little/Not at all
                sum_by_year_justalittle_notatall[year] = sum_by_year_justalittle_notatall.get(year, 0) + entry['avg_value']
                count_by_year_justalittle_notatall[year] = count_by_year_justalittle_notatall.get(year, 0) + 1

    # Convert sets to lists if needed
    distinct_years_alot_somewhat = list(distinct_years_alot_somewhat)
    distinct_years_justalittle_notatall = list(distinct_years_justalittle_notatall)

    # Calculate the average for A lot/Somewhat
    avg_by_year_alot_somewhat = {year: sum_by_year_alot_somewhat[year] / count_by_year_alot_somewhat[year] for year in distinct_years_alot_somewhat}

    # Calculate the average for Just a little/Not at all
    avg_by_year_justalittle_notatall = {year: sum_by_year_justalittle_notatall[year] / count_by_year_justalittle_notatall[year] for year in distinct_years_justalittle_notatall}

    # Extract keys (years) and values (average indicator values) from avg_by_year_alot_somewhat
    keys_alot_somewhat = list(avg_by_year_alot_somewhat.keys())
    values_alot_somewhat = list(avg_by_year_alot_somewhat.values())
    
    keys_justalittle_notatall = list(avg_by_year_justalittle_notatall.keys())
    values_justalittle_notatall = list(avg_by_year_justalittle_notatall.values())
    
    ##############Trust Section End####################################
    
    ##############Maternal Mortality by Year Section Start##################
    
    maternal_mortality_indicator_name = "Maternal Mortality by year"
    
    maternal_mortality_indicator_values = IndicatorData.objects.filter(indicator__name=maternal_mortality_indicator_name, status='approved',). \
                                        values('indicator__name', year=ExtractYear('date_submitted')).annotate(avg_value=Avg('indicator_value')). \
                                        order_by('year', 'avg_value')
    maternal_mortality_years = []
    maternal_mortality_year_values = []
    
    for entry in maternal_mortality_indicator_values:
        maternal_mortality_years.append(entry['year'])
        maternal_mortality_year_values.append(float(entry['avg_value']))
    
    ##############Maternal Mortality by Year Section End##################
    
    ##############Maternal Mortality Section Start##################
    
    maternal_mortality_indicator = f"% reduction in maternal mortality by district"
    
    avg_maternal_mortality = IndicatorData.objects.filter(indicator__name=maternal_mortality_indicator, status='approved',). \
                                        values('indicator__name', 'district__name').annotate(avg_value=Avg('indicator_value')). \
                                        order_by('district__name', 'avg_value')
    maternal_mortality_districts = []
    maternal_mortality_district_values = []
    
    for entry in avg_maternal_mortality:
        maternal_mortality_districts.append(entry['district__name'])
        maternal_mortality_district_values.append(float(entry['avg_value']))
        
    maternal_mortality_districts.append('National Average')
    maternal_mortality_district_values.append(-68)
        
    ##############Maternal Mortality Section End##################
    
    ##############Infant Mortality by Year Section Start##################
    
    infant_mortality_indicator_name = "Mortality of under five children by year"
    
    infant_mortality_indicator_values = IndicatorData.objects.filter(indicator__name=infant_mortality_indicator_name, status='approved',). \
                                        values('indicator__name', year=ExtractYear('date_submitted')).annotate(avg_value=Avg('indicator_value')). \
                                        order_by('year', 'avg_value')
    infant_mortality_years = []
    infant_mortality_year_values = []
    
    for entry in infant_mortality_indicator_values:
        infant_mortality_years.append(entry['year'])
        infant_mortality_year_values.append(float(entry['avg_value']))
        
    ##############Infant Mortality by Year Section End##################
    
    ##############Maternal Mortality Section Start##################
    
    infant_mortality_indicator = f"Mortality of under five children by districts"
    
    avg_infant_mortality = IndicatorData.objects.filter(indicator__name=infant_mortality_indicator, status='approved',). \
                                        values('indicator__name', 'district__name').annotate(avg_value=Avg('indicator_value')). \
                                        order_by('district__name', 'avg_value')
    infant_mortality_districts = []
    infant_mortality_district_values = []
    
    for entry in avg_infant_mortality:
        infant_mortality_districts.append(entry['district__name'])
        infant_mortality_district_values.append(float(entry['avg_value']))
        
    infant_mortality_districts.append('National Average')
    infant_mortality_district_values.append(-6)
        
    ##############Maternal Mortality Section End##################
    
    ##############NPSE Section Start##################
    
    # Calculate the average indicator_value for all districts where status is approved
    npse_indicator = f"% increase learning outcomes as reflected in the NPSE scores in focused districts"
    
    avg_npse_values = IndicatorData.objects.filter(indicator__name=npse_indicator, status='approved',). \
                                        values('indicator__name', 'district__name').annotate(avg_value=Avg('indicator_value')). \
                                        order_by('district__name', 'avg_value')
    
    npse_districts = []
    npse_district_values = []
    
    for entry in avg_npse_values:
        npse_districts.append(entry['district__name'])
        npse_district_values.append(float(entry['avg_value']))
        
    npse_districts.append('National Average')
    npse_district_values.append(248)
        
    ##############NPSE Section End##################
    
    ##############Stability Section Start##################
    stability_indicator = f'% increased in community stability'
    stability_choice = 'Very much'
                                        
    com_stability_choice_values = IndicatorData.objects.filter(indicator__name=stability_indicator, answer_choice_comm_stability=stability_choice, status='approved',). \
                                        values('answer_choice_comm_stability', 'district__name').annotate(avg_value=Avg('indicator_value')). \
                                        order_by('district__name', 'avg_value')
                                        
    stability_districts = []
    stability_choice_district_values = []

    for entry in com_stability_choice_values:
        stability_districts.append(entry['district__name'])
        stability_choice_district_values.append(float(entry['avg_value']))
    
    # Define functions to determine color class and description based on percentage
    def get_color_class(percentage):
        if percentage < 60:
            return "bg-red-500"  # Low
        elif percentage < 70:
            return "bg-yellow-500"  # Medium
        else:
            return "bg-green-500"  # High

    def get_color_description(percentage):
        if percentage < 60:
            return "Low stability"
        elif percentage < 70:
            return "Medium stability"
        else:
            return "High stability"
    
    # Process the percentage values and add color class and color description
    div_data = [
        {
            "district": district,
            "percentage": val,
            "color_class": get_color_class(val),
            "color_description": get_color_description(val),
        }
        for district, val in zip(stability_districts, stability_choice_district_values)
    ]
    # Process the percentage values and add color class
    # div_data = [{'district': district, 'percentage': val, 'color_class': 'bg-red-500' if val < 40 else 'bg-green-500'}
    # for district, val in zip(stability_districts, stability_choice_district_values)
    # ]
    
    ##############Stability Section End##################
    
    ##############Budget Section Start##################
    
    # Define the target answer_choice and date_submitted values
    budget_indicator = f"% of budget allocated to devolved functions"

    budget_date_2022 = datetime(2022, 10, 29)

    # Calculate the average indicator_value for each target

    avg_budget_2022 = Decimal(IndicatorData.objects.filter(date_submitted=budget_date_2022, status='approved', indicator__name=budget_indicator).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_budget_2022 = round(avg_budget_2022, 2) 

    
    ##############Budget Section End#########################
    
    ##############Bribery Section Start#########################
    target_date_2022 = datetime(2022, 10, 30)

    # List of services you want to retrieve
    services_to_retrieve = ["Medical services", "Public school"]

    # Create a Q object to filter by services
    services_filter = Q()
    for service in services_to_retrieve:
        services_filter |= Q(bribery_services=service)

    # Retrieve data for the specified services and year
    services_values = IndicatorData.objects.filter(services_filter, status='approved', date_submitted__year=target_date_2022.year,). \
        values('bribery_services').annotate(avg_value=Avg('indicator_value')).order_by('bribery_services', 'avg_value')

    services = []
    service_values = []

    for entry in services_values:
        services.append(entry['bribery_services'])
        service_values.append(float(entry['avg_value']))
        
    # Define functions to determine color class and description based on percentage
    def get_color_class(percentage):
        if percentage < 30:
            return "bg-green-500"  # Low
        elif percentage < 50:
            return "bg-yellow-500"  # Medium
        else:
            return "bg-red-500"  # High

    def get_color_description(percentage):
        if percentage < 30:
            return "Less than 30%"
        elif percentage < 50:
            return " > 30% < 50%"
        else:
            return "> 50%"
    
    # Process the percentage values and add color class and color description
    bribery_data = [
        {
            "percentage": val,
            "color_class": get_color_class(val),
            "color_description": get_color_description(val),
        }
        for val in service_values
    ]
        
    #bribery_data = [{'percentage': val, 'color_class': 'bg-red-500' if val < 40 else 'bg-green-500'} for val in service_values]
    
    ##############Bribery Section End#########################
    
    ##############Audit Recommendation Section Start#########################
    audit_indicator = f'% increase in audit recommendations implemented by the councils'
                                        
    audit_values = IndicatorData.objects.filter(indicator__name=audit_indicator, status='approved',). \
                                    values('district__name').annotate(avg_value=Avg('indicator_value')).order_by('district__name', 'avg_value')
                                        
    audit_districts = []
    audit_district_values = []

    for entry in audit_values:
        audit_districts.append(entry['district__name'])
        audit_district_values.append(float(entry['avg_value']))
        
    # Define functions to determine color class and description based on percentage
    def get_color_class(percentage):
        if percentage < 45:
            return "bg-red-500"  # Low
        elif percentage < 60:
            return "bg-yellow-500"  # Medium
        else:
            return "bg-green-500"  # High

    def get_color_description(percentage):
        if percentage < 45:
            return "Less than 30%"
        elif percentage < 60:
            return "> 30% < 60%"
        else:
            return "> 60%"
    
    # Process the percentage values and add color class and color description
    audit_data = [
        {
            'district': district,
            "percentage": val,
            "color_class": get_color_class(val),
            "color_description": get_color_description(val),
        }
        for district, val in zip(audit_districts, audit_district_values)
    ]
        
    # Process the percentage values and add color class
    # audit_data = [{'district': district, 'percentage': val, 'color_class': 'bg-red-500' if val < 40 else 'bg-green-500'}
    # for district, val in zip(audit_districts, audit_district_values)]
    
    ##############Audit Recommendation Section End#########################
    
    ##############LC Revenue Misuse Section Start#########################
    misuse_indicator = f'% Reduction in citizens who believe local councils misuse revenue'
                                        
    misuse_values = IndicatorData.objects.filter(indicator__name=misuse_indicator, status='approved',). \
                                    values('district__name').annotate(avg_value=Avg('indicator_value')).order_by('district__name', 'avg_value')
                                        
    misuse_districts = []
    misuse_district_values = []

    for entry in misuse_values:
        misuse_districts.append(entry['district__name'])
        misuse_district_values.append(float(entry['avg_value']))
        
    # Define functions to determine color class and description based on percentage
    def get_color_class(percentage):
        if percentage < 20:
            return "bg-red-500"  # Low
        elif percentage < 40:
            return "bg-yellow-500"  # Medium
        else:
            return "bg-green-500"  # High

    def get_color_description(percentage):
        if percentage < 20:
            return "Less than 20%"
        elif percentage < 60:
            return "> 20% < 40%"
        else:
            return "> 40%"
    
    # Process the percentage values and add color class and color description
    misuse_data = [
        {
            'district': district,
            "percentage": val,
            "color_class": get_color_class(val),
            "color_description": get_color_description(val),
        }
        for district, val in zip(misuse_districts, misuse_district_values)
    ]
        
    # Process the percentage values and add color class
    # misuse_data = [{'district': district, 'percentage': val, 'color_class': 'bg-red-500' if val < 40 else 'bg-green-500'}
    # for district, val in zip(misuse_districts, misuse_district_values)]
    
    ##############LC Revenue Misuse Section End#########################
    
    ##############Agricultural Satisfaction Section Start#########################
    agri_satisfaction_indicator = f'Satisfaction with government services in Agriculture​'
                                        
    agri_saf_values = SatisfactionData.objects.filter(indicator__name=agri_satisfaction_indicator, status='approved',). \
                                    values('satisfaction_services').annotate(avg_value=Avg('indicator_value')).order_by('satisfaction_services', 'avg_value')
                                        
    satisfaction_services = []
    satisfaction_services_values = []

    for entry in agri_saf_values:
        satisfaction_services.append(entry['satisfaction_services'])
        satisfaction_services_values.append(float(entry['avg_value']))
        
    # Define functions to determine color class and description based on percentage
    def get_color_class(percentage):
        if percentage < 50:
            return "bg-red-500"  # Low
        elif percentage < 60:
            return "bg-yellow-500"  # Medium
        else:
            return "bg-green-500"  # High

    def get_color_description(percentage):
        if percentage < 50:
            return "Less than 50%"
        elif percentage < 60:
            return "> 50% < 60%"
        else:
            return "> 60%"
    
    # Process the percentage values and add color class and color description
    satisfaction_services_data = [
        {
            'services': service,
            "percentage": val,
            "color_class": get_color_class(val),
            "color_description": get_color_description(val),
        }
        for service, val in zip(satisfaction_services, satisfaction_services_values)
    ]
        
    # Process the percentage values and add color class
    # satisfaction_services_data = [{'services': service, 'percentage': val, 'color_class': 'bg-red-500' if val < 60 else 'bg-green-500'} 
    #                             for service, val in zip(satisfaction_services, satisfaction_services_values)]
    
    ##############Agricultural Satisfaction Section End#########################
    
    ##############LC Budget Section Start#########################
    lc_budget_indicator = f"% of citizens who are aware of local council budget"
                                        
    lc_budget_indicator_values = IndicatorData.objects.filter(indicator__name=lc_budget_indicator, status='approved',). \
                                    values('district__name').annotate(avg_value=Avg('indicator_value')).order_by('district__name', 'avg_value')
                                        
    lc_budget_districts = []
    lc_budget_values = []

    for entry in lc_budget_indicator_values:
        lc_budget_districts.append(entry['district__name'])
        lc_budget_values.append(float(entry['avg_value']))
        
    # Define functions to determine color class and description based on percentage
    def get_color_class(percentage):
        if percentage < 30:
            return "bg-red-500"  # Low
        elif percentage < 50:
            return "bg-yellow-500"  # Medium
        else:
            return "bg-green-500"  # High

    def get_color_description(percentage):
        if percentage < 30:
            return "Less than 30%"
        elif percentage < 50:
            return "> 30% < 50%"
        else:
            return "> 50%"
    
    # Process the percentage values and add color class and color description
    lc_budget_data = [
        {
            'districts': district,
            "percentage": val,
            "color_class": get_color_class(val),
            "color_description": get_color_description(val),
        }
        for district, val in zip(lc_budget_districts, lc_budget_values)
    ]
        
    # Process the percentage values and add color class
    # lc_budget_data = [{'districts': district, 'percentage': val, 'color_class': 'bg-red-500' if val < 8 else 'bg-green-500'} 
    #                             for district, val in zip(lc_budget_districts, lc_budget_values)]
    
    # print(lc_budget_data)
    
    ##############LC Budget Section End#########################
    
    ##############LC Projects Section Start#########################
    lc_project_indicator = f"% of citizens who are aware of local council projects"
                                        
    lc_projects_indicator_values = IndicatorData.objects.filter(indicator__name=lc_project_indicator, status='approved',). \
                                    values('district__name').annotate(avg_value=Avg('indicator_value')).order_by('district__name', 'avg_value')
                                        
    lc_projects_districts = []
    lc_projects_values = []

    for entry in lc_projects_indicator_values:
        lc_projects_districts.append(entry['district__name'])
        lc_projects_values.append(float(entry['avg_value']))
        
    # Define functions to determine color class and description based on percentage
    def get_color_class(percentage):
        if percentage < 30:
            return "bg-red-500"  # Low
        elif percentage < 50:
            return "bg-yellow-500"  # Medium
        else:
            return "bg-green-500"  # High

    def get_color_description(percentage):
        if percentage < 30:
            return "Less than 30%"
        elif percentage < 50:
            return "> 30% < 50%"
        else:
            return "> 50%"
    
    # Process the percentage values and add color class and color description
    lc_projects_data = [
        {
            'districts': district,
            "percentage": val,
            "color_class": get_color_class(val),
            "color_description": get_color_description(val),
        }
        for district, val in zip(lc_projects_districts, lc_projects_values)
    ]

    ##############LC Projects Section End#########################
    
    ##############Joint Advocacy Section Start#########################

    joint_advocacy_indicator = f"Number of joint advocacy initiatives implemented by LCs and CSOs"
                                        
    joint_advocacy_indicator_values = IndicatorData.objects.filter(indicator__name=joint_advocacy_indicator, status='approved',). \
                                    values('district__name').annotate(avg_value=Avg('indicator_value')).order_by('district__name', 'avg_value')
                                        
    joint_advocacy_districts = []
    joint_advocacy_values = []

    for entry in joint_advocacy_indicator_values:
        joint_advocacy_districts.append(entry['district__name'])
        joint_advocacy_values.append(float(entry['avg_value']))
        
    # Define functions to determine color class and description based on percentage
    def get_color_class(percentage):
        if percentage < 40:
            return "bg-red-500"  # Low
        elif percentage < 60:
            return "bg-yellow-500"  # Medium
        else:
            return "bg-green-500"  # High

    def get_color_description(percentage):
        if percentage < 40:
            return "Less than 40%"
        elif percentage < 60:
            return "> 40% < 60%"
        else:
            return "> 60%"
    
    # Process the percentage values and add color class and color description
    joint_advocacy_data = [
        {
            'districts': district,
            "percentage": val,
            "color_class": get_color_class(val),
            "color_description": get_color_description(val),
        }
        for district, val in zip(joint_advocacy_districts, joint_advocacy_values)
    ]
    
    
    
    ##############Joint Advocacy Section End#########################

    
    context = {
        'values_alot_somewhat': values_alot_somewhat,
        'values_justalittle_notatall': values_justalittle_notatall,
        'keys_alot_somewhat': keys_alot_somewhat,
        
        'maternal_mortality_year_values': maternal_mortality_year_values,
        'maternal_mortality_years': maternal_mortality_years,
        
        'maternal_mortality_districts': maternal_mortality_districts,
        'maternal_mortality_district_values': maternal_mortality_district_values,
        
        'infant_mortality_years': infant_mortality_years,
        'infant_mortality_year_values': infant_mortality_year_values,
        
        'infant_mortality_districts': infant_mortality_districts,
        'infant_mortality_district_values': infant_mortality_district_values,
        
        'npse_district_values':npse_district_values,
        'npse_districts':npse_districts,

        'stability_districts':stability_districts,
        'div_data': div_data,
        
        'avg_budget_2022': avg_budget_2022,
        
        'services': services,
        'bribery_data': bribery_data,
        
        'audit_data':audit_data,
        
        'misuse_data':misuse_data,
        
        'satisfaction_services': satisfaction_services,
        'satisfaction_services_data': satisfaction_services_data,
        
        'lc_budget_data':lc_budget_data,
        
        'lc_projects_data':lc_projects_data,
        
        'joint_advocacy_data':joint_advocacy_data,
        
    }
    
    return render(request, 'index.html', context)
