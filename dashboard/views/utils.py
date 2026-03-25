import boto3
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from botocore.config import Config

@staff_member_required(login_url='/accounts/login/')
def supabase_test(request):
    """Diagnostic page to verify Supabase credentials."""
    endpoint = settings.AWS_S3_ENDPOINT_URL
    region = settings.AWS_S3_REGION_NAME
    access_key = settings.AWS_S3_ACCESS_KEY_ID
    secret_key = settings.AWS_S3_SECRET_ACCESS_KEY
    bucket = settings.AWS_STORAGE_BUCKET_NAME

    secret_display = f"{secret_key[:4]}...{secret_key[-4:]} (length={len(secret_key)})" if len(secret_key) > 8 else f"(length={len(secret_key)}) — TOO SHORT!"

    status = 'unknown'
    error_msg = ''
    try:
        s3 = boto3.client(
            's3',
            endpoint_url=endpoint,
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            config=Config(signature_version='s3v4')
        )
        s3.head_bucket(Bucket=bucket)
        status = 'ok'
    except Exception as e:
        status = 'error'
        error_msg = str(e)

    color = '#2ecc71' if status == 'ok' else '#e74c3c'
    html = f"""
    <html><head><title>Supabase Test</title></head>
    <body style="font-family:monospace;padding:30px;background:#1a1a2e;color:#eee;">
    <h2>🔍 Supabase Storage Diagnostics</h2>
    <table style="border-collapse:collapse;">
      <tr><td style="padding:8px;color:#aaa;">ENDPOINT</td><td style="padding:8px;">{endpoint or '(empty)'}</td></tr>
      <tr><td style="padding:8px;color:#aaa;">REGION</td><td style="padding:8px;">{region or '(empty)'}</td></tr>
      <tr><td style="padding:8px;color:#aaa;">ACCESS_KEY</td><td style="padding:8px;">{access_key or '(empty)'}</td></tr>
      <tr><td style="padding:8px;color:#aaa;">SECRET_KEY</td><td style="padding:8px;">{secret_display}</td></tr>
      <tr><td style="padding:8px;color:#aaa;">BUCKET</td><td style="padding:8px;">{bucket or '(empty)'}</td></tr>
      <tr><td style="padding:8px;color:#aaa;">use_supabase</td><td style="padding:8px;">{'True' if (endpoint and access_key and secret_key) else 'False — missing credentials!'}</td></tr>
    </table>
    <h3 style="color:{color};">Connection: {'✅ SUCCESS' if status == 'ok' else '❌ FAILED'}</h3>
    {f'<pre style="color:#e74c3c;background:#2a2a2a;padding:15px;border-radius:6px;">{error_msg}</pre>' if error_msg else ''}
    <br><a href="/dashboard/" style="color:#3498db;">← Back to Dashboard</a>
    </body></html>
    """
    return HttpResponse(html)
