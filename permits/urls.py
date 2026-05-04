from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create-request/', views.create_request, name='create_request'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('manager/panel/', views.manager_panel, name='manager_panel'),
    path('gm/panel/', views.gm_panel, name='gm_panel'),
    path('security/panel/', views.security_panel, name='security_panel'),
    path('requests/<int:pk>/review/<str:action>/', views.review_request, name='review_request'),
    path('security/capture/<int:pk>/', views.security_capture, name='security_capture'),
]
