# dashboard/views.py
import random
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout as auth_logout, authenticate
from django.core.mail import send_mail
from .forms import CustomUserCreationForm
from .models import CustomUser, Report
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import io
from PIL import Image
import base64
import requests
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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

def report_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Get all reports for the current user
    reports = Report.objects.filter(user=request.user).order_by('-created_at')
    
    return render(request, 'reports/report_list.html', {
        'reports': reports
    })

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

def download_report(request):
    # Get the report data
    report_data = {
        'title': 'Sample Report',
        'content': 'This is a placeholder for the AI-generated report.',
        'date': '2024-03-20'
    }
    
    # Create a BytesIO buffer to receive PDF data
    buffer = BytesIO()
    
    # Create the PDF object
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    date_style = ParagraphStyle(
        'CustomDate',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.gray,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    # Create the content
    content = []
    content.append(Paragraph(report_data['title'], title_style))
    content.append(Paragraph(f"Generated on: {report_data['date']}", date_style))
    content.append(Spacer(1, 20))
    
    # Split content into paragraphs and add them
    for paragraph in report_data['content'].split('\n'):
        if paragraph.strip():
            content.append(Paragraph(paragraph, styles['Normal']))
            content.append(Spacer(1, 12))
    
    # Build the PDF
    doc.build(content)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{report_data["date"]}.pdf"'
    response.write(pdf)
    
    return response

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if user.is_verified:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Please verify your email before logging in.')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'registration/login.html')

@login_required
def dashboard(request):
    return render(request, 'reports/dashboard.html')

@login_required
def welcome_page(request):
    return render(request, 'reports/welcome.html')

@login_required
def powerbi_report(request):
    # Power BI report URL - replace with your actual Power BI report URL
    powerbi_url = "https://app.powerbi.com/reportEmbed?reportId=your-report-id"
    return render(request, 'reports/powerbi.html', {'powerbi_url': powerbi_url})

@login_required
def take_screenshot(request):
    if request.method == 'POST':
        # Get the screenshot data from the request
        screenshot_data = request.POST.get('screenshot')
        
        # Convert base64 to image
        image_data = base64.b64decode(screenshot_data.split(',')[1])
        image = Image.open(io.BytesIO(image_data))
        
        # Save the image temporarily
        image_path = 'media/screenshots/screenshot.png'
        image.save(image_path)
        
        # TODO: Add AI model integration here
        # For now, we'll just redirect to a placeholder report
        return redirect('generate_report')
    
    return render(request, 'reports/screenshot.html')

@login_required
def generate_report(request):
    # TODO: Add AI model integration to generate the report
    # For now, we'll use placeholder data
    report_data = {
        'title': 'Sample Report',
        'content': 'This is a placeholder for the AI-generated report.',
        'date': '2024-03-20'
    }
    
    return render(request, 'reports/generated_report.html', {'report': report_data})
