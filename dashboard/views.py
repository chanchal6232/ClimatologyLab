from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from projects.models import ResearchProject
from publications.models import Publication
from team.models import TeamMember
from workshops.models import Workshop
from core.models import (
    Tutorial, RTNotice, HomePageStats, CarouselImage,
    ImpactStory, ResearchHighlight, PolicyImpact
)
from .forms import (
    ProjectForm, PublicationForm, TeamMemberForm, WorkshopForm, 
    RTNoticeForm, HomePageStatsForm, 
    CarouselImageForm, TutorialForm, ImpactStoryForm, 
    ResearchHighlightForm, PolicyImpactForm,
    OTPRequestForm, OTPVerifyForm, OTPSetPasswordForm
)
from .resources import (
    ResearchProjectResource, PublicationResource, TeamMemberResource,
    WorkshopResource, TutorialResource, ImpactStoryResource,
    RTNoticeResource
)
from django.http import HttpResponse
from tablib import Dataset

# --- IMPACT CRUD ---

@staff_member_required(login_url='/accounts/login/')
def impact_list(request):
    stories = ImpactStory.objects.all().order_by('order', '-created_at')
    return render(request, 'dashboard/impact_list.html', {'stories': stories})

# Success Stories
@staff_member_required(login_url='/accounts/login/')
@permission_required('core.add_impactstory', raise_exception=True)
def impact_story_create(request):
    if request.method == 'POST':
        form = ImpactStoryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Impact story added successfully!')
            return redirect('dashboard:impact_list')
    else:
        form = ImpactStoryForm()
    return render(request, 'dashboard/rt_form.html', {'form': form, 'title': 'Add Impact Story', 'type': 'Impact'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.change_impactstory', raise_exception=True)
def impact_story_edit(request, pk):
    story = get_object_or_404(ImpactStory, pk=pk)
    if request.method == 'POST':
        form = ImpactStoryForm(request.POST, request.FILES, instance=story)
        if form.is_valid():
            form.save()
            messages.success(request, 'Impact story updated successfully!')
            return redirect('dashboard:impact_list')
    else:
        form = ImpactStoryForm(instance=story)
    return render(request, 'dashboard/rt_form.html', {'form': form, 'title': 'Edit Impact Story', 'type': 'Impact'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.delete_impactstory', raise_exception=True)
def impact_story_delete(request, pk):
    story = get_object_or_404(ImpactStory, pk=pk)
    if request.method == 'POST':
        story.delete()
        messages.success(request, 'Impact story deleted successfully!')
        return redirect('dashboard:impact_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': story, 'type': 'Impact Story'})

@staff_member_required(login_url='/accounts/login/')
def dashboard_home(request):
    rt_count = RTNotice.objects.count()
    context = {
        'project_count': ResearchProject.objects.count(),
        'pub_count': Publication.objects.count(),
        'team_count': TeamMember.objects.count(),
        'workshop_count': Workshop.objects.count(),
        'rt_count': rt_count,
        'carousel_count': CarouselImage.objects.count(),
        'impact_count': ImpactStory.objects.count(),
    }
    return render(request, 'dashboard/home.html', context)


# --- PROJECTS CRUD ---

@staff_member_required(login_url='/accounts/login/')
@permission_required('projects.view_researchproject', raise_exception=True)
def projects_list(request):
    query = request.GET.get('q')
    projects = ResearchProject.objects.all().order_by('-start_date')
    if query:
        projects = projects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'dashboard/projects_list.html', {'projects': projects, 'query': query})

@staff_member_required(login_url='/accounts/login/')
@permission_required('projects.add_researchproject', raise_exception=True)
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project created successfully!')
            return redirect('dashboard:projects_list')
    else:
        form = ProjectForm()
    return render(request, 'dashboard/project_form.html', {'form': form, 'title': 'Add New Project', 'image_url': None})

@staff_member_required(login_url='/accounts/login/')
@permission_required('projects.change_researchproject', raise_exception=True)
def project_edit(request, pk):
    project = get_object_or_404(ResearchProject, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Project updated successfully!')
            return redirect('dashboard:projects_list')
    else:
        form = ProjectForm(instance=project)
    image_url = None
    if project.image and project.image.name:
        try:
            image_url = project.image.url
        except Exception:
            image_url = None
    return render(request, 'dashboard/project_form.html', {'form': form, 'title': 'Edit Project', 'image_url': image_url})

@staff_member_required(login_url='/accounts/login/')
@permission_required('projects.delete_researchproject', raise_exception=True)
def project_delete(request, pk):
    project = get_object_or_404(ResearchProject, pk=pk)
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Project deleted successfully!')
        return redirect('dashboard:projects_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': project, 'type': 'Project'})

# --- PUBLICATIONS CRUD ---

@staff_member_required(login_url='/accounts/login/')
@permission_required('publications.view_publication', raise_exception=True)
def publications_list(request):
    query = request.GET.get('q')
    publications = Publication.objects.all().order_by('-publication_date')
    if query:
        publications = publications.filter(
            Q(title__icontains=query) | Q(authors__icontains=query)
        )
    return render(request, 'dashboard/publications_list.html', {'publications': publications, 'query': query})

@staff_member_required(login_url='/accounts/login/')
@permission_required('publications.add_publication', raise_exception=True)
def publication_create(request):
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publication added successfully!')
            return redirect('dashboard:publications_list')
    else:
        form = PublicationForm()
    return render(request, 'dashboard/publication_form.html', {'form': form, 'title': 'Add New Publication'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('publications.change_publication', raise_exception=True)
def publication_edit(request, pk):
    pub = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, instance=pub)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publication updated successfully!')
            return redirect('dashboard:publications_list')
    else:
        form = PublicationForm(instance=pub)
    return render(request, 'dashboard/publication_form.html', {'form': form, 'title': 'Edit Publication'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('publications.delete_publication', raise_exception=True)
def publication_delete(request, pk):
    pub = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        pub.delete()
        messages.success(request, 'Publication deleted successfully!')
        return redirect('dashboard:publications_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': pub, 'type': 'Publication'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('publications.view_publication', raise_exception=True)
def publication_export_csv(request):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="publications_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Title', 'Authors', 'Category', 'Date', 'Journal', 'Citation'])

    for pub in Publication.objects.all():
        writer.writerow([pub.title, pub.authors, pub.category, pub.publication_date, pub.journal, pub.citation])

    return response

# --- TEAM CRUD ---

@staff_member_required(login_url='/accounts/login/')
@permission_required('team.view_teammember', raise_exception=True)
def team_list(request):
    query = request.GET.get('q')
    members = TeamMember.objects.all().order_by('order', 'name')
    if query:
        members = members.filter(
            Q(name__icontains=query) | Q(role__icontains=query)
        )
    return render(request, 'dashboard/team_list.html', {'members': members, 'query': query})

@staff_member_required(login_url='/accounts/login/')
@permission_required('team.add_teammember', raise_exception=True)
def team_create(request):
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Team member added successfully!')
                return redirect('dashboard:team_list')
            except Exception as e:
                messages.error(request, f'Upload failed: {e}. Check your Cloudinary credentials in the environment settings.')
    else:
        form = TeamMemberForm()
    return render(request, 'dashboard/team_form.html', {'form': form, 'title': 'Add New Member', 'photo_url': None})

@staff_member_required(login_url='/accounts/login/')
@permission_required('team.change_teammember', raise_exception=True)
def team_edit(request, pk):
    member = get_object_or_404(TeamMember, pk=pk)
    if request.method == 'POST':
        form = TeamMemberForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Team member updated successfully!')
                return redirect('dashboard:team_list')
            except Exception as e:
                messages.error(request, f'Upload failed: {e}. Check your Cloudinary credentials in the environment settings.')
    else:
        form = TeamMemberForm(instance=member)
    # Safely get the photo URL — old local-storage paths raise ValueError when Cloudinary is active
    photo_url = None
    if member.photo and member.photo.name:
        try:
            photo_url = member.photo.url
        except (ValueError, AttributeError, Exception):
            photo_url = None
    return render(request, 'dashboard/team_form.html', {'form': form, 'title': 'Edit Member', 'photo_url': photo_url})

@staff_member_required(login_url='/accounts/login/')
@permission_required('team.delete_teammember', raise_exception=True)
def team_delete(request, pk):
    member = get_object_or_404(TeamMember, pk=pk)
    if request.method == 'POST':
        member.delete()
        messages.success(request, 'Team member removed successfully!')
        return redirect('dashboard:team_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': member, 'type': 'Team Member'})

# --- WORKSHOPS CRUD ---

@staff_member_required(login_url='/accounts/login/')
@permission_required('workshops.view_workshop', raise_exception=True)
def workshops_list(request):
    query = request.GET.get('q')
    workshops = Workshop.objects.all().order_by('-event_date')
    if query:
        workshops = workshops.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    return render(request, 'dashboard/workshops_list.html', {'workshops': workshops, 'query': query})

@staff_member_required(login_url='/accounts/login/')
@permission_required('workshops.add_workshop', raise_exception=True)
def workshop_create(request):
    if request.method == 'POST':
        form = WorkshopForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Workshop added successfully!')
            return redirect('dashboard:workshops_list')
    else:
        form = WorkshopForm()
    return render(request, 'dashboard/workshop_form.html', {'form': form, 'title': 'Add New Workshop'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('workshops.change_workshop', raise_exception=True)
def workshop_edit(request, pk):
    workshop = get_object_or_404(Workshop, pk=pk)
    if request.method == 'POST':
        form = WorkshopForm(request.POST, request.FILES, instance=workshop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Workshop updated successfully!')
            return redirect('dashboard:workshops_list')
    else:
        form = WorkshopForm(instance=workshop)
    return render(request, 'dashboard/workshop_form.html', {'form': form, 'title': 'Edit Workshop'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('workshops.delete_workshop', raise_exception=True)
def workshop_delete(request, pk):
    workshop = get_object_or_404(Workshop, pk=pk)
    if request.method == 'POST':
        workshop.delete()
        messages.success(request, 'Workshop removed successfully!')
        return redirect('dashboard:workshops_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': workshop, 'type': 'Workshop'})

# --- TUTORIALS CRUD ---

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.view_tutorial', raise_exception=True)
def tutorials_list(request):
    query = request.GET.get('q')
    tutorials = Tutorial.objects.all().order_by('order', '-created_date')
    if query:
        tutorials = tutorials.filter(
            Q(title__icontains=query) | Q(playlist_id__icontains=query)
        )
    return render(request, 'dashboard/tutorials_list.html', {'tutorials': tutorials, 'query': query})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.add_tutorial', raise_exception=True)
def tutorial_create(request):
    # Form for Tutorial needs to be added to forms.py if not present
    from .forms import TutorialForm
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tutorial added successfully!')
            return redirect('dashboard:tutorials_list')
    else:
        form = TutorialForm()
    return render(request, 'dashboard/tutorial_form.html', {'form': form, 'title': 'Add New Tutorial'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.change_tutorial', raise_exception=True)
def tutorial_edit(request, pk):
    from .forms import TutorialForm
    tutorial = get_object_or_404(Tutorial, pk=pk)
    if request.method == 'POST':
        form = TutorialForm(request.POST, request.FILES, instance=tutorial)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tutorial updated successfully!')
            return redirect('dashboard:tutorials_list')
    else:
        form = TutorialForm(instance=tutorial)
    return render(request, 'dashboard/tutorial_form.html', {'form': form, 'title': 'Edit Tutorial'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.delete_tutorial', raise_exception=True)
def tutorial_delete(request, pk):
    tutorial = get_object_or_404(Tutorial, pk=pk)
    if request.method == 'POST':
        tutorial.delete()
        messages.success(request, 'Tutorial removed successfully!')
        return redirect('dashboard:tutorials_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': tutorial, 'type': 'Tutorial'})

# --- RT NOTICES CRUD ---

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.view_rtnotice', raise_exception=True)
def rt_list(request):
    query = request.GET.get('q')
    notices = RTNotice.objects.all().order_by('-event_date')
    if query:
        notices = notices.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(notice_type__icontains=query)
        )
    return render(request, 'dashboard/rt_list.html', {'notices': notices, 'query': query})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.add_rtnotice', raise_exception=True)
def rt_notice_create(request):
    if request.method == 'POST':
        form = RTNoticeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notice added successfully!')
            return redirect('dashboard:rt_list')
    else:
        form = RTNoticeForm()
    return render(request, 'dashboard/rt_form.html', {'form': form, 'title': 'Add Research / Tech Notice', 'type': 'RT'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.change_rtnotice', raise_exception=True)
def rt_notice_edit(request, pk):
    notice = get_object_or_404(RTNotice, pk=pk)
    if request.method == 'POST':
        form = RTNoticeForm(request.POST, request.FILES, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, 'Notice updated successfully!')
            return redirect('dashboard:rt_list')
    else:
        form = RTNoticeForm(instance=notice)
    return render(request, 'dashboard/rt_form.html', {'form': form, 'title': 'Edit Notice', 'type': 'RT'})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.delete_rtnotice', raise_exception=True)
def rt_notice_delete(request, pk):
    notice = get_object_or_404(RTNotice, pk=pk)
    if request.method == 'POST':
        notice.delete()
        messages.success(request, 'Notice deleted successfully!')
        return redirect('dashboard:rt_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': notice, 'type': 'Research/Tech Notice'})

# --- HOMEPAGE STATS ---

@staff_member_required(login_url='/accounts/login/')
def edit_homepage_stats(request):
    from core.models import HomePageStats
    stats, created = HomePageStats.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = HomePageStatsForm(request.POST, instance=stats)
        if form.is_valid():
            form.save()
            messages.success(request, 'Homepage statistics updated!')
            return redirect('dashboard:home')
    else:
        form = HomePageStatsForm(instance=stats)
    return render(request, 'dashboard/rt_form.html', {
        'form': form, 
        'title': 'Edit Manual Statistics',
        'type': 'Stats'
    })

def logout_view(request):
    """Custom logout that supports GET for the security guard"""
    from django.contrib.auth import logout
    logout(request)
    next_url = request.GET.get('next', 'core:home')
    return redirect(next_url)

# --- CAROUSEL IMAGES CRUD ---

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.view_carouselimage', raise_exception=True)
def carousel_list(request):
    query = request.GET.get('q')
    images = CarouselImage.objects.all().order_by('order', '-created_at')
    if query:
        images = images.filter(Q(title__icontains=query) | Q(alt_text__icontains=query))
    return render(request, 'dashboard/carousel_list.html', {'images': images, 'query': query})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.add_carouselimage', raise_exception=True)
def carousel_create(request):
    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Carousel image added successfully!')
            return redirect('dashboard:carousel_list')
    else:
        form = CarouselImageForm()
    return render(request, 'dashboard/carousel_form.html', {'form': form, 'title': 'Add Carousel Image', 'image_url': None})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.change_carouselimage', raise_exception=True)
def carousel_edit(request, pk):
    image = get_object_or_404(CarouselImage, pk=pk)
    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            form.save()
            messages.success(request, 'Carousel image updated successfully!')
            return redirect('dashboard:carousel_list')
    else:
        form = CarouselImageForm(instance=image)
    image_url = None
    if image.image and image.image.name:
        try:
            image_url = image.image.url
        except Exception:
            image_url = None
    return render(request, 'dashboard/carousel_form.html', {'form': form, 'title': 'Edit Carousel Image', 'image_url': image_url})

@staff_member_required(login_url='/accounts/login/')
@permission_required('core.delete_carouselimage', raise_exception=True)
def carousel_delete(request, pk):
    image = get_object_or_404(CarouselImage, pk=pk)
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Carousel image deleted successfully!')
        return redirect('dashboard:carousel_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': image, 'type': 'Carousel Image'})

from django.utils.decorators import method_decorator

@method_decorator(staff_member_required(login_url='/accounts/login/'), name='dispatch')
class DashboardPasswordChangeView(PasswordChangeView):
    template_name = 'dashboard/password_change.html'
    success_url = reverse_lazy('dashboard:home')

    def form_valid(self, form):
        messages.success(self.request, 'Your password has been changed successfully!')
        return super().form_valid(form)

# --- IMPORT/EXPORT GENERIC VIEWS ---

MODEL_RESOURCE_MAP = {
    'projects': {
        'model': ResearchProject,
        'resource': ResearchProjectResource,
        'redirect': 'dashboard:projects_list',
        'title': 'Projects'
    },
    'publications': {
        'model': Publication,
        'resource': PublicationResource,
        'redirect': 'dashboard:publications_list',
        'title': 'Publications'
    },
    'team': {
        'model': TeamMember,
        'resource': TeamMemberResource,
        'redirect': 'dashboard:team_list',
        'title': 'Team Members'
    },
    'workshops': {
        'model': Workshop,
        'resource': WorkshopResource,
        'redirect': 'dashboard:workshops_list',
        'title': 'Workshops'
    },
    'tutorials': {
        'model': Tutorial,
        'resource': TutorialResource,
        'redirect': 'dashboard:tutorials_list',
        'title': 'Tutorials'
    },
    'impact': {
        'model': ImpactStory,
        'resource': ImpactStoryResource,
        'redirect': 'dashboard:impact_list',
        'title': 'Impact Stories'
    },
    'research_tech': {
        'model': RTNotice,
        'resource': RTNoticeResource,
        'redirect': 'dashboard:rt_list',
        'title': 'Research & Technology'
    },
}

@staff_member_required(login_url='/accounts/login/')
def export_data(request, model_type):
    if model_type not in MODEL_RESOURCE_MAP:
        messages.error(request, "Invalid model type for export.")
        return redirect('dashboard:home')
    
    config = MODEL_RESOURCE_MAP[model_type]
    resource = config['resource']()
    dataset = resource.export()
    
    format = request.GET.get('format', 'csv')
    if format == 'csv':
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{model_type}_export.csv"'
    elif format == 'xlsx':
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{model_type}_export.xlsx"'
    else:
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{model_type}_export.csv"'
        
    return response

@staff_member_required(login_url='/accounts/login/')
def import_data(request, model_type):
    if model_type not in MODEL_RESOURCE_MAP:
        messages.error(request, "Invalid model type for import.")
        return redirect('dashboard:home')
    
    config = MODEL_RESOURCE_MAP[model_type]
    
    if request.method == 'POST' and request.FILES.get('import_file'):
        resource = config['resource']()
        dataset = Dataset()
        new_items = request.FILES['import_file']
        
        try:
            if new_items.name.endswith('.csv'):
                imported_data = dataset.load(new_items.read().decode('utf-8'), format='csv')
            elif new_items.name.endswith('.xlsx'):
                imported_data = dataset.load(new_items.read(), format='xlsx')
            else:
                messages.error(request, "Unsupported file format. Please use CSV or XLSX.")
                return redirect(config['redirect'])
                
            result = resource.import_data(dataset, dry_run=True)  # Test the import
            
            if not result.has_errors():
                resource.import_data(dataset, dry_run=False)  # Actually import
                messages.success(request, f"Successfully imported data into {config['title']}.")
            else:
                messages.error(request, f"Errors occurred during import. Please check your file.")
        except Exception as e:
            messages.error(request, f"Import failed: {str(e)}")
            
        return redirect(config['redirect'])
        
    return render(request, 'dashboard/import_form.html', {
        'title': f"Import {config['title']}",
        'model_type': model_type,
        'back_url': config['redirect']
    })


# --- OTP PASSWORD RESET ---

import random
import time
import threading
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User

def send_otp_email_in_background(email, otp):
    """Sends the OTP email via Django SMTP backend (AWS SES) in a background thread."""
    try:
        from django.core.mail import EmailMessage, get_connection
        from django.conf import settings

        connection = get_connection()
        msg = EmailMessage(
            subject='Climatology Lab - Password Reset OTP',
            body=f'Your OTP for password reset is: {otp}\n\nThis code expires in 10 minutes.\n\nIf you did not request this, please ignore this email.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
            connection=connection,
        )
        msg.send(fail_silently=False)
        connection.close()
    except Exception as e:
        print(f"Error sending OTP email via SMTP: {e}")


def otp_request_view(request):
    """Step 1: Enter email, receive OTP."""
    if request.method == 'POST':
        form = OTPRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = str(random.randint(100000, 999999))
            request.session['reset_otp'] = otp
            request.session['reset_otp_email'] = email
            request.session['reset_otp_time'] = time.time()
            request.session['reset_otp_verified'] = False

            # Send OTP via email in background
            threading.Thread(
                target=send_otp_email_in_background,
                args=(email, otp)
            ).start()
            
            messages.info(request, f'A 6-digit OTP has been sent to {email}.')
            return redirect('dashboard:otp_verify')
    else:
        form = OTPRequestForm()
    return render(request, 'dashboard/password_reset_form.html', {'form': form})


def otp_verify_view(request):
    """Step 2: Verify the OTP."""
    stored_otp = request.session.get('reset_otp')
    otp_time = request.session.get('reset_otp_time')

    if not stored_otp or not otp_time:
        messages.error(request, 'Please request an OTP first.')
        return redirect('dashboard:password_reset')

    # Check expiry (10 minutes)
    if time.time() - otp_time > 600:
        for key in ['reset_otp', 'reset_otp_email', 'reset_otp_time', 'reset_otp_verified']:
            request.session.pop(key, None)
        messages.error(request, 'OTP has expired. Please request a new one.')
        return redirect('dashboard:password_reset')

    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            entered_otp = form.cleaned_data['otp']
            if entered_otp == stored_otp:
                request.session['reset_otp_verified'] = True
                messages.success(request, 'OTP verified! Please set your new password.')
                return redirect('dashboard:otp_set_password')
            else:
                messages.error(request, 'Invalid OTP. Please try again.')
    else:
        form = OTPVerifyForm()

    email = request.session.get('reset_otp_email', '')
    remaining = max(0, int(600 - (time.time() - otp_time)))
    return render(request, 'dashboard/password_reset_otp.html', {
        'form': form,
        'email': email,
        'remaining_seconds': remaining,
    })


def otp_set_password_view(request):
    """Step 3: Set new password after OTP verification."""
    if not request.session.get('reset_otp_verified'):
        messages.error(request, 'Please verify your OTP first.')
        return redirect('dashboard:password_reset')

    email = request.session.get('reset_otp_email')
    if not email:
        messages.error(request, 'Session expired. Please start over.')
        return redirect('dashboard:password_reset')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        messages.error(request, 'No account found with this email.')
        return redirect('dashboard:password_reset')

    if request.method == 'POST':
        form = OTPSetPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['new_password1'])
            user.save()
            # Clear session
            for key in ['reset_otp', 'reset_otp_email', 'reset_otp_time', 'reset_otp_verified']:
                request.session.pop(key, None)
            messages.success(request, 'Password reset successful! Please login with your new password.')
            return redirect('dashboard:password_reset_complete')
    else:
        form = OTPSetPasswordForm()

    return render(request, 'dashboard/password_reset_confirm.html', {'form': form})


# --- SUPABASE DIAGNOSTIC ---

@staff_member_required(login_url='/accounts/login/')
def supabase_test(request):
    """Diagnostic page to verify Supabase credentials."""
    import boto3
    from django.conf import settings
    from botocore.config import Config

    endpoint = settings.AWS_S3_ENDPOINT_URL
    region = settings.AWS_S3_REGION_NAME
    access_key = settings.AWS_S3_ACCESS_KEY_ID
    secret_key = settings.AWS_S3_SECRET_ACCESS_KEY
    bucket = settings.AWS_STORAGE_BUCKET_NAME

    secret_display = f"{secret_key[:4]}...{secret_key[-4:]} (length={len(secret_key)})" if len(secret_key) > 8 else f"(length={len(secret_key)}) — TOO SHORT!"

    status = 'unknown'
    error_msg = ''
    try:
        s3 = boto3.client(
            's3',
            endpoint_url=endpoint,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        s3.head_bucket(Bucket=bucket)
        status = 'ok'
    except Exception as e:
        status = 'error'
        error_msg = str(e)

    from django.http import HttpResponse
    color = '#2ecc71' if status == 'ok' else '#e74c3c'
    html = f"""
    <html><head><title>Supabase Test</title></head>
    <body style="font-family:monospace;padding:30px;background:#1a1a2e;color:#eee;">
    <h2>🔍 Supabase Storage Diagnostics</h2>
    <table style="border-collapse:collapse;">
      <tr><td style="padding:8px;color:#aaa;">ENDPOINT</td><td style="padding:8px;">{endpoint or '(empty)'}</td></tr>
      <tr><td style="padding:8px;color:#aaa;">REGION</td><td style="padding:8px;">{region or '(empty)'}</td></tr>
      <tr><td style="padding:8px;color:#aaa;">ACCESS_KEY</td><td style="padding:8px;">{access_key or '(empty)'}</td></tr>
      <tr><td style="padding:8px;color:#aaa;">SECRET_KEY</td><td style="padding:8px;">{secret_display}</td></tr>
      <tr><td style="padding:8px;color:#aaa;">BUCKET</td><td style="padding:8px;">{bucket or '(empty)'}</td></tr>
      <tr><td style="padding:8px;color:#aaa;">use_supabase</td><td style="padding:8px;">{'True' if (endpoint and access_key and secret_key) else 'False — missing credentials!'}</td></tr>
    </table>
    <h3 style="color:{color};">Connection: {'✅ SUCCESS' if status == 'ok' else '❌ FAILED'}</h3>
    {f'<pre style="color:#e74c3c;background:#2a2a2a;padding:15px;border-radius:6px;">{error_msg}</pre>' if error_msg else ''}
    <br><a href="/dashboard/" style="color:#3498db;">← Back to Dashboard</a>
    </body></html>
    """
    return HttpResponse(html)
