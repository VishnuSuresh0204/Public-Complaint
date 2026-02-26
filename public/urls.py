"""
URL configuration for public project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from myapp import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('register/', views.register_public),
    path('register_staff/', views.register_staff),
    path('login/', views.login_view),
    path('admin_home/', views.admin_home),
    path('admin_view_users/', views.admin_view_users),
    path('staff_home/', views.staff_home),
    path('citizen_home/', views.citizen_home),  
    path('admin_view_staff/', views.admin_view_staff),
    path('approve_staff/', views.approve_staff),
    path('view_staff/', views.admin_view_staff),
    path('admin_view_complaints/', views.admin_view_complaints),
    path('admin_add_department/', views.admin_add_department),
    path('admin_view_department/', views.admin_view_department),
    path('admin_edit_department/', views.admin_edit_department),
    path('admin_delete_department/', views.admin_delete_department),
    path('admin_view_feedback/', views.admin_view_feedbacks),
    path('admin_view_reports/', views.admin_view_reports),

    # Worker Registration and Management
    path('register_worker/', views.register_worker),
    path('admin_view_workers/', views.admin_view_workers),
    path('approve_worker/', views.approve_worker),
    path('reject_worker/', views.reject_worker),
    path('block_worker/', views.block_worker),
    path('unblock_worker/', views.unblock_worker),

    # Admin Citizen Management
    path('block_citizen/', views.block_citizen),
    path('unblock_citizen/', views.unblock_citizen),

    # Admin Staff Management
    path('block_staff/', views.block_staff),
    path('unblock_staff/', views.unblock_staff),
    path('reject_staff/', views.reject_staff),

    path('staff_my_profile/', views.my_profile),
    path('staff_complaints/', views.staff_complaints),
    path('staff_add_complaint_action/', views.add_complaint_action),
    path('staff_complaint_action_page/', views.staff_complaint_action_page),
    
    # Worker Assignment and Staff Verification
    path('staff_assign_worker/', views.staff_assign_worker),
    path('staff_verify_work_update/', views.staff_verify_work_update),

    # Worker Side
    path('worker_home/', views.worker_home),
    path('worker_view_assigned_works/', views.worker_view_assigned_works),
    path('worker_update_work_status/', views.worker_update_work_status),

    # Chat System
    path('chat/', views.chat_list),
    path('chat_messages/<int:receiver_id>/', views.chat_messages),

    path('citizen_add_complaint/', views.citizen_add_complaint),
    path('add_feedback/', views.add_feedback),
    path('user_view_complaints/', views.user_view_complaints),
    path('view_feedbacks/', views.view_feedbacks),
    path('edit_feedback/', views.edit_feedback),
    path('delete_feedback/', views.delete_feedback),
    path('add_report/', views.add_report),
    path('view_reports/', views.view_reports),
    
    path('staff_complaint_detail/', views.staff_complaint_detail),
    path('citizen_complaint_detail/', views.citizen_complaint_detail),
    path('admin_complaint_detail/', views.admin_complaint_detail),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
