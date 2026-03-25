from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('projects/', views.projects_view, name='projects'),
    path('projects/research/', views.research_projects_view, name='research_projects'),
    path('projects/consultancy/', views.consultancy_projects_view, name='consultancy_projects'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    path('team/', views.team_view, name='team'),
    path('learn/', views.learn_view, name='learn'),
    path('impact/', views.impact_view, name='impact'),
    # path('contact/', views.contact_view, name='contact'),  # Contact form moved to footer
    path('research-technology/', views.research_technology_view, name='research_technology'),
    path('workshops/', views.workshops_view, name='workshops'),
    path('tutorials/', views.tutorials_view, name='tutorials'),
]
