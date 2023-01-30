from django.urls import path
from .views import GoogleCalendarInitView, GoogleCalendarRedirectView


urlpatterns = [
    path('init/', GoogleCalendarInitView.as_view(), name='google_permission'),
    path('redirect/', GoogleCalendarRedirectView.as_view(), name='google_redirect')
]
