from django.urls import path

from . import views

urlpatterns = [
path('', views.home, name="home"),
path('report', views.big_report, name="report"),
path('report_missing', views.report_missing, name="report_missing"),
path('report_bonding', views.report_bonding, name="report_bonding"),
path('report_engines', views.report_engines, name="report_engines"),
path('report_values', views.report_values, name="report_values"),
path('report_vmware', views.report_vmware, name="report_vmware")
    ]