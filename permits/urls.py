from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('requests/<int:pk>/', views.request_detail, name='request_detail'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/<int:pk>/<str:action>/', views.review_request, name='review_request'),
]
