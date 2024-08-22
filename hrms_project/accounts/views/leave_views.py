from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def approve_leaves(request):
    leave_requests = []  # Replace with actual query to fetch leave requests
    return render(request, 'accounts/approve_leaves.html', {'leave_requests': leave_requests})

@login_required
def leave_reports(request):
    reports = []  # Replace with actual logic to generate reports
    return render(request, 'accounts/leave_reports.html', {'reports': reports})