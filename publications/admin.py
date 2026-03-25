import re
from django.contrib import admin
from django import forms
from datetime import datetime
from import_export import resources, fields, widgets
from import_export.widgets import DateWidget
from .models import Publication, Journal, Conference, Book, Guideline, OtherDocument
from core.admin_base import BaseAdmin

class FlexibleDateWidget(DateWidget):
    """Widget to handle multiple date formats and extraction from text."""
    def clean(self, value, row=None, *args, **kwargs):
        if not value:
            # Try to extract year from citation if date is missing
            citation = row.get('DATA', '')
            year_match = re.search(r'\((\d{4})\)', citation)
            if year_match:
                return datetime(int(year_match.group(1)), 1, 1).date()
            return None
        
        # Try common formats
        formats = ['%Y-%m-%d', '%b %d, %Y', '%d-%m-%Y', '%d/%m/%Y', '%m/%d/%Y']
        for fmt in formats:
            try:
                return datetime.strptime(str(value).strip(), fmt).date()
            except (ValueError, TypeError):
                continue
        return super().clean(value, row, *args, **kwargs)

class PublicationResource(resources.ModelResource):
    # Map CSV columns (case-insensitive mapping handled in before_import_row)
    citation = fields.Field(attribute='citation', column_name='DATA')
    publication_date = fields.Field(attribute='publication_date', column_name='DATE', widget=FlexibleDateWidget())
    external_link = fields.Field(attribute='external_link', column_name='LINK')
    title = fields.Field(attribute='title', column_name='TITLE')
    authors = fields.Field(attribute='authors', column_name='AUTHORS')
    
    def before_import(self, dataset, **kwargs):
        # 1. Normalize all headers to UPPERCASE to avoid "Column not found" errors
        dataset.headers = [str(h).upper().strip() for h in dataset.headers]
        
    def before_import_row(self, row, **kwargs):
        # 2. Flexible Column Mapping (Handle variations like "Publication date", "Authors List", etc.)
        mappings = {
            'DATE': ['PUBLICATION DATE', 'PUBLICATION YEAR', 'YEAR', 'DATE'],
            'AUTHORS': ['AUTHORS', 'AUTHOR', 'CONTRIBUTORS'],
            'TITLE': ['TITLE', 'NAME', 'PUBLICATION TITLE'],
            'LINK': ['LINK', 'URL', 'EXTERNAL LINK'],
            'DATA': ['DATA', 'CITATION', 'TEXT']
        }
        
        for standardized_key, variations in mappings.items():
            for key in list(row.keys()):
                if key.upper() in variations or any(v in key.upper() for v in variations):
                    if standardized_key not in row or not row[standardized_key]:
                        row[standardized_key] = row[key]
                    break

        # 2. Category Normalization
        category = str(row.get('Category', row.get('category', ''))).lower()
        if 'conference' in category:
            row['category'] = 'conference'
        elif 'journal' in category:
            row['category'] = 'journal'
        elif 'book' in category:
            row['category'] = 'book'

        # 3. Extract Title and Authors from Citation (DATA) if missing
        citation = row.get('DATA', '')
        if citation:
            parts = [p.strip() for p in citation.split('.') if p.strip()]
            if not row.get('TITLE') or row.get('TITLE') == row.get('DATA'):
                if parts: row['TITLE'] = parts[0][:499]
                
            if not row.get('AUTHORS') or row.get('AUTHORS') == "Unknown Authors":
                for part in parts:
                    if re.search(r'\(\d{4}\)', p := str(part)):
                        author_part = p.split('(')[0].strip()
                        if author_part:
                            row['AUTHORS'] = author_part
                            break
    class Meta:
        model = Publication
        fields = ('id', 'citation', 'publication_date', 'external_link', 'title', 'authors', 'journal', 'category', 'scope')
        import_id_fields = ('title',)
        skip_unchanged = True

# Category-specific resources to ensure correct assignment during import
class JournalResource(PublicationResource):
    def before_import_row(self, row, **kwargs):
        super().before_import_row(row, **kwargs)
        row['category'] = 'journal'

class BookResource(PublicationResource):
    def before_import_row(self, row, **kwargs):
        super().before_import_row(row, **kwargs)
        row['category'] = 'book'

class ConferenceResource(PublicationResource):
    def before_import_row(self, row, **kwargs):
        super().before_import_row(row, **kwargs)
        row['category'] = 'conference'

class ThesisResource(PublicationResource):
    def before_import_row(self, row, **kwargs):
        super().before_import_row(row, **kwargs)
        row['category'] = 'thesis'

class GuidelineResource(PublicationResource):
    def before_import_row(self, row, **kwargs):
        super().before_import_row(row, **kwargs)
        row['category'] = 'guideline'

@admin.register(Publication)
class PublicationAdmin(BaseAdmin):
    resource_class = PublicationResource
    list_display = ['title', 'journal', 'publication_date', 'category', 'scope', 'is_featured', 'is_active']
    list_filter = ['category', 'scope', 'is_featured', 'is_active', 'publication_date']
    search_fields = ['title', 'authors', 'journal', 'doi', 'abstract']
    actions = ['fix_misplaced_categories']

    @admin.action(description="Fix categories based on 'journal' field name")
    def fix_misplaced_categories(self, request, queryset):
        # Emergency fix for "Unknown Authors" and misplaced book chapters
        count = 0
        for obj in queryset:
            if 'chapter' in obj.citation.lower() or 'book' in obj.citation.lower():
                obj.category = 'book'
                obj.save()
                count += 1
        self.message_user(request, f"Updated {count} publications to Book Chapters.")

class BaseProxyAdmin(PublicationAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(category=self.category_value)
    def save_model(self, request, obj, form, change):
        obj.category = self.category_value
        super().save_model(request, obj, form, change)

@admin.register(Journal)
class JournalAdmin(BaseProxyAdmin):
    category_value = 'journal'
    resource_class = JournalResource

@admin.register(Conference)
class ConferenceAdmin(BaseProxyAdmin):
    category_value = 'conference'
    resource_class = ConferenceResource

@admin.register(Book)
class BookAdmin(BaseProxyAdmin):
    category_value = 'book'
    resource_class = BookResource

@admin.register(Guideline)
class GuidelineAdmin(BaseProxyAdmin):
    category_value = 'guideline'
    resource_class = GuidelineResource

@admin.register(OtherDocument)
class OtherDocumentAdmin(BaseProxyAdmin):
    category_value = 'other'
