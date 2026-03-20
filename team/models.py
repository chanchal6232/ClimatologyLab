from django.db import models

class TeamMember(models.Model):
    """Team member information"""
    
    name = models.CharField(max_length=200)
    role = models.CharField(max_length=100, help_text="e.g., Professor, PhD Student, Research Associate")
    photo = models.ImageField(upload_to='team/', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    google_scholar_url = models.URLField(blank=True, verbose_name="Google Scholar URL")
    bio = models.TextField(blank=True, help_text="Short introduction/bio (especially for faculty)")
    order = models.IntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.role}"
