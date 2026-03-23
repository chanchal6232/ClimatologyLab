from import_export import resources, fields, widgets
from import_export.widgets import DateWidget, Widget
from .models import ResearchProject

class MapChoicesWidget(Widget):
    """Custom widget to map human-readable labels and common aliases to database keys"""
    def __init__(self, choices, *args, **kwargs):
        # Create a lowercase map from the model choices
        self.choices_map = {str(label).strip().lower(): key for key, label in choices}
        
        # Add common aliases found in CSVs
        aliases = {
            'pi': 'pi',
            'co-pi': 'co-pi',
            'copi': 'co-pi',
            'principal investigator': 'pi',
            'co-principal investigator': 'co-pi',
            'research project': 'research',
            'consultancy project': 'consultancy',
            'ongoing': 'ongoing',
            'completed': 'completed',
            'collaborator': 'team_member',
            'project team member': 'team_member',
        }
        for alias, key in aliases.items():
            if alias not in self.choices_map:
                self.choices_map[alias] = key
                
        super().__init__(*args, **kwargs)
    
    def clean(self, value, row=None, *args, **kwargs):
        if not value or str(value).strip() in ['---', '', 'None']:
            return None
        
        val_lower = str(value).strip().lower()
        # Return the key if found in the map, otherwise return the original value
        return self.choices_map.get(val_lower, value)

class ResearchProjectResource(resources.ModelResource):
    """Import/Export resource for ResearchProject - optimized for current model"""
    
    # Map CSV columns to model fields
    title = fields.Field(attribute='title', column_name='TOPIC')
    description = fields.Field(attribute='description', column_name='DESCRIPTION')
    funding_agency = fields.Field(attribute='funding_agency', column_name='FUNDING AGENCY')
    grant_amount = fields.Field(attribute='grant_amount', column_name='GRANT AMOUNT')
    collaborators = fields.Field(attribute='collaborators', column_name='OTHER OFFICERS / COLLABORATORS')
    partner_institutions = fields.Field(attribute='partner_institutions', column_name='PARTNER INSTITUTIONS')
    
    # Support DD/MM/YYYY format as seen in latest screenshot
    start_date = fields.Field(
        attribute='start_date', 
        column_name='START DATE', 
        widget=DateWidget(format='%d/%m/%Y')
    )
    end_date = fields.Field(
        attribute='end_date', 
        column_name='END DATE', 
        widget=DateWidget(format='%d/%m/%Y')
    )
    
    # Use smarter MapChoicesWidget
    status = fields.Field(
        attribute='status', 
        column_name='STATUS', 
        widget=MapChoicesWidget(choices=ResearchProject.STATUS_CHOICES)
    )
    project_type = fields.Field(
        attribute='project_type', 
        column_name='PROJECT TYPE', 
        widget=MapChoicesWidget(choices=ResearchProject.PROJECT_TYPE_CHOICES)
    )
    role = fields.Field(
        attribute='role', 
        column_name='ROLE', 
        widget=MapChoicesWidget(choices=ResearchProject.ROLE_CHOICES)
    )

    class Meta:
        model = ResearchProject
        import_id_fields = ('title',)
        fields = (
            'title', 'description', 'funding_agency', 'grant_amount',
            'collaborators', 'partner_institutions', 'start_date', 'end_date',
            'status', 'role', 'project_type', 'is_active'
        )
        skip_unchanged = True
        report_skipped = True
