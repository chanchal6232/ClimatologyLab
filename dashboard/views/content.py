from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.models import HomePageStats, CarouselImage, HomePageContent
from dashboard.models import ActivityLog
from dashboard.forms import HomePageStatsForm, CarouselImageForm, HomePageContentForm

@login_required
def homepage_stats_update(request):
    """Update homepage stats"""
    stats, created = HomePageStats.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = HomePageStatsForm(request.POST, instance=stats)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Updated',
                model_name='HomePageStats',
                object_name='Global Stats'
            )
            messages.success(request, "Homepage stats updated successfully.")
            return redirect('dashboard:home')
    else:
        form = HomePageStatsForm(instance=stats)
    return render(request, 'dashboard/content/stats_form.html', {'form': form})

@login_required
def homepage_content_update(request):
    """Update homepage text content"""
    content, created = HomePageContent.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = HomePageContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Updated',
                model_name='HomePageContent',
                object_name='Hero/About Content'
            )
            messages.success(request, "Homepage content updated successfully.")
            return redirect('dashboard:home')
    else:
        form = HomePageContentForm(instance=content)
    return render(request, 'dashboard/content/homepage_content_form.html', {'form': form})

@login_required
def carousel_list(request):
    """List carousel images"""
    images = CarouselImage.objects.all().order_by('order')
    return render(request, 'dashboard/content/carousel_list.html', {'images': images})

@login_required
def carousel_add(request):
    """Add a new carousel image"""
    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Created',
                model_name='CarouselImage',
                object_id=image.id,
                object_name=image.title or "Carousel Image"
            )
            messages.success(request, "Carousel image added successfully.")
            return redirect('dashboard:carousel_list')
    else:
        form = CarouselImageForm()
    return render(request, 'dashboard/content/carousel_form.html', {'form': form, 'action': 'Add'})

@login_required
def carousel_edit(request, pk):
    """Edit a carousel image"""
    image = get_object_or_404(CarouselImage, pk=pk)
    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            image = form.save()
            ActivityLog.objects.create(
                user=request.user,
                action='Updated',
                model_name='CarouselImage',
                object_id=image.id,
                object_name=image.title or "Carousel Image"
            )
            messages.success(request, "Carousel image updated successfully.")
            return redirect('dashboard:carousel_list')
    else:
        form = CarouselImageForm(instance=image)
    return render(request, 'dashboard/content/carousel_form.html', {'form': form, 'action': 'Edit', 'image': image})

@login_required
def carousel_delete(request, pk):
    """Delete a carousel image"""
    image = get_object_or_404(CarouselImage, pk=pk)
    if request.method == 'POST':
        image_name = image.title or "Carousel Image"
        ActivityLog.objects.create(
            user=request.user,
            action='Deleted',
            model_name='CarouselImage',
            object_id=image.id,
            object_name=image_name
        )
        image.delete()
        messages.success(request, "Carousel image deleted successfully.")
        return redirect('dashboard:carousel_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': image, 'back_url': 'dashboard:carousel_list'})
