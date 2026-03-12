from django import forms
from projects.models import ResearchProject
from publications.models import Publication
from team.models import TeamMember
from workshops.models import Workshop
from core.models import (
    Tutorial, RTNotice, HomePageStats, CarouselImage, 
    ImpactStory, ResearchHighlight, PolicyImpact
)

class ImpactStoryForm(forms.ModelForm):
    class Meta:
        model = ImpactStory
        fields = ['title', 'category', 'description', 'impact_metrics', 'image', 'order', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ResearchHighlightForm(forms.ModelForm):
    class Meta:
        model = ResearchHighlight
        fields = ['title', 'icon', 'description', 'link', 'order', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class PolicyImpactForm(forms.ModelForm):
    class Meta:
        model = PolicyImpact
        fields = ['year', 'title', 'description', 'organization', 'order', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class CarouselImageForm(forms.ModelForm):
    class Meta:
        model = CarouselImage
        fields = ['title', 'image', 'alt_text', 'order', 'is_active']
        widgets = {
            'alt_text': forms.TextInput(attrs={'placeholder': 'Accessibility description'}),
        }

class ProjectForm(forms.ModelForm):
    class Meta:
        model = ResearchProject
        fields = [
            'title', 'description', 'project_type', 'status', 
            'funding_agency', 'grant_amount', 'image', 'external_link',
            'role', 'collaborators', 'partner_institutions', 
            'start_date', 'end_date', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = [
            'title', 'authors', 'category', 'scope', 
            'journal', 'publication_date', 'citation', 
            'abstract', 'pdf_file', 'external_link',
            'is_featured', 'is_active'
        ]
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'abstract': forms.Textarea(attrs={'rows': 4}),
        }

class TeamMemberForm(forms.ModelForm):
    class Meta:
        model = TeamMember
        fields = [
            'name', 'role', 'photo', 'email', 
            'linkedin_url', 'google_scholar_url', 'order', 'is_active'
        ]

class WorkshopForm(forms.ModelForm):
    class Meta:
        model = Workshop
        fields = [
            'title', 'description', 'event_date', 'link', 'is_active'
        ]
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class TutorialForm(forms.ModelForm):
    class Meta:
        model = Tutorial
        fields = [
            'title', 'external_link', 'playlist_id', 
            'is_playlist', 'lecture_number', 'order', 'is_active'
        ]
        widgets = {
            'external_link': forms.TextInput(attrs={'placeholder': 'YouTube URL or external link'}),
        }
        help_texts = {
            'external_link': 'YouTube link or external website URL',
            'playlist_id': 'ID to group videos into a playlist (e.g., urban-ecosystem)',
            'is_playlist': 'Check this if this entry is the main playlist container',
        }

class RTNoticeForm(forms.ModelForm):
    class Meta:
        model = RTNotice
        fields = ['notice_type', 'title', 'description', 'event_date', 'link', 'image', 'is_active']
        labels = {
            'notice_type': 'Category',
            'title': 'Research Focus / Technology Name',
            'description': 'Description/Brief',
            'event_date': 'Initiated / Adoption Date',
            'link': 'Project/Doc Link (Optional)',
        }
        widgets = {
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
from django.core.exceptions import ValidationError

class OTPRequestForm(forms.Form):
    """Form to request an OTP - restricted to official lab email only."""
    email = forms.EmailField(
        label='Email Address',
        widget=forms.EmailInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Enter your registered email'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email != 'climatologylab@ar.iitr.ac.in':
            raise ValidationError("Password reset is only allowed for the official lab email.")
        return email


class OTPVerifyForm(forms.Form):
    """Form to enter and verify the 6-digit OTP."""
    otp = forms.CharField(
        label='Enter OTP',
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg text-center fw-bold',
            'placeholder': '------',
            'maxlength': '6',
            'style': 'letter-spacing: 12px; font-size: 1.8rem;',
            'autocomplete': 'off',
            'inputmode': 'numeric',
        })
    )


class OTPSetPasswordForm(forms.Form):
    """Form to set a new password after OTP verification."""
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter new password'
        })
    )
    new_password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('new_password1')
        p2 = cleaned_data.get('new_password2')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data

class HomePageStatsForm(forms.ModelForm):
    class Meta:
        model = HomePageStats
        fields = ['publications_count', 'projects_count', 'outreach_programs_count', 'years_of_research']
        labels = {
            'publications_count': 'Manual Publication Count (if needed)',
            'projects_count': 'Manual Project Count (if needed)',
            'outreach_programs_count': 'Manual outreach count (if needed)',
            'years_of_research': 'Years of Research (Manual)',
        }
        widgets = {
            'years_of_research': forms.NumberInput(attrs={'class': 'form-control'}),
        }
