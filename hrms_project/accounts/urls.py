from django.urls import path, include
from .views import auth_views, dashboard_views, user_views, employee_views, leave_views, kyc_views

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs (Flattening)
    path('login/', auth_views.login_view, name='login'),
    path('logout/', auth_views.logout_view, name='logout'),

    # Dashboard URLs
    path('dashboard/', include([
        path('', dashboard_views.home_view, name='home'),
        path('admin/', dashboard_views.admin_dashboard, name='admin_dashboard'),
        path('user/', dashboard_views.user_dashboard, name='user_dashboard'),
    ])),
    
    # User management URLs
    path('users/', include([
        path('create/', user_views.create_user_view, name='create_user'),
        path('list/', user_views.list_users, name='list_users'),
        path('update/<str:user_id>/', user_views.update_user, name='update_user'),
        path('delete/<str:user_id>/', user_views.delete_user, name='delete_user'),
        path('api/proxy-supabase/', user_views.proxy_supabase, name='proxy_supabase'),
    ])),
    
    # Employee URLs
    path('employees/', include([
        path('add/', employee_views.add_employee, name='add_employee'),
        path('list/', employee_views.list_employees, name='list_employees'),
    ])),
    
    # Leave management URLs
    path('leaves/', include([
        path('approve/', leave_views.approve_leaves, name='approve_leaves'),
        path('reports/', leave_views.leave_reports, name='leave_reports'),
    ])),
    
    # KYC URLs
    path('kyc/', include([
        path('pending/', kyc_views.pending_kyc, name='pending_kyc'),
        path('reports/', kyc_views.kyc_reports, name='kyc_reports'),
    ])),
]
