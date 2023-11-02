from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect, render, get_object_or_404, HttpResponse
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.contrib.auth.forms import AuthenticationForm
from .forms import LocalCouncilRegisterForm, DistrictCSORegisterForm, MDARegisterForm, MLGRDRegisterForm, AssignmentForm
from .models import LocalCouncil, DistrictCSO, MDA, MLGRD, Assignment, Role, Notification
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.core.paginator import Paginator
import os
from django.conf import settings
import calendar
from django.db.models.functions import ExtractMonth, ExtractHour, ExtractDay
from django.db.models import Count, CharField, Value
from datetime import timedelta
from django.utils import timezone
from django.db.models.functions import TruncDate, Cast
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic.edit import CreateView
from indicators.models import IndicatorData
from .signals import send_notification_on_assignment




def register(request):
    selected_card = request.GET.get('selected_card', None)  # Get the selected card from the request

    # Check if the selected card is valid
    valid_cards = ['local_council', 'district_cso', 'mda', 'mlgrd']
    if selected_card not in valid_cards:
        selected_card = None  # Reset selected_card if it's not valid

    context = {'selected_card': selected_card}
    return render(request, 'register.html', context)

@login_required
def local_council_profile(request, id):
    local_council = get_object_or_404(LocalCouncil, id=id)
    assigned_indicators = Assignment.objects.filter(assigned_to=request.user)
    
    if request.user.is_authenticated:
    
        context = {
            'local_council': local_council,
            'assigned_indicators': assigned_indicators
        }
    
        return render(request, 'local_council_profile.html', context)
    else:
        return render(request, 'login.html')
    
@login_required
def district_cso_profile(request, id):
    district_cso = get_object_or_404(DistrictCSO, id=id)
    assigned_indicators = Assignment.objects.filter(assigned_to=request.user)
    
    if request.user.is_authenticated:
    
        context = {
            'district_cso': district_cso,
            'assigned_indicators': assigned_indicators
        }
    
        return render(request, 'district_cso_profile.html', context)
    else:
        return render(request, 'login.html')

@login_required
def mda_profile(request, id):
    mda = get_object_or_404(MDA, id=id)
    assigned_indicators = Assignment.objects.filter(assigned_to=request.user)
    
    if request.user.is_authenticated:
    
        context = {
            'mda': mda,
            'assigned_indicators': assigned_indicators
        }
    
        return render(request, 'mda_profile.html', context)
    else:
        return render(request, 'login.html')
    
@login_required
def mlgrd_profile(request, id):
    mlgrd = get_object_or_404(MLGRD, id=id)
    assigned_indicators = Assignment.objects.filter(assigned_to=request.user)
    
    if request.user.is_authenticated:
    
        context = {
            'mlgrd': mlgrd,
            'assigned_indicators': assigned_indicators
        }
    
        return render(request, 'mlgrd_profile.html', context)
    else:
        return render(request, 'login.html')
    
@login_required
def local_council_dashboard(request):
    return render(request, 'local_council_dashboard.html')
    



def local_council_register(request):
    if request.method == "POST":
        form = LocalCouncilRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            username = user.username  # Get the username from the user instance
            messages.success(request, f"{username} was successfully registered")
            login(request, user)  # Pass the user instance to the login function
            return redirect('/')
        else:
            messages.error(request, "Form is not valid")
    else:
        form = LocalCouncilRegisterForm()

    context = {'form': form}
    return render(request, 'local_council.html', context)


def district_cso_register(request):
    if request.method == "POST":
        form = DistrictCSORegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f"{user} was successfully registered")
            return redirect("profile")
    else:
        form = DistrictCSORegisterForm()
        messages.error(request, "Form is not valid")
        context = {'form':form}
        return render(request, 'district_cso.html', context)

    return render(request, 'district_cso.html', {'form':form})

def mda_register(request):
    if request.method == "POST":
        form = MDARegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f"{user} was successfully registered")
            return redirect("profile")
    else:
        form = MDARegisterForm()
        messages.error(request, "Form is not valid")
        context = {'form':form}
        return render(request, 'mda.html', context)

    return render(request, 'mda.html', {'form':form})


def mlgrd_register(request):
    if request.method == "POST":
        form = MLGRDRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, f"{user} was successfully registered")
            return redirect("profile")
    else:
        form = MLGRDRegisterForm()
        messages.error(request, "Form is not valid")
        context = {'form':form}
        return render(request, 'mlgrd.html', context)

    return render(request, 'mlgrd.html', {'form':form})

def login_request(request):

        
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                    # Determine the appropriate redirect URL based on user type
                if user.is_local_council:
                    return redirect('local_council_profile')
                elif user.is_district_cso:
                    return redirect('profile')
                elif user.is_mda:
                    return redirect('profile')
                elif user.is_mlgrd:
                    return redirect('profile')

            else:
                messages.error(request,"Invalid username or password")
        else:
            messages.error(request,"Invalid username or password")
    form = AuthenticationForm()
    return render(request, 'login.html', {'form':form})

def logout_view(request):
    logout(request)
    return redirect('/')

def assignment_success(request):
    messages.success(request, 'Indicator Assignment created successfully!')
    return render(request, 'assignment_success.html')

def assign_indicator(request, indicator_id):
    user = request.user
    user_district = None
    user_account_type = None

    # Determine the user's account type and district
    if hasattr(user, 'local_council'):
        user_account_type = 'LocalCouncil'
        user_district = user.local_council.district
    elif hasattr(user, 'district_cso'):
        user_account_type = 'DistrictCSO'
        user_district = user.district_cso.district
    elif hasattr(user, 'mda'):
        user_account_type = 'MDA'
        user_district = user.mda.district
    elif hasattr(user, 'mlgrd'):
        user_account_type = 'MLGRD'
        user_district = user.mlgrd.district
    # Add similar code for MDA and MLGRD

    try:
        indicator = IndicatorData.objects.get(pk=indicator_id)
    except IndicatorData.DoesNotExist:
        # Handle the case where the indicator doesn't exist
        return redirect('indicator_list')

    if indicator.district == user_district:
        if user_account_type in ['LocalCouncil', 'DistrictCSO', 'MDA', 'MLGRD']:
            if request.method == 'POST':
                # Process the assignment form
                form = AssignmentForm(request.POST)
                if form.is_valid():
                    assignment = form.save(commit=False)
                    assignment.assigned_to = user
                    assignment.save()
                    # Redirect to a success page or show a success message
                    return redirect('indicator_list')
            else:
                form = AssignmentForm()

            return render(request, 'assign_indicator.html', {'form': form, 'indicator': indicator})
        else:
            error_message = "You do not have permission to manage indicators."
            return render(request, 'error_page.html', {'error_message': error_message})
    else:
        error_message = "You can only manage indicators in your own district."
        return render(request, 'error_page.html', {'error_message': error_message})

class AssignmentCreateView(CreateView):
    model = Assignment
    form_class = AssignmentForm
    template_name = 'indicator_assignment.html'
    
    @login_required  # Add this decorator if the view requires authentication
    def form_valid(self, form):
        # Assign the current user (assigned_by) to the assignment
        form.instance.assigned_by = self.request.user
        
        # Additional logic to create the assignment, e.g., calling save() on the form
        form.save()
        
        # Trigger the notification signal to inform the user
        send_notification_on_assignment(sender=Assignment, instance=form.instance)
        
        # Add a success message
        messages.success(self.request, 'Indicator Assignment created successfully!')
        
        # Redirect to the success view
        return HttpResponseRedirect(reverse('assignment_success'))
    
    
def assigned_indicators(request):
    
    # Retrieve indicators assigned to the logged-in user
    #user_district = request.user.is_local_council.district  # Get the current user
    assigned_indicators = Assignment.objects.filter(assigned_to=request.user)

    return render(request, 'assigned_indicators.html', {'assigned_indicators': assigned_indicators})
    
# Define a custom user check function
def can_post_update_indicator_data(user, indicator_id):
    try:
        assignment = Assignment.objects.get(indicator_id=indicator_id, assigned_to=user)
        return user.role.name == 'Reactor'
    except (Assignment.DoesNotExist, Role.DoesNotExist):
        return False
    

@login_required
def get_notifications(request):
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:10]  # Get the latest 10 notifications
    notifications_data = [{'id': n.id, 'message': n.message, 'is_read': n.is_read, 'created_at': n.created_at} for n in notifications]
    
    # Calculate the total number of unread notifications
    unread_count = len([n for n in notifications if not n.is_read])
    
    return JsonResponse({'notifications': notifications_data})