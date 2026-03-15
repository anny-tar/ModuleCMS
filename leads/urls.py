from django.urls import path
from . import views

urlpatterns = [
    path('leads/submit/<int:section_id>/', views.submit_form, name='submit_form'),
    path('leads/thanks/',                  views.thanks,       name='leads_thanks'),
]