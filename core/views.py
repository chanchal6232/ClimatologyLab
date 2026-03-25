from itertools import chain
from operator import attrgetter

from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

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


def home(request):
    """Homepage view"""
    # Get or create stats
    stats, created = HomePageStats.objects.get_or_create(
        pk=1,
        defaults={
            'publications_count': 100,
            'projects_count': 120,
            'outreach_programs_count': 50
        }
    )
    
    # Get recent workshops
    workshops = Workshop.objects.filter(is_active=True).order_by('-event_date')[:6]
    
    # Get recent Research & Technology notices
    rt_notices = RTNotice.objects.filter(is_active=True).order_by('-event_date')[:3]
    
    # Calculate Dynamic Counts
    pub_count = Publication.objects.filter(is_active=True).count()
    proj_count = ResearchProject.objects.filter(is_active=True).count()
    team_count = TeamMember.objects.filter(is_active=True).count()
    
    context = {
        'stats': stats,
        'workshops': workshops,
        'rt_notices': rt_notices,
        'pub_count': pub_count,
        'proj_count': proj_count,
        'team_count': team_count,
        'carousel_images': CarouselImage.objects.filter(is_active=True),
    }
    return render(request, 'home.html', context)


def projects_view(request):
    """Default projects view - redirects to research projects"""
    return redirect('core:research_projects')


def research_projects_view(request):
    """Research projects listing view with search and sort"""
    # Base queryset
    projects = ResearchProject.objects.filter(is_active=True, project_type='research')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(funding_agency__icontains=search_query) |
            Q(collaborators__icontains=search_query)
        )
    
    # Sort functionality
    sort_by = request.GET.get('sort', 'latest')
    if sort_by == 'latest':
        projects = projects.order_by('-start_date')
    elif sort_by == 'oldest':
        projects = projects.order_by('start_date')
    elif sort_by == 'az':
        projects = projects.order_by('title')
    elif sort_by == 'za':
        projects = projects.order_by('-title')
    else:
        projects = projects.order_by('-start_date')  # Default
    
    context = {
        'projects': projects,
        'project_type': 'research',
        'page_title': 'Research Projects',
        'search_query': search_query,
        'sort_by': sort_by,
        'is_sort_latest': sort_by == 'latest' or not sort_by,
        'is_sort_oldest': sort_by == 'oldest',
        'is_sort_az': sort_by == 'az',
        'is_sort_za': sort_by == 'za',
    }
    return render(request, 'projects.html', context)


def consultancy_projects_view(request):
    """Consultancy projects listing view with search and sort"""
    # Base queryset
    projects = ResearchProject.objects.filter(is_active=True, project_type='consultancy')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(funding_agency__icontains=search_query) |
            Q(collaborators__icontains=search_query)
        )
    
    # Sort functionality
    sort_by = request.GET.get('sort', 'latest')
    if sort_by == 'latest':
        projects = projects.order_by('-start_date')
    elif sort_by == 'oldest':
        projects = projects.order_by('start_date')
    elif sort_by == 'az':
        projects = projects.order_by('title')
    elif sort_by == 'za':
        projects = projects.order_by('-title')
    else:
        projects = projects.order_by('-start_date')  # Default
    
    context = {
        'projects': projects,
        'project_type': 'consultancy',
        'page_title': 'Consultancy Projects',
        'search_query': search_query,
        'sort_by': sort_by,
        'is_sort_latest': sort_by == 'latest' or not sort_by,
        'is_sort_oldest': sort_by == 'oldest',
        'is_sort_az': sort_by == 'az',
        'is_sort_za': sort_by == 'za',
    }
    return render(request, 'projects.html', context)


def project_detail(request, pk):
    """Project detail view showing all database fields"""
    project = get_object_or_404(ResearchProject, pk=pk, is_active=True)
    
    context = {
        'project': project,
        'page_title': project.title,
    }
    return render(request, 'project_detail.html', context)


def team_view(request):
    """Team listing view with categories"""
    all_members = TeamMember.objects.filter(is_active=True)
    
    # Filter into categories based on role keywords
    faculty_members = []
    postgraduate_members = []
    phd_members = []
    alumni_members = []
    
    for member in all_members:
        role_lower = member.role.lower()
        if 'faculty' in role_lower or 'professor' in role_lower:
            faculty_members.append(member)
        elif 'post graduate' in role_lower or 'm.arch' in role_lower or 'master' in role_lower:
            postgraduate_members.append(member)
        elif 'phd' in role_lower or 'research scholar' in role_lower or 'doctoral' in role_lower:
            phd_members.append(member)
        elif 'alumni' in role_lower or 'alumnus' in role_lower:
            alumni_members.append(member)
    
    context = {
        'faculty_members': faculty_members,
        'postgraduate_members': postgraduate_members,
        'phd_members': phd_members,
        'alumni_members': alumni_members,
    }
    return render(request, 'team.html', context)


def learn_view(request):
    """Learn page view"""
    context = {
        'page_title': 'Learning Resources',
    }
    return render(request, 'learn.html', context)


def impact_view(request):
    """Impact page view with dynamic content"""
    success_stories = ImpactStory.objects.filter(is_active=True)
    research_highlights = ResearchHighlight.objects.filter(is_active=True)
    policy_impacts = PolicyImpact.objects.filter(is_active=True)
    
    context = {
        'impact_stats': {
            'publications_count': Publication.objects.count(),
            'citations_count': '450+', # Manual for now
            'collaborations_count': 12, # Manual for now
            'outreach_count': 25 # Manual for now
        },
        'success_stories': success_stories,
        'research_highlights': research_highlights,
        'policy_impacts': policy_impacts
    }
    return render(request, 'impact.html', context)


def contact_view(request):
    """Contact page view"""
    return render(request, 'contact.html')


def workshops_view(request):
    """Workshops listing view with search and sort"""
    # Base queryset
    workshops = Workshop.objects.filter(is_active=True)
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        workshops = workshops.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Sort functionality
    sort_by = request.GET.get('sort', 'latest')
    if sort_by == 'latest':
        workshops = workshops.order_by('-event_date')
    elif sort_by == 'oldest':
        workshops = workshops.order_by('event_date')
    elif sort_by == 'az':
        workshops = workshops.order_by('title')
    elif sort_by == 'za':
        workshops = workshops.order_by('-title')
    else:
        workshops = workshops.order_by('-event_date')  # Default
    
    context = {
        'workshops': workshops,
        'page_title': 'Workshops',
        'search_query': search_query,
        'sort_by': sort_by,
        'is_sort_latest': sort_by == 'latest' or not sort_by,
        'is_sort_oldest': sort_by == 'oldest',
        'is_sort_az': sort_by == 'az',
        'is_sort_za': sort_by == 'za',
    }
    return render(request, 'workshops.html', context)


def tutorials_view(request):
    """Tutorials listing view with playlist support and search/sort"""
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    
    # Sort functionality
    sort_by = request.GET.get('sort', 'latest')
    
    # Get all active playlists (main/parent videos)
    playlists = Tutorial.objects.filter(
        is_active=True, 
        is_playlist=True
    )
    
    # Apply search to playlists
    if search_query:
        playlists = playlists.filter(title__icontains=search_query)
    
    # Apply sort to playlists
    if sort_by == 'oldest':
        playlists = playlists.order_by('created_date')
    elif sort_by == 'az':
        playlists = playlists.order_by('title')
    elif sort_by == 'za':
        playlists = playlists.order_by('-title')
    else:  # latest (default)
        playlists = playlists.order_by('-created_date')
    
    # For each playlist, get its lectures
    playlist_data = []
    for playlist in playlists:
        lectures = Tutorial.objects.filter(
            is_active=True,
            is_playlist=False,
            playlist_id=playlist.playlist_id
        ).order_by('lecture_number', 'id')
        
        playlist_data.append({
            'playlist': playlist,
            'lectures': list(lectures),
            'lecture_count': lectures.count()
        })
    
    # Get standalone tutorials (ONLY videos NOT part of any playlist)
    standalone_tutorials = Tutorial.objects.filter(
        is_active=True,
        is_playlist=False
    ).filter(
        Q(playlist_id__isnull=True) | Q(playlist_id='')
    )
    
    # Apply search to standalone tutorials
    if search_query:
        standalone_tutorials = standalone_tutorials.filter(title__icontains=search_query)
    
    # Apply sort to standalone tutorials
    if sort_by == 'oldest':
        standalone_tutorials = standalone_tutorials.order_by('created_date')
    elif sort_by == 'az':
        standalone_tutorials = standalone_tutorials.order_by('title')
    elif sort_by == 'za':
        standalone_tutorials = standalone_tutorials.order_by('-title')
    else:  # latest (default)
        standalone_tutorials = standalone_tutorials.order_by('-created_date')
    
    context = {
        'playlist_data': playlist_data,
        'standalone_tutorials': standalone_tutorials,
        'page_title': 'Tutorials',
        'search_query': search_query,
        'sort_by': sort_by,
        'is_sort_latest': sort_by == 'latest' or not sort_by,
        'is_sort_oldest': sort_by == 'oldest',
        'is_sort_az': sort_by == 'az',
        'is_sort_za': sort_by == 'za',
    }
    return render(request, 'tutorials.html', context)


def research_technology_view(request):
    """Research and Technology notices view with search and sort"""
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    
    notices = RTNotice.objects.filter(is_active=True)
    
    if search_query:
        notices = notices.filter(
            Q(title__icontains=search_query) | Q(description__icontains=search_query)
        )
        
    # Sort functionality
    sort_by = request.GET.get('sort', 'latest')
    if sort_by == 'oldest':
        notices = notices.order_by('event_date')
    elif sort_by == 'az':
        notices = notices.order_by('title')
    elif sort_by == 'za':
        notices = notices.order_by('-title')
    else: # latest
        notices = notices.order_by('-event_date')
    
    context = {
        'notices': notices,
        'search_query': search_query,
        'sort_by': sort_by,
        'is_sort_latest': sort_by == 'latest' or not sort_by,
        'is_sort_oldest': sort_by == 'oldest',
        'is_sort_az': sort_by == 'az',
        'is_sort_za': sort_by == 'za',
        'page_title': 'Research & Technology',
        'search_placeholder': 'Search research & technology...',
    }
    return render(request, 'research_technology.html', context)
