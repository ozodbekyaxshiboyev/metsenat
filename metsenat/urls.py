from django.urls import path,include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views

from .views import *


router = DefaultRouter()
router.register('otm',OtmViewSet,'otm')


urlpatterns = [
    path('', include(router.urls)),
    path('sponsor/',SponsorListCreateApiView.as_view(),name='sponsor'),
    path('sponsor/info/',SponsorDetailApiView.as_view(),name='sponsor-info'),

    path('student/',StudentListCreateApiView.as_view(),name='student'),
    path('student/info/',StudentDetailDestroyApiView.as_view(),name='student-info'),

    path('student/support/',StudentSupportApiView.as_view(),name='student-support'),
    path('student/add-sponsor/',SponsorAddApiView.as_view(),name='add-sponsor'),

    path('dashboard/',DashboardApiView.as_view(),name='dashboard'),

    path('register/', RegisterView.as_view(), name='auth_register'),
    path('auth/',views.obtain_auth_token), 
]
