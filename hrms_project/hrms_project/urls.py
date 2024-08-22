from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', lambda request: redirect('login')),  # Redirect root URL to the login page
    # path('__debug__/', include('debug_toolbar.urls')),
]
