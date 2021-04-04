from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from _datetime import datetime as dt, timedelta
from .models import VersionCount, ClientOS, MissingImplementation, BondingSet, VMwareConnection, EnginesCount, ReportValues

def big_report(request):
    report_date = dt.today().date()
    if (request.method == 'POST'):
        submit_date = request.POST['report_date']
        if submit_date != "":
            report_date = submit_date
    versions_query = VersionCount.query.format(report_date)
    clientos_query = ClientOS.query.format(report_date)

    return render(request, "report/report.html",{"report_date":report_date,
                                                               "versions":VersionCount.objects.raw(versions_query),
                                                               "clients_os":ClientOS.objects.raw(clientos_query)
                                                               })

def report_values(request):
    report_date = dt.today().date()
    license = ''
    if (request.method == 'POST'):
        submit_date = request.POST['report_date']
        license = request.POST['license']
        print(license)
        if submit_date != "":
            report_date = submit_date
    query = ReportValues.query.format(license,report_date)
    return render(request, "report/report_values.html",{"report_date":report_date,"parameters":ReportValues.objects.raw(query)
                                                               })

def daily_report(request, model, url, set_name):
    report_date = dt.today().date()
    if (request.method == 'POST'):
        submit_date = request.POST['report_date']
        if submit_date != "":
            report_date = submit_date
    query = model.query.format(report_date)
    return render(request, url ,{"report_date":report_date, set_name:model.objects.raw(query)})

def report_bonding(request):
    return daily_report(request, BondingSet, url="report/report_bonding.html", set_name="bonding_set")

def report_vmware(request):
    return daily_report(request, VMwareConnection, url="report/report_vmware.html", set_name="vmware_set")

def report_missing(request):
    return daily_report(request, MissingImplementation, url="report/report_missing.html", set_name="missing_implementations")

def report_engines(request):
    return daily_report(request, EnginesCount, url="report/report_engines.html", set_name="engine_counts")



def home(request):
    return render(request, "report/home.html")