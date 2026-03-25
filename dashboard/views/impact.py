from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ImpactStory, ResearchHighlight, PolicyImpact
from dashboard.forms import ImpactStoryForm, ResearchHighlightForm, PolicyImpactForm

# --- Impact Story Views ---
@login_required
def impact_story_list(request):
    """List Impact Stories"""
    stories_list = ImpactStory.objects.all().order_by('order', '-created_at')
    paginator = Paginator(stories_list, 20)
    page_number = request.GET.get('page')
    stories = paginator.get_page(page_number)
    return render(request, 'dashboard/impact_list.html', {'stories': stories})

@login_required
def impact_story_add(request):
    """Add a new Impact Story"""
    if request.method == 'POST':
        form = ImpactStoryForm(request.POST, request.FILES)
        if form.is_valid():
            story = form.save()
            messages.success(request, f"Impact Story '{story.title}' added successfully.")
            return redirect('dashboard:impact_story_list')
    else:
        form = ImpactStoryForm()
    return render(request, 'dashboard/rt_form.html', {'form': form, 'action': 'Add'})

@login_required
def impact_story_edit(request, pk):
    """Edit an Impact Story"""
    story = get_object_or_404(ImpactStory, pk=pk)
    if request.method == 'POST':
        form = ImpactStoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            story = form.save()
            messages.success(request, f"Impact Story '{story.title}' updated successfully.")
            return redirect('dashboard:impact_story_list')
    else:
        form = ImpactStoryForm(instance=story)
    return render(request, 'dashboard/rt_form.html', {'form': form, 'action': 'Edit', 'story': story})

@login_required
def impact_story_delete(request, pk):
    """Delete an Impact Story"""
    story = get_object_or_404(ImpactStory, pk=pk)
    if request.method == 'POST':
        title = story.title
        story.delete()
        messages.success(request, f"Impact Story '{title}' deleted successfully.")
        return redirect('dashboard:impact_story_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': story, 'back_url': 'dashboard:impact_story_list'})

# --- Research Highlight Views ---
@login_required
def research_highlight_list(request):
    """List Research Highlights"""
    highlights_list = ResearchHighlight.objects.all().order_by('order', 'title')
    paginator = Paginator(highlights_list, 20)
    page_number = request.GET.get('page')
    highlights = paginator.get_page(page_number)
    return render(request, 'dashboard/impact_list.html', {'highlights': highlights, 'type': 'highlights'})

@login_required
def research_highlight_add(request):
    """Add a new Research Highlight"""
    if request.method == 'POST':
        form = ResearchHighlightForm(request.POST, request.FILES)
        if form.is_valid():
            highlight = form.save()
            messages.success(request, f"Research Highlight '{highlight.title}' added successfully.")
            return redirect('dashboard:research_highlight_list')
    else:
        form = ResearchHighlightForm()
    return render(request, 'dashboard/rt_form.html', {'form': form, 'action': 'Add'})

@login_required
def research_highlight_edit(request, pk):
    """Edit a Research Highlight"""
    highlight = get_object_or_404(ResearchHighlight, pk=pk)
    if request.method == 'POST':
        form = ResearchHighlightForm(request.POST, request.FILES, instance=highlight)
        if form.is_valid():
            highlight = form.save()
            messages.success(request, f"Research Highlight '{highlight.title}' updated successfully.")
            return redirect('dashboard:research_highlight_list')
    else:
        form = ResearchHighlightForm(instance=highlight)
    return render(request, 'dashboard/rt_form.html', {'form': form, 'action': 'Edit', 'highlight': highlight})

@login_required
def research_highlight_delete(request, pk):
    """Delete a Research Highlight"""
    highlight = get_object_or_404(ResearchHighlight, pk=pk)
    if request.method == 'POST':
        title = highlight.title
        highlight.delete()
        messages.success(request, f"Research Highlight '{title}' deleted successfully.")
        return redirect('dashboard:research_highlight_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': highlight, 'back_url': 'dashboard:research_highlight_list'})

# --- Policy Impact Views ---
@login_required
def policy_impact_list(request):
    """List Policy Impacts"""
    impacts_list = PolicyImpact.objects.all().order_by('-year', 'order')
    paginator = Paginator(impacts_list, 20)
    page_number = request.GET.get('page')
    impacts = paginator.get_page(page_number)
    return render(request, 'dashboard/impact_list.html', {'impacts': impacts, 'type': 'policy'})

@login_required
def policy_impact_add(request):
    """Add a new Policy Impact"""
    if request.method == 'POST':
        form = PolicyImpactForm(request.POST, request.FILES)
        if form.is_valid():
            impact = form.save()
            messages.success(request, f"Policy Impact '{impact.title}' added successfully.")
            return redirect('dashboard:policy_impact_list')
    else:
        form = PolicyImpactForm()
    return render(request, 'dashboard/rt_form.html', {'form': form, 'action': 'Add'})

@login_required
def policy_impact_edit(request, pk):
    """Edit a Policy Impact"""
    impact = get_object_or_404(PolicyImpact, pk=pk)
    if request.method == 'POST':
        form = PolicyImpactForm(request.POST, request.FILES, instance=impact)
        if form.is_valid():
            impact = form.save()
            messages.success(request, f"Policy Impact '{impact.title}' updated successfully.")
            return redirect('dashboard:policy_impact_list')
    else:
        form = PolicyImpactForm(instance=impact)
    return render(request, 'dashboard/rt_form.html', {'form': form, 'action': 'Edit', 'impact': impact})

@login_required
def policy_impact_delete(request, pk):
    """Delete a Policy Impact"""
    impact = get_object_or_404(PolicyImpact, pk=pk)
    if request.method == 'POST':
        title = impact.title
        impact.delete()
        messages.success(request, f"Policy Impact '{title}' deleted successfully.")
        return redirect('dashboard:policy_impact_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': impact, 'back_url': 'dashboard:policy_impact_list'})
