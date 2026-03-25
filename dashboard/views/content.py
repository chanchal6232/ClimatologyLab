from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from core.models import HomePageStats, CarouselImage, HomePageContent
from dashboard.forms import HomePageStatsForm, CarouselImageForm

# Define HomePageContentForm inline if it's missing in dashboard.forms
class HomePageContentForm(forms.ModelForm):
    class Meta:
        model = HomePageContent
        fields = ['welcome_title', 'welcome_text', 'professor_name', 'is_active']
        widgets = {
            'welcome_text': forms.Textarea(attrs={'rows': 5}),
        }

@login_required
def homepage_stats_update(request):
    """Update homepage stats"""
    stats, created = HomePageStats.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = HomePageStatsForm(request.POST, instance=stats)
        if form.is_valid():
            form.save()
            messages.success(request, "Homepage stats updated successfully.")
            return redirect('dashboard:home')
    else:
        form = HomePageStatsForm(instance=stats)
    return render(request, 'dashboard/carousel_form.html', {'form': form, 'action': 'Update Stats'})

@login_required
def homepage_content_update(request):
    """Update homepage text content"""
    content, created = HomePageContent.objects.get_or_create(pk=1)
    if request.method == 'POST':
        form = HomePageContentForm(request.POST, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, "Homepage content updated successfully.")
            return redirect('dashboard:home')
    else:
        form = HomePageContentForm(instance=content)
    return render(request, 'dashboard/carousel_form.html', {'form': form, 'action': 'Update Content'})

@login_required
def carousel_list(request):
    """List carousel images"""
    images = CarouselImage.objects.all().order_by('order')
    return render(request, 'dashboard/carousel_list.html', {'images': images})

@login_required
def carousel_add(request):
    """Add a new carousel image"""
    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES)
        if form.is_valid():
            image = form.save()
            messages.success(request, "Carousel image added successfully.")
            return redirect('dashboard:carousel_list')
    else:
        form = CarouselImageForm()
    return render(request, 'dashboard/carousel_form.html', {'form': form, 'action': 'Add'})

@login_required
def carousel_edit(request, pk):
    """Edit a carousel image"""
    image = get_object_or_404(CarouselImage, pk=pk)
    if request.method == 'POST':
        form = CarouselImageForm(request.POST, request.FILES, instance=image)
        if form.is_valid():
            image = form.save()
            messages.success(request, "Carousel image updated successfully.")
            return redirect('dashboard:carousel_list')
    else:
        form = CarouselImageForm(instance=image)
    return render(request, 'dashboard/carousel_form.html', {'form': form, 'action': 'Edit', 'image': image})

@login_required
def carousel_delete(request, pk):
    """Delete a carousel image"""
    image = get_object_or_404(CarouselImage, pk=pk)
    if request.method == 'POST':
        image.delete()
        messages.success(request, "Carousel image deleted successfully.")
        return redirect('dashboard:carousel_list')
    return render(request, 'dashboard/confirm_delete.html', {'object': image, 'back_url': 'dashboard:carousel_list'})
