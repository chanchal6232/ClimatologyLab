from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from projects.models import ResearchProject
from dashboard.models import ActivityLog
from dashboard.forms import ResearchProjectForm

@login_required
def project_list(request):
    """List research and consultancy projects with search and filter"""
    projects_list = ResearchProject.objects.all().order_by('-start_date')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        projects_list = projects_list.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(funding_agency__icontains=search_query) |
            Q(collaborators__icontains=search_query)
        )
        
    # Filter functionality
    type_filter = request.GET.get('project_type', '')
    if type_filter:
        projects_list = projects_list.filter(project_type=type_filter)
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter:
        projects_list = projects_list.filter(status=status_filter)
        
    paginator = Paginator(projects_list, 20)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    
    context = {
        'projects': projects,
        'search_query': search_query,
        'type_filter': type_filter,
        'status_filter': status_filter,
    }
    return render(request, 'dashboard/projects/project_list.html', context)

@login_required
def project_add(request):
    """Add a new project"""
    if request.method == 'POST':
        form = ResearchProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Created',
                model_name='ResearchProject',
                object_id=project.id,
                object_name=f"{project.title[:50]}..." if len(project.title)>50 else project.title
            )
            messages.success(request, f"Project '{project.title}' added successfully.")
            return redirect('dashboard:project_list')
    else:
        form = ResearchProjectForm()
    return render(request, 'dashboard/projects/project_form.html', {'form': form, 'action': 'Add'})

@login_required
def project_edit(request, pk):
    """Edit an existing project"""
    project = get_object_or_404(ResearchProject, pk=pk)
    if request.method == 'POST':
        form = ResearchProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            project = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Updated',
                model_name='ResearchProject',
                object_id=project.id,
                object_name=f"{project.title[:50]}..." if len(project.title)>50 else project.title
            )
            messages.success(request, f"Project '{project.title}' updated successfully.")
            return redirect('dashboard:project_list')
    else:
        form = ResearchProjectForm(instance=project)
    return render(request, 'dashboard/projects/project_form.html', {'form': form, 'action': 'Edit', 'project': project})

@login_required
def project_delete(request, pk):
    """Delete a project"""
    project = get_object_or_404(ResearchProject, pk=pk)
    if request.method == 'POST':
        project_title = project.title
        ActivityLog.objects.create(
            user=request.user,
            action='Deleted',
            model_name='ResearchProject',
            object_id=project.id,
            object_name=f"{project_title[:50]}..." if len(project_title)>50 else project_title
        )
        project.delete()
        messages.success(request, f"Project '{project_title}' deleted successfully.")
        return redirect('dashboard:project_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': project, 'back_url': 'dashboard:project_list'})
