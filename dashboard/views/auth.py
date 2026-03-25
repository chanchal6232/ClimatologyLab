import random
import string
from datetime import timedelta

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.utils import timezone

from dashboard.forms import PasswordResetForm, OTPVerifyForm, OTPSetPasswordForm

User = get_user_model()

def password_reset_request(request):
    """Initial request for password reset (email entry)"""
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Find all users with this email (if multiple exist)
            users = User.objects.filter(email=email)
            if users.exists():
                otp = ''.join(random.choices(string.digits, k=6))
                request.session['reset_otp'] = otp
                request.session['reset_otp_email'] = email
                request.session['reset_otp_time'] = timezone.now().isoformat()
                
                # Send email
                send_mail(
                    'Your Password Reset OTP - Climatology Lab',
                    f'Your OTP for password reset is: {otp}. It is valid for 10 minutes.',
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                
                messages.success(request, 'An OTP has been sent to your email.')
                return redirect('dashboard:password_reset_verify')
            else:
                messages.error(request, 'No account found with this email.')
    else:
        form = PasswordResetForm()
    return render(request, 'dashboard/password_reset.html', {'form': form})

def password_reset_verify(request):
    """Verify the OTP sent via email"""
    otp_session = request.session.get('reset_otp')
    email = request.session.get('reset_otp_email')
    otp_time_str = request.session.get('reset_otp_time')

    if not all([otp_session, email, otp_time_str]):
        messages.error(request, 'Session expired. Please request a new OTP.')
        return redirect('dashboard:password_reset')

    otp_time = timezone.datetime.fromisoformat(otp_time_str)
    if timezone.now() > otp_time + timedelta(minutes=10):
        messages.error(request, 'OTP expired. Please request a new one.')
        return redirect('dashboard:password_reset')

    if request.method == 'POST':
        form = OTPVerifyForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['otp'] == otp_session:
                request.session['reset_otp_verified'] = True
                return redirect('dashboard:password_reset_confirm')
            else:
                messages.error(request, 'Invalid OTP.')
    else:
        form = OTPVerifyForm()

    return render(request, 'dashboard/password_reset_verify.html', {'form': form, 'email': email})

def password_reset_confirm(request):
    """Final step: Set new password"""
    if not request.session.get('reset_otp_verified'):
        messages.error(request, 'Please verify your OTP first.')
        return redirect('dashboard:password_reset_verify')

    email = request.session.get('reset_otp_email')
    user = User.objects.filter(email=email).first()
    
    if not user:
        messages.error(request, 'No account found with this email.')
        return redirect('dashboard:password_reset')

    if request.method == 'POST':
        form = OTPSetPasswordForm(request.POST)
        if form.is_valid():
            users = User.objects.filter(email=email)
            for u in users:
                u.set_password(form.cleaned_data['new_password1'])
                u.save()
            
            for key in ['reset_otp', 'reset_otp_email', 'reset_otp_time', 'reset_otp_verified']:
                request.session.pop(key, None)
            messages.success(request, 'Password reset successful! Please login with your new password.')
            return redirect('dashboard:login')
    else:
        form = OTPSetPasswordForm()

    return render(request, 'dashboard/password_reset_confirm.html', {'form': form})

from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

class DashboardPasswordChangeView(PasswordChangeView):
    template_name = 'dashboard/password_change.html'
    success_url = reverse_lazy('dashboard:home')
    
    def form_valid(self, form):
        messages.success(self.request, "Your password has been changed successfully.")
        return super().form_valid(form)
