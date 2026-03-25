from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from workshops.models import Workshop
from core.models import RTNotice
from dashboard.forms import WorkshopForm, RTNoticeForm

@login_required
def workshop_list(request):
    """List workshops with search and filter"""
    workshops_list = Workshop.objects.all().order_by('-event_date')
    
    # Search functionality
    search_query = request.GET.get('q', '').strip()
    if search_query:
        workshops_list = workshops_list.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        
    paginator = Paginator(workshops_list, 20)
    page_number = request.GET.get('page')
    workshops = paginator.get_page(page_number)
    
    context = {
        'workshops': workshops,
        'query': search_query,
    }
    return render(request, 'dashboard/workshops_list.html', context)

@login_required
def workshop_add(request):
    """Add a new workshop"""
    if request.method == 'POST':
        form = WorkshopForm(request.POST, request.FILES)
        if form.is_valid():
            workshop = form.save()
            messages.success(request, f"Workshop '{workshop.title}' added successfully.")
            return redirect('dashboard:workshop_list')
    else:
        form = WorkshopForm()
    return render(request, 'dashboard/workshop_form.html', {'form': form, 'action': 'Add'})

@login_required
def workshop_edit(request, pk):
    """Edit an existing workshop"""
    workshop = get_object_or_404(Workshop, pk=pk)
    if request.method == 'POST':
        form = WorkshopForm(request.POST, request.FILES, instance=workshop)
        if form.is_valid():
            workshop = form.save()
            messages.success(request, f"Workshop '{workshop.title}' updated successfully.")
            return redirect('dashboard:workshop_list')
    else:
        form = WorkshopForm(instance=workshop)
    return render(request, 'dashboard/workshop_form.html', {'form': form, 'action': 'Edit', 'workshop': workshop})

@login_required
def workshop_delete(request, pk):
    """Delete a workshop"""
    workshop = get_object_or_404(Workshop, pk=pk)
    if request.method == 'POST':
        workshop_title = workshop.title
        workshop.delete()
        messages.success(request, f"Workshop '{workshop_title}' deleted successfully.")
        return redirect('dashboard:workshop_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': workshop, 'back_url': 'dashboard:workshop_list'})

# --- RT Notice Views ---
@login_required
def rt_notice_list(request):
    """List RT Notices with search"""
    notices_list = RTNotice.objects.all().order_by('-event_date')
    
    search_query = request.GET.get('search', '').strip()
    if search_query:
        notices_list = notices_list.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        
    paginator = Paginator(notices_list, 20)
    page_number = request.GET.get('page')
    notices = paginator.get_page(page_number)
    
    return render(request, 'dashboard/rt_list.html', {'notices': notices, 'query': search_query})

@login_required
def rt_notice_add(request):
    """Add a new RT Notice"""
    if request.method == 'POST':
        form = RTNoticeForm(request.POST, request.FILES)
        if form.is_valid():
            notice = form.save()
            messages.success(request, f"Notice '{notice.title}' added successfully.")
            return redirect('dashboard:rt_notice_list')
    else:
        form = RTNoticeForm()
    return render(request, 'dashboard/rt_form.html', {'form': form, 'action': 'Add'})

@login_required
def rt_notice_edit(request, pk):
    """Edit an RT Notice"""
    notice = get_object_or_404(RTNotice, pk=pk)
    if request.method == 'POST':
        form = RTNoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            notice = form.save()
            messages.success(request, f"Notice '{notice.title}' updated successfully.")
            return redirect('dashboard:rt_notice_list')
    else:
        form = RTNoticeForm(instance=notice)
    return render(request, 'dashboard/rt_form.html', {'form': form, 'action': 'Edit', 'notice': notice})

@login_required
def rt_notice_delete(request, pk):
    """Delete an RT Notice"""
    notice = get_object_or_404(RTNotice, pk=pk)
    if request.method == 'POST':
        notice_title = notice.title
        notice.delete()
        messages.success(request, f"Notice '{notice_title}' deleted successfully.")
        return redirect('dashboard:rt_notice_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': notice, 'back_url': 'dashboard:rt_notice_list'})
