from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def pending_kyc(request):
    pending_applications = []  # Replace with actual logic to get pending KYC applications
    return render(request, 'accounts/pending_kyc.html', {'pending_applications': pending_applications})

@login_required
def kyc_reports(request):
    kyc_report_data = []  # Replace with actual logic to get KYC report data
    return render(request, 'accounts/kyc_reports.html', {'kyc_report_data': kyc_report_data})