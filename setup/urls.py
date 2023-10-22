from django.urls import path
from . import views

urlpatterns = [
    path('edit/<int:event_id>/', views.edit),
    # path('edit/<int:event_id>/zones', views.edit_zones),
    path('delete/<int:event_id>/', views.delete),
    path('restore/<int:event_id>/', views.restore),
    path('new/', views.new),
    path('', views.setup),
]
