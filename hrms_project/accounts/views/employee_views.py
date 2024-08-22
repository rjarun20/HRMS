from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def add_employee(request):
    return render(request, 'accounts/add_employee.html')

@login_required
def list_employees(request):
    employees = []  # Replace with actual query to fetch employees
    return render(request, 'accounts/list_employees.html', {'employees': employees})