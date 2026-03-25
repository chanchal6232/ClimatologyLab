from .base import dashboard_home, export_data, import_data, activity_log_view
from .content import (
    homepage_stats_update as edit_homepage_stats,
    carousel_list, 
    carousel_add as carousel_create, 
    carousel_edit, 
    carousel_delete,
    homepage_content_update
)
from .projects import (
    project_list as projects_list, 
    project_add as project_create, 
    project_edit, 
    project_delete
)
from .publications import (
    publication_list as publications_list, 
    publication_add as publication_create, 
    publication_edit, 
    publication_delete
)
from .team import (
    team_list, 
    team_add as team_create, 
    team_edit, 
    team_delete
)
from .workshops import (
    workshop_list as workshops_list, 
    workshop_add as workshop_create, 
    workshop_edit, 
    workshop_delete,
    rt_notice_list as rt_list, 
    rt_notice_add as rt_notice_create, 
    rt_notice_edit, 
    rt_notice_delete
)
from .tutorials import (
    tutorial_list as tutorials_list, 
    tutorial_add as tutorial_create, 
    tutorial_edit, 
    tutorial_delete
)
from .impact import (
    impact_story_list as impact_list, 
    impact_story_add as impact_story_create, 
    impact_story_edit, 
    impact_story_delete,
    research_highlight_list, 
    research_highlight_add, 
    research_highlight_edit, 
    research_highlight_delete,
    policy_impact_list, 
    policy_impact_add, 
    policy_impact_edit, 
    policy_impact_delete
)
from .auth import (
    password_reset_request as otp_request_view, 
    password_reset_verify as otp_verify_view, 
    password_reset_confirm as otp_set_password_view,
    DashboardPasswordChangeView
)
from .utils import supabase_test

# Placeholders for potentially missing views
@login_required
def bulk_delete(request):
    messages.warning(request, "Bulk delete is currently unavailable.")
    return redirect('dashboard:home')

@login_required
def publication_export_csv(request):
    return export_data(request, 'publication')
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
