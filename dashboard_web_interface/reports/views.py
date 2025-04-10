# dashboard/views.py
import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout as auth_logout
from django.core.mail import send_mail
from .forms import CustomUserCreationForm
from .models import CustomUser, Report
from django.utils import timezone

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if not email.lower().endswith('@apo.com.tn'):
                form.add_error('email', 'Email must be an @apo.com.tn address.')
            else:
                # Create user but mark as inactive until email verification
                user = form.save(commit=False)
                verification_code = str(random.randint(100000, 999999))
                user.verification_code = verification_code
                user.is_verified = False
                user.is_active = False  # Prevent login until verified
                user.save()

                # Send verification email
                send_mail(
                    'Verify your APO account',
                    f'Your verification code is: {verification_code}',
                    'no-reply@yourdomain.com',  # Replace with your sending email
                    [email],
                    fail_silently=False,
                )
                # Store user ID in session to use in verification
                request.session['new_user_id'] = user.id
                return redirect('verify_email')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# dashboard/views.py (continued)
from django.contrib.auth import get_user_model

def verify_email(request):
    error = None
    if request.method == 'POST':
        code = request.POST.get('code')
        user_id = request.session.get('new_user_id')
        User = get_user_model()
        try:
            user = User.objects.get(id=user_id)
            if user.verification_code == code:
                user.is_verified = True
                user.is_active = True  # Activate the account
                user.verification_code = ''
                user.save()
                login(request, user)
                return redirect('dashboard')
            else:
                error = 'Invalid verification code.'
        except User.DoesNotExist:
            error = 'User not found.'
    return render(request, 'registration/verify_email.html', {'error': error})

# dashboard/views.py (continued)
def logout_view(request):
    if request.user.is_authenticated:
        request.user.last_logout = timezone.now()
        request.user.save()
    auth_logout(request)
    return redirect('login')

# dashboard/views.py (process_screenshot view update)
import base64, os, json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Import your AI analysis function (assuming it takes the image path and returns text)
"""from report_ai import analyze_screenshot  

@csrf_exempt  # In production, ensure proper CSRF handling
def process_screenshot(request):
    if request.method == 'POST' and request.user.is_authenticated:
        data = json.loads(request.body)
        image_data = data.get('image')
        if image_data:
            header, encoded = image_data.split(',', 1)
            binary_data = base64.b64decode(encoded)
            screenshot_path = os.path.join(settings.BASE_DIR, 'dashboard', 'temp_screenshot.png')
            with open(screenshot_path, 'wb') as f:
                f.write(binary_data)

            # Run your AI analysis tool
            report_text = analyze_screenshot(screenshot_path)

            # Create a Report record linked to the user
            report = Report.objects.create(
                user=request.user,
                report_text=report_text
            )
            # Store report id in session for further PDF processing if needed
            request.session['report_id'] = report.id
            request.session['report_text'] = report_text

            return JsonResponse({'report_url': '/report/'})
    return JsonResponse({'error': 'Invalid request or not authenticated.'}, status=400)
"""

# dashboard/views.py (continued)
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

def download_pdf(request):
    report_id = request.session.get('report_id')
    if report_id:
        try:
            report = Report.objects.get(id=report_id, user=request.user)
            # Render a template to HTML for PDF conversion
            html_string = render_to_string('pdf_report.html', {
                'report_text': report.report_text,
                'screenshot_path': request.session.get('screenshot_path', None)
            }, request=request)
            html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
            pdf = html.write_pdf()
            # Mark as downloaded
            report.downloaded = True
            report.save()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="dashboard_report.pdf"'
            return response
        except Report.DoesNotExist:
            pass
    return HttpResponse("Report not found.", status=404)
