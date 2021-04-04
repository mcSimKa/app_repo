from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from _datetime import datetime as dt, timedelta
from .models import VersionCount, ClientOS

def big_report(request):
    report_date = (dt.today() - timedelta(days=3)).date()
    versions_query = 'SELECT substring_index(dv.string_value,".",2) AS aRelease, COUNT(*) AS aInstances, ds.report_date\
                FROM dataset ds JOIN data_values dv ON ds.id=dv.dataset_id\
                JOIN property pr ON dv.property_id=pr.id \
                WHERE pr.property_name = "version" \
                    AND ds.report_date =  "{}"\
                GROUP BY ds.report_date, substring_index(dv.string_value,".",2)\
                ORDER BY aRelease;'

    clientos_query = ("SELECT substring(ad1.property_name,19,255) AS os,"
                     "sum(CONVERT(ad1.string_value, UNSIGNED)) AS count, ad1.report_date " 
                     "FROM v_appliance_values_param ad1 "
                     "LEFT OUTER JOIN v_appliance_values_param ad2 ON ad2.report_date=ad1.report_date AND ad1.license=ad2.license "
                     "AND ad2.property_name='replication.mode' AND ad2.string_value='DELTA_SECONDARY' "
                     "WHERE ad1.property_name LIKE 'backend.client.os%%' "
                     "AND ad1.property_name not in (  'backend.client.os.VmWare','backend.client.os.VMware', "
                                                        "'backend.client.os.Hyper V','backend.client.os.Hyper-V', "
                                                        "'backend.client.os.Unknown')" 
                     "AND ad1.report_date='{}' AND ad2.property_name is NULL GROUP BY ad1.report_date, ad1.property_name ORDER BY count desc;".format(report_date)
                      )


    clients = VersionCount.objects.raw(versions_query.format(report_date))
    print(clients)
    return render(request, "version_count/version_count.html",{"report_date":report_date,
                                                               "versions":VersionCount.objects.raw(versions_query.format(report_date)),
                                                               "clients_os":ClientOS.objects.raw(clientos_query)
                                                               })

def home(request):
    return HttpResponse("This page was served at " + str(dt.now()))