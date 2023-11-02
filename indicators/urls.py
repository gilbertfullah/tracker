from django.urls import path
from . import views

urlpatterns=[
    path('satisfaction-data-form/', views.satisfaction_data_form, name='satisfaction_data_form'),
    path('satisfaction-data-display/', views.satisfaction_indicator_view, name='satisfaction_data_display'),
    
    path('manage-indicator/<int:indicator_id>/', views.manage_indicator, name='manage_indicator'),
    
    path('trust-in-local-authorities/', views.citizen_priorities_view, name='trust_in_local_authorities'),
    
    path('indicator_list/', views.indicator_list, name='indicator_list'),
    
    path('indicator-detail/<int:indicator_id>/', views.indicator_detail, name='indicator_detail'),
    
    path('edit-indicator-data/<int:indicator_id>/', views.edit_indicator_data, name='edit_indicator_data'),

    path('add-indicator-data/<int:indicator_id>/', views.add_indicator_data, name='add_indicator_data'),
    
    path('delete-indicator/<int:indicator_id>/', views.delete_indicator, name='delete_indicator'),
    
    path('update-indicator-value/<int:id>/', views.update_indicator_value, name='update_indicator_value'),
]