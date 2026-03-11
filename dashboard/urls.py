from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from . import views


app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),

    # Supabase diagnostic (staff only)
    path('supabase-diagnostic/', views.supabase_test, name='supabase_test'),

    # Bulk Delete
    path('bulk-delete/', views.bulk_delete, name='bulk_delete'),

    # Projects CRUD
    path('projects/', views.projects_list, name='projects_list'),
    path('projects/add/', views.project_create, name='project_create'),
    path('projects/edit/<int:pk>/', views.project_edit, name='project_edit'),
    path('projects/delete/<int:pk>/', views.project_delete, name='project_delete'),
    
    # Publications CRUD
    path('publications/', views.publications_list, name='publications_list'),
    path('publications/add/', views.publication_create, name='publication_create'),
    path('publications/edit/<int:pk>/', views.publication_edit, name='publication_edit'),
    path('publications/delete/<int:pk>/', views.publication_delete, name='publication_delete'),
    path('publications/export/csv/', views.publication_export_csv, name='publication_export_csv'),
    
    # Team CRUD
    path('team/', views.team_list, name='team_list'),
    path('team/add/', views.team_create, name='team_create'),
    path('team/edit/<int:pk>/', views.team_edit, name='team_edit'),
    path('team/delete/<int:pk>/', views.team_delete, name='team_delete'),
    
    # Workshops CRUD
    path('workshops/', views.workshops_list, name='workshops_list'),
    path('workshops/add/', views.workshop_create, name='workshop_create'),
    path('workshops/edit/<int:pk>/', views.workshop_edit, name='workshop_edit'),
    path('workshops/delete/<int:pk>/', views.workshop_delete, name='workshop_delete'),
    
    # Tutorials CRUD
    path('tutorials/', views.tutorials_list, name='tutorials_list'),
    path('tutorials/add/', views.tutorial_create, name='tutorial_create'),
    path('tutorials/edit/<int:pk>/', views.tutorial_edit, name='tutorial_edit'),
    path('tutorials/delete/<int:pk>/', views.tutorial_delete, name='tutorial_delete'),
    
    # Research & Technology Unified CRUD
    path('rt/', views.rt_list, name='rt_list'),
    path('rt/add/', views.rt_notice_create, name='rt_notice_create'),
    path('rt/edit/<int:pk>/', views.rt_notice_edit, name='rt_notice_edit'),
    path('rt/delete/<int:pk>/', views.rt_notice_delete, name='rt_notice_delete'),

    # Site Settings/Stats
    path('stats/edit/', views.edit_homepage_stats, name='edit_stats'),

    # Carousel Images CRUD
    path('carousel/', views.carousel_list, name='carousel_list'),
    path('carousel/add/', views.carousel_create, name='carousel_create'),
    path('carousel/edit/<int:pk>/', views.carousel_edit, name='carousel_edit'),
    path('carousel/delete/<int:pk>/', views.carousel_delete, name='carousel_delete'),

    # Impact Management
    path('impact/', views.impact_list, name='impact_list'),
    
    # Impact Stories
    path('impact/stories/add/', views.impact_story_create, name='impact_story_create'),
    path('impact/stories/edit/<int:pk>/', views.impact_story_edit, name='impact_story_edit'),
    path('impact/stories/delete/<int:pk>/', views.impact_story_delete, name='impact_story_delete'),
    

    # Profile/Security
    path('password-change/', views.DashboardPasswordChangeView.as_view(), name='password_change'),
    
    # OTP Password Reset
    path('password-reset/', views.otp_request_view, name='password_reset'),
    path('password-reset/verify/', views.otp_verify_view, name='otp_verify'),
    path('password-reset/set-password/', views.otp_set_password_view, name='otp_set_password'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='dashboard/password_reset_complete.html'
         ), 
         name='password_reset_complete'),

    # Import/Export
    path('export/<str:model_type>/', views.export_data, name='export_data'),
    path('import/<str:model_type>/', views.import_data, name='import_data'),
]
