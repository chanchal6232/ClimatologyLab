from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import EmailMessage, get_connection
from django.template.loader import render_to_string
from django.conf import settings
from .models import ContactSubmission
import threading

def send_contact_emails_in_background(name, email, phone, query, submission_id):
    """Sends both admin notification and user auto-reply via Django SMTP backend (AWS SES) in background."""
    try:
        from django.core.mail import EmailMessage, get_connection

        connection = get_connection()
        connection.open()

        # Admin notification email
        admin_msg = EmailMessage(
            subject=f'New Contact Form Submission from {name}',
            body=f"New contact form submission received:\n\nName: {name}\nEmail: {email}\nPhone: {phone if phone else 'Not provided'}\n\nMessage/Query:\n{query}\n\n---\nSubmission ID: {submission_id}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
            connection=connection,
        )

        # User auto-reply email
        user_msg = EmailMessage(
            subject='Thank You for Contacting Climatology Lab',
            body=f"Dear {name},\n\nThank you for connecting with us. We have received your query and will get back to you soon.\n\nYour Query:\n{query}\n\nWe appreciate your interest in the Climatology Lab and will respond as quickly as possible.\n\nBest regards,\nClimatology Lab",
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email],
            connection=connection,
        )

        connection.send_messages([admin_msg, user_msg])
        connection.close()

    except Exception as e:
        print(f"Error sending contact emails via SMTP: {e}")

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
