from django.urls import path
from .views import login_view, home_view, admin_dashboard, user_dashboard

urlpatterns = [
    path('login/', login_view, name='login'),
    path('home/', home_view, name='home'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/user/', user_dashboard, name='user_dashboard'),
]
