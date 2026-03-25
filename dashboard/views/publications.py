from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from publications.models import Publication
from dashboard.models import ActivityLog
from dashboard.forms import PublicationForm

@login_required
def publication_list(request):
    """List journal papers, conference, etc. with search and filter"""
    publications_list = Publication.objects.all().order_by('-publication_date')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        publications_list = publications_list.filter(
            Q(title__icontains=search_query) | 
            Q(authors__icontains=search_query) |
            Q(journal_name__icontains=search_query) |
            Q(publisher__icontains=search_query)
        )
        
    # Filter functionality
    category_filter = request.GET.get('category', '')
    if category_filter:
        publications_list = publications_list.filter(category=category_filter)
        
    paginator = Paginator(publications_list, 20)
    page_number = request.GET.get('page')
    publications = paginator.get_page(page_number)
    
    context = {
        'publications': publications,
        'search_query': search_query,
        'category_filter': category_filter,
    }
    return render(request, 'dashboard/publications/publication_list.html', context)

@login_required
def publication_add(request):
    """Add a new publication"""
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Created',
                model_name='Publication',
                object_id=publication.id,
                object_name=f"{publication.title[:50]}..." if len(publication.title)>50 else publication.title
            )
            messages.success(request, f"Publication '{publication.title}' added successfully.")
            return redirect('dashboard:publication_list')
    else:
        form = PublicationForm()
    return render(request, 'dashboard/publications/publication_form.html', {'form': form, 'action': 'Add'})

@login_required
def publication_edit(request, pk):
    """Edit an existing publication"""
    publication = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, instance=publication)
        if form.is_valid():
            publication = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Updated',
                model_name='Publication',
                object_id=publication.id,
                object_name=f"{publication.title[:50]}..." if len(publication.title)>50 else publication.title
            )
            messages.success(request, f"Publication '{publication.title}' updated successfully.")
            return redirect('dashboard:publication_list')
    else:
        form = PublicationForm(instance=publication)
    return render(request, 'dashboard/publications/publication_form.html', {'form': form, 'action': 'Edit', 'publication': publication})

@login_required
def publication_delete(request, pk):
    """Delete a publication"""
    publication = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        publication_title = publication.title
        ActivityLog.objects.create(
            user=request.user,
            action='Deleted',
            model_name='Publication',
            object_id=publication.id,
            object_name=f"{publication_title[:50]}..." if len(publication_title)>50 else publication_title
        )
        publication.delete()
        messages.success(request, f"Publication '{publication_title}' deleted successfully.")
        return redirect('dashboard:publication_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': publication, 'back_url': 'dashboard:publication_list'})
