import csv
import io
from datetime import datetime

from django.apps import apps
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from tablib import Dataset

from core.models import (
    CarouselImage,
    HomePageContent,
    HomePageStats,
    ImpactStory,
    PolicyImpact,
    ResearchHighlight,
    RTNotice,
    Tutorial,
)
from projects.models import ResearchProject
from publications.models import Publication
from team.models import TeamMember
from workshops.models import Workshop

# Resource classes for import/export
from publications.resources import PublicationResource
from team.resources import TeamMemberResource
from projects.resources import ResearchProjectResource
from workshops.resources import WorkshopResource

MODEL_RESOURCE_MAP = {
    'publication': (Publication, PublicationResource),
    'teammember': (TeamMember, TeamMemberResource),
    'researchproject': (ResearchProject, ResearchProjectResource),
    'workshop': (Workshop, WorkshopResource),
}

@login_required
def dashboard_home(request):
    """Dashboard home view with stats and summary"""
    stats = {
        'project_count': ResearchProject.objects.count(),
        'pub_count': Publication.objects.count(),
        'team_count': TeamMember.objects.count(),
        'workshop_count': Workshop.objects.count(),
        'rt_count': RTNotice.objects.count(),
        'carousel_count': CarouselImage.objects.count(),
        'impact_count': ImpactStory.objects.count(),
        
        # Category-specific counts for the UI boxes
        'j_c': Publication.objects.filter(category='journal').count(),
        'c_c': Publication.objects.filter(category='conference').count(),
        'b_c': Publication.objects.filter(category='book').count(),
        'bg_c': Publication.objects.filter(category='guideline').count(),
        'o_c': Publication.objects.filter(category='other').count(),
    }
    return render(request, 'dashboard/home.html', stats)

@login_required
def export_data(request, model_name):
    """Export model data to various formats"""
    if model_name not in MODEL_RESOURCE_MAP:
        messages.error(request, f"Export not supported for {model_name}.")
        return redirect('dashboard:home')
    
    model_class, resource_class = MODEL_RESOURCE_MAP[model_name]
    resource = resource_class()
    dataset = resource.export()
    
    format_type = request.GET.get('format', 'csv')
    
    if format_type == 'xlsx':
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{model_name}_{datetime.now().strftime("%Y%m%d")}.xlsx"'
    elif format_type == 'json':
        response = HttpResponse(dataset.json, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{model_name}_{datetime.now().strftime("%Y%m%d")}.json"'
    else: # Default to CSV
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{model_name}_{datetime.now().strftime("%Y%m%d")}.csv"'
        
    return response

@login_required
def import_data(request, model_name):
    """Import model data from CSV/XLSX"""
    if model_name not in MODEL_RESOURCE_MAP:
        messages.error(request, f"Import not supported for {model_name}.")
        return redirect('dashboard:home')
        
    if request.method == 'POST' and request.FILES.get('import_file'):
        model_class, resource_class = MODEL_RESOURCE_MAP[model_name]
        resource = resource_class()
        dataset = Dataset()
        import_file = request.FILES['import_file']
        
        try:
            if import_file.name.endswith('.csv'):
                dataset.load(import_file.read().decode('utf-8'), format='csv')
            elif import_file.name.endswith('.xlsx'):
                dataset.load(import_file.read(), format='xlsx')
            else:
                messages.error(request, "Unsupported file format. Please use CSV or XLSX.")
                return redirect(f'dashboard:{model_name}_list')
                
            result = resource.import_data(dataset, dry_run=False, raise_errors=True)
            messages.success(request, f"Successfully imported {result.total_rows} records.")
            
        except Exception as e:
            messages.error(request, f"Error importing data: {str(e)}")
            
    return redirect(f'dashboard:{model_name}_list')
