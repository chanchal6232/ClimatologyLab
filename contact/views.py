from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives, get_connection, EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from .models import ContactSubmission
import threading

def send_contact_emails_in_background(name, email, phone, query, submission_id):
    """Sends both admin notification and user auto-reply over the Resend HTTP API in the background."""
    try:
        import resend
        from django.conf import settings
        
        resend.api_key = getattr(settings, "RESEND_API_KEY", "")
        if not resend.api_key:
            from django.core.mail import EmailMessage, get_connection
            # Fallback to local console/SMTP if testing without Resend API key config
            connection = get_connection()
            connection.open()
            admin_msg = EmailMessage(
                f'New Contact Form Submission from {name}',
                f"Name: {name}\nEmail: {email}\nPhone: {phone}\nQuery:\n{query}",
                settings.DEFAULT_FROM_EMAIL,
                [settings.ADMIN_EMAIL],
                connection=connection,
            )
            user_msg = EmailMessage(
                'Thank You for Contacting Climatology Lab',
                f"Dear {name},\n\nWe have received your query and will get back to you soon.\n\nQuery:\n{query}",
                settings.DEFAULT_FROM_EMAIL,
                [email],
                connection=connection,
            )
            connection.send_messages([admin_msg, user_msg])
            connection.close()
            return
        # Resend API - Admin email
        try:
            resend.Emails.send({
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": [settings.ADMIN_EMAIL],
                "subject": f'New Contact Form Submission from {name}',
                "text": f"New contact form submission received:\n\nName: {name}\nEmail: {email}\nPhone: {phone if phone else 'Not provided'}\n\nMessage/Query:\n{query}\n\n---\nSubmission ID: {submission_id}",
            })
        except Exception as admin_err:
            print(f"Error sending Admin notification via Resend: {admin_err}")
        
        # Resend API - User email
        try:
            resend.Emails.send({
                "from": settings.DEFAULT_FROM_EMAIL,
                "to": [email],
                "subject": 'Thank You for Contacting Climatology Lab',
                "text": f"Dear {name},\n\nThank you for connecting with us. We have received your query and will get back to you soon.\n\nYour Query:\n{query}\n\nWe appreciate your interest in the Climatology Lab and will respond as quickly as possible.\n\nBest regards,\nClimatology Lab",
            })
        except Exception as user_err:
            print(f"Error sending User auto-reply via Resend: {user_err}")
            
    except Exception as e:
        print(f"Critical error in contact background thread: {e}")

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
