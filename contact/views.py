from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import ContactSubmission
import threading

def send_contact_emails_in_background(name, email, phone, query, submission_id):
    """Sends both admin notification and user auto-reply over a single SMTP connection in the background."""
    try:
        from django.core.mail import EmailMessage, get_connection
        # Create a new connection since this is a new thread
        connection = get_connection()
        connection.open()
        
        # Admin email
        admin_subject = f'New Contact Form Submission from {name}'
        admin_message = f"""
New contact form submission received:

Name: {name}
Email: {email}
Phone: {phone if phone else 'Not provided'}

Message/Query:
{query}

---
This email was sent from the Climatology Lab website contact form.
Submission ID: {submission_id}
        """
        
        msg1 = EmailMessage(
            admin_subject,
            admin_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            connection=connection,
        )
        
        # User auto-reply
        user_subject = 'Thank You for Contacting Climatology Lab'
        user_message = f"""
Dear {name},

Thank you for connecting with us. We have received your query and will get back to you soon.

Your Query:
{query}

We appreciate your interest in the Climatology Lab and will respond to your inquiry as quickly as possible.

Best regards,
Climatology Lab
IIT Roorkee

---
This is an automated acknowledgment email. Please do not reply to this email.
If you have additional questions, please submit a new query through our website.
        """
        
        msg2 = EmailMessage(
            user_subject,
            user_message,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            connection=connection,
        )
        
        connection.send_messages([msg1, msg2])
        connection.close()
        
    except Exception as e:
        print(f"Error sending contact emails in background: {e}")

def contact_submit(request):
    """Handle contact form submission with email notifications"""
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone', '')
        query = request.POST.get('query')
        
        # Create contact submission
        submission = ContactSubmission.objects.create(
            name=name,
            email=email,
            phone=phone,
            query=query
        )
        
        # Trigger background email task
        threading.Thread(
            target=send_contact_emails_in_background,
            args=(name, email, phone, query, submission.id)
        ).start()
        
        messages.success(request, 'Thank you for contacting us! We have sent a confirmation email to your address.')
        return redirect('core:home')
    
    return redirect('core:home')
