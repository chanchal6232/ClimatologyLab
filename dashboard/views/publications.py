from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from publications.models import Publication
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
            Q(journal__icontains=search_query)
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
        'query': search_query,
        'current_category': category_filter or 'all',
        'categories': Publication.CATEGORY_CHOICES,
        'total_count': Publication.objects.count(),
    }
    return render(request, 'dashboard/publications_list.html', context)

@login_required
def publication_add(request):
    """Add a new publication"""
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save()
            messages.success(request, f"Publication '{publication.title}' added successfully.")
            return redirect('dashboard:publication_list')
    else:
        form = PublicationForm()
    return render(request, 'dashboard/publication_form.html', {'form': form, 'action': 'Add'})

@login_required
def publication_edit(request, pk):
    """Edit an existing publication"""
    publication = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, instance=publication)
        if form.is_valid():
            publication = form.save()
            messages.success(request, f"Publication '{publication.title}' updated successfully.")
            return redirect('dashboard:publication_list')
    else:
        form = PublicationForm(instance=publication)
    return render(request, 'dashboard/publication_form.html', {'form': form, 'action': 'Edit', 'publication': publication})

@login_required
def publication_delete(request, pk):
    """Delete a publication"""
    publication = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        publication_title = publication.title
        publication.delete()
        messages.success(request, f"Publication '{publication_title}' deleted successfully.")
        return redirect('dashboard:publication_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': publication, 'back_url': 'dashboard:publication_list'})
