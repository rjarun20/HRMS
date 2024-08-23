from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # Include all accounts URLs
    path('', lambda request: redirect('accounts:login'), name='root'),  # Redirect root to login
]
