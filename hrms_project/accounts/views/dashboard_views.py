from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def home_view(request):
    user_data = request.session.get('user')

    if user_data:
        if user_data['user_metadata'].get('is_admin'):
            return redirect('accounts:admin_dashboard')
        else:
            return redirect('accounts:user_dashboard')
    else:
        messages.error(request, "User data not found. Please log in again.")
        return redirect('accounts:login')
    
    
@login_required
def admin_dashboard(request):
    user_data = request.session.get('user')

    if user_data and user_data['user_metadata'].get('is_admin'):
        return render(request, 'accounts/admin_dashboard.html', {'user_data': user_data})
    else:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('accounts:home')

@login_required
def user_dashboard(request):
    user_data = request.session.get('user')
    return render(request, 'accounts/user_dashboard.html', {'user_data': user_data})