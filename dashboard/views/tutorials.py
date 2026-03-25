from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.models import Tutorial
from dashboard.models import ActivityLog
from dashboard.forms import TutorialForm

@login_required
def tutorial_list(request):
    """List tutorials with search and filter"""
    tutorials_list = Tutorial.objects.all().order_by('-created_date', 'lecture_number')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        tutorials_list = tutorials_list.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(playlist_id__icontains=search_query)
        )
        
    paginator = Paginator(tutorials_list, 20)
    page_number = request.GET.get('page')
    tutorials = paginator.get_page(page_number)
    
    context = {
        'tutorials': tutorials,
        'search_query': search_query,
    }
    return render(request, 'dashboard/tutorials/tutorial_list.html', context)

@login_required
def tutorial_add(request):
    """Add a new tutorial"""
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES)
        if form.is_valid():
            tutorial = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Created',
                model_name='Tutorial',
                object_id=tutorial.id,
                object_name=f"{tutorial.title[:50]}..." if len(tutorial.title)>50 else tutorial.title
            )
            messages.success(request, f"Tutorial '{tutorial.title}' added successfully.")
            return redirect('dashboard:tutorial_list')
    else:
        form = TutorialForm()
    return render(request, 'dashboard/tutorials/tutorial_form.html', {'form': form, 'action': 'Add'})

@login_required
def tutorial_edit(request, pk):
    """Edit an existing tutorial"""
    tutorial = get_object_or_404(Tutorial, pk=pk)
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES, instance=tutorial)
        if form.is_valid():
            tutorial = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Updated',
                model_name='Tutorial',
                object_id=tutorial.id,
                object_name=f"{tutorial.title[:50]}..." if len(tutorial.title)>50 else tutorial.title
            )
            messages.success(request, f"Tutorial '{tutorial.title}' updated successfully.")
            return redirect('dashboard:tutorial_list')
    else:
        form = TutorialForm(instance=tutorial)
    return render(request, 'dashboard/tutorials/tutorial_form.html', {'form': form, 'action': 'Edit', 'tutorial': tutorial})

@login_required
def tutorial_delete(request, pk):
    """Delete a tutorial"""
    tutorial = get_object_or_404(Tutorial, pk=pk)
    if request.method == 'POST':
        tutorial_title = tutorial.title
        ActivityLog.objects.create(
            user=request.user,
            action='Deleted',
            model_name='Tutorial',
            object_id=tutorial.id,
            object_name=f"{tutorial_title[:50]}..." if len(tutorial_title)>50 else tutorial_title
        )
        tutorial.delete()
        messages.success(request, f"Tutorial '{tutorial_title}' deleted successfully.")
        return redirect('dashboard:tutorial_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': tutorial, 'back_url': 'dashboard:tutorial_list'})
