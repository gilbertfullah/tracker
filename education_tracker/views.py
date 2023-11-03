from django.shortcuts import render
from schools.models import School, District, ServiceType
from django.db.models import Avg, Sum
from django.db.models import Count, F, ExpressionWrapper, FloatField
from decimal import Decimal
from indicators.models import IndicatorData, CitizenPrioritiesData, CitizenPrioritiesData, TrustInLocalAuthorities, NPSEResults, CommunityStability, \
    BudgetAllocation, BriberyReductionData
from datetime import datetime
import json
from django.db.models.functions import ExtractYear

def index(request):
    ##############Trust Section Start##################
    trust_indicator = f"% increase in citizen’s trust in local authorities"
    target_choice = 'A lot'
    target_date_2018 = datetime(2018, 10, 25)
    target_date_2020 = datetime(2020, 10, 25)
    target_date_2022 = datetime(2022, 10, 25)

    # Calculate the average indicator_value for each target
    avg_2018 = Decimal(IndicatorData.objects.filter(answer_choice_trust=target_choice, date_submitted=target_date_2018, status='approved', indicator__name=trust_indicator).
                    aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_2018 = round(avg_2018, 2)
    
    avg_2020 = Decimal(IndicatorData.objects.filter(answer_choice_trust=target_choice, date_submitted=target_date_2020, status='approved', indicator__name=trust_indicator).
                    aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_2020 = round(avg_2020, 2)

    avg_2022 = Decimal(IndicatorData.objects.filter(answer_choice_trust=target_choice, date_submitted=target_date_2022, status='approved', indicator__name=trust_indicator).
                    aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_2022 = round(avg_2022, 2) 

    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_value):
        if avg_value <= 34:
            return 'red', 'down'
        elif 35 <= avg_value <= 49:
            return 'orange', 'right'
        else:
            return 'green', 'up'

    color_2018, arrow_2018 = get_color_and_arrow(avg_2018)
    color_2020, arrow_2020 = get_color_and_arrow(avg_2020)
    color_2022, arrow_2022 = get_color_and_arrow(avg_2022)
    
    # Query the data and calculate average indicator values for each trust choice
    indicator_values = IndicatorData.objects.values('answer_choice_trust', year=ExtractYear('date_submitted')).annotate(avg=Avg('indicator_value')).order_by('year', 'avg')
    
    trust_years = []
    
    y = IndicatorData.objects.values(year=ExtractYear('date_submitted')).distinct().order_by('year')
    for i in y:
        trust_years.append(i['year'])
        

    # Initialize dictionaries to store the data
    data_by_trust_choice = {}
    
        

    for values in indicator_values:
        #years.append(values['year'])
        trust_choice = values['answer_choice_trust']
        avg_value = float(values['avg'])  # Extract the numeric value

        # Create or update the dataset for each trust choice
        if trust_choice not in data_by_trust_choice:
            data_by_trust_choice[trust_choice] = {
                'label': trust_choice,
                'data': [],
            }

        data_by_trust_choice[trust_choice]['data'].append(avg_value)

    # Prepare the data for the chart
    labels = list(set(data['label'] for data in data_by_trust_choice.values()))
    datasets = list(data_by_trust_choice.values())
    
    data_values = [entry['data'] for entry in datasets]
    
    not_at_all = data_values[0][:3]
    just_a_little = data_values[1]
    a_lot = data_values[2]
    somewhat = data_values[3]
    
    ##############Trust Section End##################
    
    ##############Maternal Mortality Section Start##################
    
    maternal_mortality_indicator = f"% reduction in maternal mortality by district"
    
    avg_maternal_mortality = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=maternal_mortality_indicator).
                    aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_maternal_mortality = round(avg_maternal_mortality, 2)
    
    def get_color_and_arrow(avg_maternal_mortality):
        if avg_maternal_mortality <= 34:
            return 'red', 'down'
        elif 35 <= avg_maternal_mortality <= 49:
            return 'orange', 'right'
        else:
            return 'green', 'up'

    maternal_mortality_color, maternal_mortality_arrow_2018 = get_color_and_arrow(avg_maternal_mortality)
    
    maternal_mortality = IndicatorData.objects.filter(indicator__name=maternal_mortality_indicator)
    
    maternal_mortality_indicator_values = IndicatorData.objects.filter(indicator__name=maternal_mortality_indicator). \
                                        values('indicator__name', year=ExtractYear('date_submitted')).annotate(avg_value=Avg('indicator_value')). \
                                        order_by('year', 'indicator__name')
                                        
    distinct_years = maternal_mortality_indicator_values.values_list('year', flat=True).distinct()
    
    chart_data = {
    'labels': list(distinct_years),
    'datasets': [
        {
            'label': 'Average Indicator Value',
            'data': list(maternal_mortality_indicator_values.values_list('avg_value', flat=True)),
        },
    ],
    }
    
    print(maternal_mortality_indicator_values)
    print(maternal_mortality)
        
    ##############Maternal Mortality Section End##################
    
    ##############NPSE Section Start##################
    
    # Calculate the average indicator_value for all districts where status is approved
    npse_indicator = f"% increase learning outcomes as reflected in the NPSE scores in focused districts"
    
    avg_npse_values = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=npse_indicator).
                    aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_npse_values = round(avg_npse_values, 0)
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_npse_values):
        if avg_npse_values <= 230:
            return 'red', 'down'
        elif 231 <= avg_npse_values <= 240:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    npse_color, npse_arrow = get_color_and_arrow(avg_npse_values)
    
    indicator_name = f'% increase learning outcomes as reflected in the NPSE scores in focused districts'
    
    district_avg_values = (IndicatorData.objects.filter(indicator__name=indicator_name, status='approved').values('district__name').annotate(avg=Avg('indicator_value')).order_by('avg'))
    
    district_name = []
    average_value = []
    # Now, `district_avg_values` contains the average indicator_value for each district.
    for result in district_avg_values:
        district_name.append(result['district__name'])
        average_value.append(float(result['avg']))
        
    karene_npse = average_value[0]
    moyamba_npse = average_value[1]
    kono_npse = average_value[2]
    tonkolili_npse = average_value[3]
    war_npse = average_value[4]
    falaba_npse = average_value[5]
        
    ##############NPSE Section End##################
    
    ##############Stability Section Start##################
    
    # Define the target answer_choice and date_submitted values
    target_answer_choice = 'Very much'

    # Calculate the average indicator_value for each target
    avg_com_stability = Decimal(IndicatorData.objects.filter(answer_choice_comm_stability=target_answer_choice, status='approved').
                                aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_com_stability = round(avg_com_stability, 2)


    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_com_stability):
        if avg_com_stability <= 34:
            return 'red', 'down'
        elif 35 <= avg_com_stability <= 49:
            return 'orange', 'right'
        else:
            return 'green', 'up'

    stability_color, stability_arrow = get_color_and_arrow(avg_com_stability)
    
    # Get the selected district from the URL parameter or use None if not provided
    district_id = request.GET.get('district')
    
    # Get all available districts for the filter dropdown
    districts = District.objects.all()
    
    base_query = (IndicatorData.objects.values('answer_choice_comm_stability', 'district__name').annotate(avg=Avg('indicator_value')).order_by('district', 'avg'))
    
    if district_id:
        # Filter the query by the selected district if provided
        base_query = base_query.filter(district=district_id)
        
    data_by_answer_choice = {}
    stability_district_names = []
    
    # Now, base_query contains the average indicator_value for each district based on answer_choice_comm_stability.
    for result in base_query:
        comm_stability = result['answer_choice_comm_stability']
        stability_district_names.append(result['district__name'])
        average_value = float(result['avg'])

        # Create or update the dataset for each trust choice
        if comm_stability not in data_by_answer_choice:
            data_by_answer_choice[comm_stability] = {
                'label': comm_stability,
                'data': [],
            }

        data_by_answer_choice[comm_stability]['data'].append(average_value)

    # Prepare the data for the chart
    labels = list(set(data['label'] for data in data_by_answer_choice.values()))
    datasets = list(data_by_answer_choice.values())
    
    data_values = [entry['data'] for entry in datasets]
    
    print(labels)
    print(data_values)
    
    stability_a_little_bit = data_values[0]
    stability_not_at_all = data_values[1]
    stability_somewhat = data_values[2]
    stability_very_much = data_values[4]
    
    ##############Stability Section End##################
    
    ##############Budget Section Start##################
    
    # Define the target answer_choice and date_submitted values
    budget_indicator = f"% of budget allocated to devolved functions"
    
    budget_date_2020 = datetime(2020, 10, 29)
    budget_date_2021 = datetime(2021, 10, 29)
    budget_date_2022 = datetime(2022, 10, 29)

    # Calculate the average indicator_value for each target
    avg_budget_2020 = Decimal(IndicatorData.objects.filter(date_submitted=budget_date_2020, status='approved', indicator__name=budget_indicator).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_budget_2020 = round(avg_budget_2020, 2)
    
    avg_budget_2021 = Decimal(IndicatorData.objects.filter(date_submitted=budget_date_2021, status='approved', indicator__name=budget_indicator).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_budget_2021 = round(avg_budget_2021, 2)

    avg_budget_2022 = Decimal(IndicatorData.objects.filter(date_submitted=budget_date_2022, status='approved', indicator__name=budget_indicator).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_budget_2022 = round(avg_budget_2022, 2) 

    # Define color and arrow direction based on the average values
    def get_color_and_arrow(budget_avg_value):
        if budget_avg_value <= 34:
            return 'red', 'down'
        elif 35 <= budget_avg_value <= 49:
            return 'orange', 'right'
        else:
            return 'green', 'up'

    budget_color_2020, budget_arrow_2020 = get_color_and_arrow(avg_budget_2020)
    budget_color_2021, budget_arrow_2021 = get_color_and_arrow(avg_budget_2021)
    budget_color_2022, budget_arrow_2022 = get_color_and_arrow(avg_budget_2022)
    
    ##############Budget Section End#########################
    
    ##############Bribery Section Start#########################

    target_date_2018 = datetime(2018, 10, 30)
    target_date_2020 = datetime(2020, 10, 30)
    target_date_2022 = datetime(2022, 10, 30)
    
    bribery_medical_service = "Medical services"
    bribery_public_service = "Public school"
    bribery_identity_service = "Identity documents"
    
    avg_bribery_medical_service = Decimal(IndicatorData.objects.filter(bribery_services=bribery_medical_service, status='approved', date_submitted=target_date_2018).
                                aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_bribery_medical_service  = round(avg_bribery_medical_service, 2)
    
    avg_bribery_public_service = Decimal(IndicatorData.objects.filter(bribery_services=bribery_public_service, status='approved', date_submitted=target_date_2018).
                                aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_bribery_public_service  = round(avg_bribery_public_service, 2)
    
    avg_bribery_identity_service = Decimal(IndicatorData.objects.filter(bribery_services=bribery_identity_service, status='approved', date_submitted=target_date_2018).
                                aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_bribery_identity_service  = round(avg_bribery_identity_service, 2)

    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_bribery_service):
        if avg_bribery_service <= 34:
            return 'red', 'down'
        elif 35 <= avg_bribery_service <= 49:
            return 'orange', 'right'
        else:
            return 'green', 'up'

    bribery_medical_service_color, bribery_medical_service_arrow = get_color_and_arrow(avg_bribery_medical_service)
    bribery_public_service_color, bribery_public_service_arrow = get_color_and_arrow(avg_bribery_public_service)
    bribery_identity_service_color, bribery_identity_service_arrow = get_color_and_arrow(avg_bribery_identity_service)
    
    # Query the data and calculate average indicator values for each trust choice
    bribery_services_indicator_values = IndicatorData.objects.values('bribery_services', year=ExtractYear('date_submitted')).annotate(avg=Avg('indicator_value')).order_by('year', 'avg')
    
    bribery_years = []
    
    ye = IndicatorData.objects.values(year=ExtractYear('date_submitted')).distinct().order_by('year')
    for i in ye:
        bribery_years.append(i['year'])

    # Initialize dictionaries to store the data
    data_by_bribery_services = {}

    for values in bribery_services_indicator_values:
        #years.append(values['year'])
        bribery_services = values['bribery_services']
        avg_value = float(values['avg'])  # Extract the numeric value

        # Create or update the dataset for each trust choice
        if bribery_services not in data_by_bribery_services:
            data_by_bribery_services[bribery_services] = {
                'label': bribery_services,
                'data': [],
            }

        data_by_bribery_services[bribery_services]['data'].append(avg_value)

    # Prepare the data for the chart
    labels = list(set(data['label'] for data in data_by_bribery_services.values()))
    datasets = list(data_by_bribery_services.values())
    
    data_values = [entry['data'] for entry in datasets]
    
    medical_services = data_values[1]
    public_school_services = data_values[2]
    identity_documents_services = data_values[3]

    
    ##############Bribery Section End#########################
    
    
    ##############Media Section Start#########################
    
    # Define the target answer_choice and date_submitted values
    media_outlet = 'Radio'

    # Calculate the average indicator_value for each target
    avg_media_outlet = Decimal(IndicatorData.objects.filter(media_outlets=media_outlet, status='approved').
                                aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_media_outlet  = round(avg_media_outlet, 2)


    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_media_outlet):
        if avg_media_outlet <= 34:
            return 'red', 'down'
        elif 35 <= avg_media_outlet <= 49:
            return 'orange', 'right'
        else:
            return 'green', 'up'

    media_outlet_color, media_outlet_arrow = get_color_and_arrow(avg_media_outlet)
    
    media_outlets_indicator_values = IndicatorData.objects.values('media_outlets').annotate(avg=Avg('indicator_value')).order_by('avg')
    
    # Initialize dictionaries to store the data
    data_by_media_outlets = {}

    for values in media_outlets_indicator_values:
        #years.append(values['year'])
        media_outlets = values['media_outlets']
        avg_value = float(values['avg'])  # Extract the numeric value

        # Create or update the dataset for each trust choice
        if media_outlets not in data_by_media_outlets:
            data_by_media_outlets[media_outlets] = {
                'label': media_outlets,
                'data': [],
            }

        data_by_media_outlets[media_outlets]['data'].append(avg_value)

    # Prepare the data for the chart
    media_labels = list(set(data['label'] for data in data_by_media_outlets.values()))
    media_outlets_datasets = list(data_by_media_outlets.values())
    
    media_outlets_data_values = [entry['data'] for entry in media_outlets_datasets]
    
    notice_board = media_outlets_data_values[7]
    radio = media_outlets_data_values[6]
    local_online = media_outlets_data_values[0]
    print_newspaper = media_outlets_data_values[2]
    whatsapp = media_outlets_data_values[5]
    other_social_media = media_outlets_data_values[1]
    other = media_outlets_data_values[3]
    
    ##############Media Section End#########################
    
    ##############Audit Recommendation Section Start#########################
    
    # Calculate the average indicator_value for all districts where status is approved
    audit_recommendation_indicator = f'% increase in audit recommendations implemented by the councils'
    district_names_list = ['Falaba', 'Karene', 'Kono', 'Moyamba', 'Tonkolili', 'Western Rural Area']
    
    audit_indicator_values = IndicatorData.objects.filter(district__name__in=district_names_list, status='approved', indicator__name=audit_recommendation_indicator)
    
    audit_total_sum = audit_indicator_values.aggregate(Sum('indicator_value'))['indicator_value__sum'] or 0
    
    num_districts = len(district_names_list)
    if num_districts > 0:
        average = audit_total_sum / num_districts
        audit_average = round(average, 2)  # Optionally, round to two decimal places
    else:
        audit_average = 0 
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(audit_average):
        if audit_average <= 230:
            return 'red', 'down'
        elif 231 <= audit_average <= 240:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    audit_recommendation_color, audit_recommendation_arrow = get_color_and_arrow(audit_average)
        
    data_by_audit_recommendations = {}
    audit_district_names = []
    
    for district_name in district_names_list:
    # Your query to calculate the average indicator value for the current district
        avg_audit_recommendation = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=audit_recommendation_indicator, district__name=district_name).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)

        # Round the result if needed
        avg_audit_recommendation = round(avg_audit_recommendation, 0)
        
        avg_audit_recommendation = float(avg_audit_recommendation)

        audit_district_names.append(district_name)

        if district_name not in data_by_audit_recommendations:
            data_by_audit_recommendations[district_name] = {
                'label': district_name,
                'data': [],
            }

        data_by_audit_recommendations[district_name]['data'].append(avg_audit_recommendation)

    # Continue with your data processing and chart preparation
    audit_labels = list(set(data['label'] for data in data_by_audit_recommendations.values()))
    audit_datasets = list(data_by_audit_recommendations.values())

    audit_data_values = [entry['data'] for entry in audit_datasets]
    
    falaba_district = audit_data_values[0]
    karene_district = audit_data_values[1]
    kono_district = audit_data_values[2]
    moyamba_district = audit_data_values[3]
    tonkolili_district = audit_data_values[4]
    wa_district = audit_data_values[5]
    
    ##############Audit Recommendation Section End#########################
    
    ##############LC Revenue Misuse Section Start#########################
    
    # Calculate the average indicator_value for all districts where status is approved
    audit_lc_misuse = f"% Reduction in citizens who believe local councils misuse revenue"
    
    misuse_indicator_values = IndicatorData.objects.filter(district__name__in=district_names_list, status='approved', indicator__name=audit_lc_misuse)
    
    misuse_total_sum = misuse_indicator_values.aggregate(Sum('indicator_value'))['indicator_value__sum'] or 0
    
    num_districts = len(district_names_list)
    if num_districts > 0:
        average = misuse_total_sum / num_districts
        misuse_average = round(average, 2)  # Optionally, round to two decimal places
    else:
        misuse_average = 0 
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(misuse_average):
        if misuse_average <= 230:
            return 'red', 'down'
        elif 231 <= misuse_average <= 240:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    lc_misuse_color, lc_misuse_arrow = get_color_and_arrow(misuse_average)
    
    data_by_lc_misuse = {}
    lc_misuse_district_names = []
    
    for district_name in district_names_list:
    # Your query to calculate the average indicator value for the current district
        avg_lc_misuse = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=audit_lc_misuse, district__name=district_name).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)

        # Round the result if needed
        avg_lc_misuse = round(avg_lc_misuse, 0)
        
        avg_lc_misuse = float(avg_lc_misuse)

        lc_misuse_district_names.append(district_name)

        if district_name not in data_by_lc_misuse:
            data_by_lc_misuse[district_name] = {
                'label': district_name,
                'data': [],
            }

        data_by_lc_misuse[district_name]['data'].append(avg_lc_misuse)

    # Continue with your data processing and chart preparation
    lc_misuse_labels = list(set(data['label'] for data in data_by_lc_misuse.values()))
    lc_misuse_datasets = list(data_by_lc_misuse.values())

    lc_misuse_data_values = [entry['data'] for entry in lc_misuse_datasets]
    
    falaba_misuse = lc_misuse_data_values[0]
    karene_misuse = lc_misuse_data_values[1]
    kono_misuse = lc_misuse_data_values[2]
    moyamba_misuse = lc_misuse_data_values[3]
    tonkolili_misuse = lc_misuse_data_values[4]
    wa_misuse = lc_misuse_data_values[5]
    
    ##############LC Revenue Misuse Section End#########################
    
    ##############LC Budget Section Start#########################
    
    # Calculate the average indicator_value for all districts where status is approved
    lc_budget_indicator = f"% of citizens who are aware of local council budget"
    
    lc_budget_indicator_values = IndicatorData.objects.filter(district__name__in=district_names_list, status='approved', indicator__name=lc_budget_indicator)
    
    lc_budget_total_sum = lc_budget_indicator_values.aggregate(Sum('indicator_value'))['indicator_value__sum'] or 0
    
    num_districts = len(district_names_list)
    if num_districts > 0:
        average = lc_budget_total_sum / num_districts
        lc_budget_average = round(average, 2)  # Optionally, round to two decimal places
    else:
        lc_budget_average = 0 
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(lc_budget_average):
        if lc_budget_average <= 230:
            return 'red', 'down'
        elif 231 <= lc_budget_average <= 240:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    lc_budget_color, lc_budget_arrow = get_color_and_arrow(lc_budget_average)
    
    data_by_lc_budget = {}
    lc_budget_district_names = []
    
    for district_name in district_names_list:
    # Your query to calculate the average indicator value for the current district
        avg_lc_budget = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=lc_budget_indicator, district__name=district_name).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)

        # Round the result if needed
        avg_lc_budget = round(avg_lc_budget, 0)
        
        avg_lc_budget = float(avg_lc_budget)

        lc_budget_district_names.append(district_name)

        if district_name not in data_by_lc_budget:
            data_by_lc_budget[district_name] = {
                'label': district_name,
                'data': [],
            }

        data_by_lc_budget[district_name]['data'].append(avg_lc_budget)

    # Continue with your data processing and chart preparation
    lc_budget_labels = list(set(data['label'] for data in data_by_lc_budget.values()))
    lc_budget_datasets = list(data_by_lc_budget.values())

    lc_budget_data_values = [entry['data'] for entry in lc_budget_datasets]
    
    falaba_budget = lc_budget_data_values[0]
    karene_budget = lc_budget_data_values[1]
    kono_budget = lc_budget_data_values[2]
    moyamba_budget = lc_budget_data_values[3]
    tonkolili_budget = lc_budget_data_values[4]
    wa_budget = lc_budget_data_values[5]
    
    ##############LC Budget Section End#########################
    
    ##############LC Projects Section Start#########################

    lc_project_indicator = f"% of citizens who are aware of local council projects"
    
    lc_project_indicator_values = IndicatorData.objects.filter(district__name__in=district_names_list, status='approved', indicator__name=lc_project_indicator)
    
    lc_project_total_sum = lc_project_indicator_values.aggregate(Sum('indicator_value'))['indicator_value__sum'] or 0
    
    num_districts = len(district_names_list)
    if num_districts > 0:
        average = lc_project_total_sum / num_districts
        lc_project_average = round(average, 2)  # Optionally, round to two decimal places
    else:
        lc_project_average = 0 
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(lc_project_average):
        if lc_project_average <= 15:
            return 'red', 'down'
        elif 15 >= lc_project_average <= 18:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    lc_project_color, lc_project_arrow = get_color_and_arrow(lc_project_average)
    
    data_by_lc_project = {}
    lc_project_district_names = []
    
    for district_name in district_names_list:
    # Your query to calculate the average indicator value for the current district
        avg_lc_project = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=lc_project_indicator, district__name=district_name).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)

        # Round the result if needed
        avg_lc_project = round(avg_lc_project, 0)
        
        avg_lc_project = float(avg_lc_project)

        lc_project_district_names.append(district_name)

        if district_name not in data_by_lc_project:
            data_by_lc_project[district_name] = {
                'label': district_name,
                'data': [],
            }

        data_by_lc_project[district_name]['data'].append(avg_lc_project)

    # Continue with your data processing and chart preparation
    lc_project_labels = list(set(data['label'] for data in data_by_lc_project.values()))
    lc_project_datasets = list(data_by_lc_project.values())

    lc_project_data_values = [entry['data'] for entry in lc_project_datasets]
    
    falaba_project = lc_project_data_values[0]
    karene_project = lc_project_data_values[1]
    kono_project = lc_project_data_values[2]
    moyamba_project = lc_project_data_values[3]
    tonkolili_project = lc_project_data_values[4]
    wa_project = lc_project_data_values[5]
    

    ##############LC Projects Section End#########################
    
    ##############Joint Advocacy Section Start#########################

    joint_advocacy_indicator = f"Number of joint advocacy initiatives implemented by LCs and CSOs"
    
    joint_advocacy_indicator_values = IndicatorData.objects.filter(district__name__in=district_names_list, status='approved', indicator__name=joint_advocacy_indicator)
    
    joint_advocacy_total_sum = joint_advocacy_indicator_values.aggregate(Sum('indicator_value'))['indicator_value__sum'] or 0
    
    num_districts = len(district_names_list)
    if num_districts > 0:
        average = joint_advocacy_total_sum / num_districts
        joint_advocacy_average = round(average, 2)  # Optionally, round to two decimal places
    else:
        joint_advocacy_average = 0 
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(joint_advocacy_average):
        if joint_advocacy_average <= 50:
            return 'red', 'down'
        elif 51 >= joint_advocacy_average <= 60:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    joint_advocacy_color, joint_advocacy_arrow = get_color_and_arrow(joint_advocacy_average)
    
    data_by_joint_advocacy = {}
    joint_advocacy_district_names = []
    
    for district_name in district_names_list:
    # Your query to calculate the average indicator value for the current district
        avg_joint_advocacy = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=joint_advocacy_indicator, district__name=district_name).aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)

        # Round the result if needed
        avg_joint_advocacy = round(avg_joint_advocacy, 0)
        
        avg_joint_advocacy = float(avg_joint_advocacy)

        joint_advocacy_district_names.append(district_name)

        if district_name not in data_by_joint_advocacy:
            data_by_joint_advocacy[district_name] = {
                'label': district_name,
                'data': [],
            }

        data_by_joint_advocacy[district_name]['data'].append(avg_joint_advocacy)

    # Continue with your data processing and chart preparation
    joint_advocacy_labels = list(set(data['label'] for data in data_by_joint_advocacy.values()))
    joint_advocacy_datasets = list(data_by_joint_advocacy.values())

    joint_advocacy_data_values = [entry['data'] for entry in joint_advocacy_datasets]
    
    falaba_joint_advocacy = joint_advocacy_data_values[0]
    karene_joint_advocacy = joint_advocacy_data_values[1]
    kono_joint_advocacy = joint_advocacy_data_values[2]
    moyamba_joint_advocacy = joint_advocacy_data_values[3]
    tonkolili_joint_advocacy = joint_advocacy_data_values[4]
    wa_joint_advocacy = joint_advocacy_data_values[5]
    
    ##############Joint Advocacy Section End#########################

    
    context = {
        'avg_2018': avg_2018,
        'avg_2020': avg_2020,
        'avg_2022': avg_2022,
        'color_2018': color_2018,
        'color_2020': color_2020,
        'color_2022': color_2022,
        'arrow_2018': arrow_2018,
        'arrow_2020': arrow_2020,
        'arrow_2022': arrow_2022,
        'not_at_all': json.dumps(not_at_all),
        'just_a_little': json.dumps(just_a_little),
        'a_lot': json.dumps(a_lot),
        'somewhat': json.dumps(somewhat),
        'trust_years': json.dumps(trust_years),
        
        'avg_npse_values':avg_npse_values,
        'npse_color':npse_color,
        'npse_arrow':npse_arrow,
        'karene_npse': json.dumps(karene_npse),
        'moyamba_npse': json.dumps(moyamba_npse),
        'kono_npse': json.dumps(kono_npse),
        'tonkolili_npse': json.dumps(tonkolili_npse),
        'war_npse': json.dumps(war_npse),
        'falaba_npse': json.dumps(falaba_npse),
        
        'avg_com_stability':avg_com_stability,
        'stability_color':stability_color,
        'stability_arrow':stability_arrow,
        'stability_a_little_bit': json.dumps(stability_a_little_bit),
        'stability_not_at_all': json.dumps(stability_not_at_all),
        'stability_somewhat': json.dumps(stability_somewhat),
        'stability_very_much': json.dumps(stability_very_much),
        'stability_district_names': json.dumps(stability_district_names),
        
        'avg_budget_2020': avg_budget_2020,
        'avg_budget_2021': avg_budget_2021,
        'avg_budget_2022': avg_budget_2022,
        'budget_color_2020': budget_color_2020,
        'budget_color_2021': budget_color_2021,
        'budget_color_2022': budget_color_2022,
        'budget_arrow_2020': budget_arrow_2020,
        'budget_arrow_2021': budget_arrow_2021,
        'budget_arrow_2022': budget_arrow_2022,
        
        'avg_bribery_medical_service': avg_bribery_medical_service,
        'avg_bribery_public_service': avg_bribery_public_service,
        'avg_bribery_identity_service': avg_bribery_identity_service,
        'bribery_medical_service_color': bribery_medical_service_color,
        'bribery_public_service_color': bribery_public_service_color,
        'bribery_identity_service_color': bribery_identity_service_color,
        'bribery_medical_service_arrow': bribery_medical_service_arrow,
        'bribery_public_service_arrow': bribery_public_service_arrow,
        'bribery_identity_service_arrow': bribery_identity_service_arrow,
        'medical_services': medical_services,
        'public_school_services': public_school_services,
        'identity_documents_services': identity_documents_services,
        'bribery_years': bribery_years,
        
        'avg_media_outlet':avg_media_outlet,
        'media_outlet_color':media_outlet_color,
        'media_outlet_arrow':media_outlet_arrow,
        'notice_board': json.dumps(notice_board),
        'radio': json.dumps(radio),
        'local_online': json.dumps(local_online),
        'print_newspaper': json.dumps(print_newspaper),
        'whatsapp': json.dumps(whatsapp),
        'other_social_media': json.dumps(other_social_media),
        'other': json.dumps(other),
        
        'audit_average':audit_average,
        'audit_recommendation_color':audit_recommendation_color,
        'audit_recommendation_arrow':audit_recommendation_arrow,
        'wa_district': wa_district,
        'tonkolili_district': tonkolili_district,
        'moyamba_district': moyamba_district,
        'kono_district': kono_district,
        'karene_district': karene_district,
        'falaba_district': falaba_district,
        
        'misuse_average':misuse_average,
        'lc_misuse_color':lc_misuse_color,
        'lc_misuse_arrow':lc_misuse_arrow,
        'falaba_misuse': falaba_misuse,
        'karene_misuse': karene_misuse,
        'kono_misuse': kono_misuse,
        'moyamba_misuse': moyamba_misuse,
        'tonkolili_misuse': tonkolili_misuse,
        'wa_misuse': wa_misuse,
        
        'lc_budget_average':lc_budget_average,
        'lc_budget_color':lc_budget_color,
        'lc_budget_arrow':lc_budget_arrow,
        'falaba_budget': falaba_budget,
        'karene_budget': karene_budget,
        'kono_budget': kono_budget,
        'moyamba_budget': moyamba_budget,
        'tonkolili_budget': tonkolili_budget,
        'wa_budget': wa_budget,
        
        'lc_project_average':lc_project_average,
        'lc_project_color':lc_project_color,
        'lc_project_arrow':lc_project_arrow,
        'falaba_project': falaba_project,
        'karene_project': karene_project,
        'kono_project': kono_project,
        'moyamba_project': moyamba_project,
        'tonkolili_project': tonkolili_project,
        'wa_project': wa_project,
        
        'joint_advocacy_average':joint_advocacy_average,
        'joint_advocacy_color':joint_advocacy_color,
        'joint_advocacy_arrow':joint_advocacy_arrow,
        'falaba_joint_advocacy': falaba_joint_advocacy,
        'karene_joint_advocacy': karene_joint_advocacy,
        'kono_joint_advocacy': kono_joint_advocacy,
        'moyamba_joint_advocacy': moyamba_joint_advocacy,
        'tonkolili_joint_advocacy': tonkolili_joint_advocacy,
        'wa_joint_advocacy': wa_joint_advocacy,
        
    }
    
    return render(request, 'index.html', context)
