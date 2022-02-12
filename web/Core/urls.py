from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView, PasswordChangeDoneView
from django.urls import path, reverse_lazy
from Core.views import home, stats, upload


app_name = 'core'

urlpatterns = [
    path('', home.homepage_view, name="home"),
    path('login/', LoginView.as_view(template_name='Core/auth_login.html', extra_context={'title': 'Anmelden'}), name='login'),
    path('logout/', LogoutView.as_view(template_name='Core/auth_logout.html'), name='logout'),
    path('password-change/', PasswordChangeView.as_view(template_name='Core/auth_password_change.html', success_url=reverse_lazy('core:password-change-done')), name='password-change'),
    path('password-changed/', PasswordChangeDoneView.as_view(template_name='Core/auth_password_change_done.html'), name='password-change-done'),
    path('statistics/', stats.view, name="stats"),
    path('upload/', upload.upload_view, name="upload"),
]
