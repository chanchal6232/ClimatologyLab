from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from team.models import TeamMember
from dashboard.models import ActivityLog
from dashboard.forms import TeamMemberForm

@login_required
def team_list(request):
    """List team members with search and filter"""
    team_list = TeamMember.objects.all().order_by('order', 'first_name')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        team_list = team_list.filter(
            Q(first_name__icontains=search_query) | 
            Q(last_name__icontains=search_query) |
            Q(role__icontains=search_query) |
            Q(email__icontains=search_query)
        )
        
    # Filter functionality
    # You can add more filters here if needed
        
    paginator = Paginator(team_list, 20)
    page_number = request.GET.get('page')
    team = paginator.get_page(page_number)
    
    context = {
        'team': team,
        'search_query': search_query,
    }
    return render(request, 'dashboard/team/team_list.html', context)

@login_required
def team_add(request):
    """Add a new team member"""
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Created',
                model_name='TeamMember',
                object_id=member.id,
                object_name=f"{member.first_name} {member.last_name}"
            )
            messages.success(request, f"Team member '{member.first_name}' added successfully.")
            return redirect('dashboard:team_list')
    else:
        form = TeamMemberForm()
    return render(request, 'dashboard/team/team_form.html', {'form': form, 'action': 'Add'})

@login_required
def team_edit(request, pk):
    """Edit an existing team member"""
    member = get_object_or_404(TeamMember, pk=pk)
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            member = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Updated',
                model_name='TeamMember',
                object_id=member.id,
                object_name=f"{member.first_name} {member.last_name}"
            )
            messages.success(request, f"Team member '{member.first_name}' updated successfully.")
            return redirect('dashboard:team_list')
    else:
        form = TeamMemberForm(instance=member)
    return render(request, 'dashboard/team/team_form.html', {'form': form, 'action': 'Edit', 'member': member})

@login_required
def team_delete(request, pk):
    """Delete a team member"""
    member = get_object_or_404(TeamMember, pk=pk)
    if request.method == 'POST':
        name = f"{member.first_name} {member.last_name}"
        ActivityLog.objects.create(
            user=request.user,
            action='Deleted',
            model_name='TeamMember',
            object_id=member.id,
            object_name=name
        )
        member.delete()
        messages.success(request, f"Team member '{name}' deleted successfully.")
        return redirect('dashboard:team_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': member, 'back_url': 'dashboard:team_list'})
