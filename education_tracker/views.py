from django.shortcuts import render
from schools.models import School, District, ServiceType
from django.db.models import Avg
from django.db.models import Count, F, ExpressionWrapper, FloatField
from decimal import Decimal
from indicators.models import IndicatorData, CitizenPrioritiesData, CitizenPrioritiesData, TrustInLocalAuthorities, NPSEResults, CommunityStability, \
    BudgetAllocation, BriberyReductionData
from datetime import datetime
import json
from django.db.models.functions import ExtractYear

def index(request):
    ##############Trust Section Start##################
    # Define the target answer_choice and date_submitted values
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
    
    stability_a_little_bit = data_values[1]
    stability_not_at_all = data_values[2]
    stability_somewhat = data_values[3]
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
    
    avg_audit_recommendation = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=audit_recommendation_indicator).
                    aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_audit_recommendation = round(avg_audit_recommendation, 0)
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_audit_recommendation):
        if avg_audit_recommendation <= 230:
            return 'red', 'down'
        elif 231 <= avg_audit_recommendation <= 240:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    audit_recommendation_color, audit_recommendation_arrow = get_color_and_arrow(avg_audit_recommendation)
    
    audit_base_query = (IndicatorData.objects.values('district__name').annotate(avg=Avg('indicator_value')).order_by('avg'))
        
    data_by_audit_recommendations = {}
    audit_district_names = []
    
    # Now, base_query contains the average indicator_value for each district based on answer_choice_comm_stability.
    for result in base_query:
        audit_district_names.append(result['district__name'])
        average_value = float(result['avg'])

        # Create or update the dataset for each trust choice
        if audit_district_names not in data_by_audit_recommendations:
            data_by_audit_recommendations[audit_district_names] = {
                'label': audit_district_names,
                'data': [],
            }

        data_by_audit_recommendations[audit_district_names]['data'].append(average_value)

    # Prepare the data for the chart
    audit_labels = list(set(data['label'] for data in data_by_audit_recommendations.values()))
    audit_datasets = list(data_by_audit_recommendations.values())
    
    audit_data_values = [entry['data'] for entry in datasets]
    
    audit_falaba = data_values[1]
    stability_not_at_all = data_values[2]
    stability_somewhat = data_values[3]
    stability_very_much = data_values[4]
    
    ##############Audit Recommendation Section End#########################
    
    ##############LC Revenue Misuse Section Start#########################
    
    # Calculate the average indicator_value for all districts where status is approved
    audit_lc_misuse = f"% Reduction in citizens who believe local councils misuse revenue"
    
    avg_lc_misuse = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=audit_lc_misuse).
                    aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_lc_misuse = round(avg_lc_misuse, 0)
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_lc_misuse):
        if avg_lc_misuse <= 230:
            return 'red', 'down'
        elif 231 <= avg_lc_misuse <= 240:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    lc_misuse_color, lc_misuse_arrow = get_color_and_arrow(avg_lc_misuse)
    
    
    # Calculate the average indicator_value for all districts where status is approved
    lc_budget_indicator = f"% of citizens who are aware of local council budget"
    
    avg_lc_budget = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=lc_budget_indicator).
                    aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_lc_budget = round(avg_lc_budget, 0)
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_lc_budget):
        if avg_lc_budget <= 230:
            return 'red', 'down'
        elif 231 <= avg_lc_budget <= 240:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    lc_budget_color, lc_budget_arrow = get_color_and_arrow(avg_lc_budget)
    
    
    # Calculate the average indicator_value for all districts where status is approved
    lc_project_indicator = f"% of citizens who are aware of local council projects"
    
    avg_lc_project = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=lc_project_indicator).
                    aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_lc_project = round(avg_lc_project, 0)
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_lc_project):
        if avg_lc_project <= 230:
            return 'red', 'down'
        elif 231 <= avg_lc_project <= 240:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    lc_project_color, lc_project_arrow = get_color_and_arrow(avg_lc_project)
    
    
    # Define color and arrow direction based on the average values
    lc_budget_color, lc_budget_arrow = get_color_and_arrow(avg_lc_budget)
    
    
    # Calculate the average indicator_value for all districts where status is approved
    joint_advocacy_indicator = f"Number of joint advocacy initiatives implemented by LCs and CSOs"
    
    avg_joint_advocacy = Decimal(IndicatorData.objects.filter(status='approved', indicator__name=joint_advocacy_indicator).
                    aggregate(Avg('indicator_value'))['indicator_value__avg'] or 0)
    avg_joint_advocacy = round(avg_joint_advocacy, 0)
    
    # Define color and arrow direction based on the average values
    def get_color_and_arrow(avg_joint_advocacy):
        if avg_joint_advocacy <= 230:
            return 'red', 'down'
        elif 231 <= avg_joint_advocacy <= 240:
            return 'orange', 'right'
        else:
            return 'green', 'up'
    
    # Define color and arrow direction based on the average values
    joint_advocacy_color, joint_advocacy_arrow = get_color_and_arrow(avg_joint_advocacy)

    
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
        
        'avg_audit_recommendation':avg_audit_recommendation,
        'audit_recommendation_color':audit_recommendation_color,
        'audit_recommendation_arrow':audit_recommendation_arrow,
        
        'avg_lc_misuse':avg_lc_misuse,
        'lc_misuse_color':lc_misuse_color,
        'lc_misuse_arrow':lc_misuse_arrow,
        
        'avg_lc_budget':avg_lc_budget,
        'lc_budget_color':lc_budget_color,
        'lc_budget_arrow':lc_budget_arrow,
        
        'avg_lc_project':avg_lc_project,
        'lc_project_color':lc_project_color,
        'lc_project_arrow':lc_project_arrow,
        
        'avg_joint_advocacy':avg_joint_advocacy,
        'joint_advocacy_color':joint_advocacy_color,
        'joint_advocacy_arrow':joint_advocacy_arrow,
        
    }
    
    return render(request, 'index.html', context)
