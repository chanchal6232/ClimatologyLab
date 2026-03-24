import os
import sys
import django

# Add current directory to path
sys.path.append(os.getcwd())

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from team.models import TeamMember

# Three paragraphs content
para1 = "Dr. Mahua Mukherjee is a Professor in the Department of Architecture and Planning at IIT Roorkee with extensive expertise in disaster mitigation, sustainable architecture, and urban resilience. She has over two decades of experience in teaching, research, and academic leadership, including serving as the Head of the Centre of Excellence in Disaster Mitigation and Management (CoEDMM). "
para2 = "Her research focuses on climate-responsive design, earthquake-resistant structures, and the development of sustainable and safe habitats. She has been actively involved in national and international research collaborations, consultancy projects, and has delivered numerous invited lectures and workshops. "
para3 = "With a strong academic background, including a PhD from Jadavpur University and international research exposure, she continues to contribute significantly to academia, research, and policy development in resilient and sustainable built environments."

bio_content = f"{para1}\n\n{para2}\n\n{para3}"

try:
    # Use name icontains to be safe with Dr. prefix
    member = TeamMember.objects.filter(name__icontains="Mahua Mukherjee").first()
    if member:
        member.bio = bio_content
        member.save()
        print(f"Successfully updated bio for {member.name}")
    else:
        print("Professor Mahua Mukherjee not found in database.")
except Exception as e:
    print(f"Error updating database: {e}")
