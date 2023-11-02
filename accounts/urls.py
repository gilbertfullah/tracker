from django.urls import path
from . import views
from .views import AssignmentCreateView
from django.contrib.auth.views import LoginView

urlpatterns=[
     path('register/', views.register, name='register'),
     path('login/', LoginView.as_view(template_name='login.html'), name='login'),
     path('logout/', views.logout_view, name='logout'),
     
     path('local_council_dashboard/', views.local_council_dashboard, name='local_council_dashboard'),
     
     path('local-council/profile/<int:id>/', views.local_council_profile, name='local_council_profile'),
     path('district_cso/profile/<int:id>/', views.district_cso_profile, name='district_cso_profile'),
     path('mda/profile/<int:id>/', views.mda_profile, name='mda_profile'),
     path('mlgrd/profile/<int:id>/', views.mlgrd_profile, name='mlgrd_profile'),

     path('register/local-council/', views.local_council_register, name='local_council_register'),
     path('register/mda/', views.mda_register, name='mda_register'),
     path('register/district-cso/', views.district_cso_register, name='district_cso_register'),
     path('register/mlgrd/', views.mlgrd_register, name='mlgrd_register'),
     
     path('indicator-assignment/create/', AssignmentCreateView.as_view(), name='assignment_create'),
     path('indicator-assignment/success/', views.assignment_success, name='assignment_success'),
     
     path('assigned-indicators/', views.assigned_indicators, name='assigned_indicators'),
     
     path('get_notifications/', views.get_notifications, name='get_notifications'),
]

