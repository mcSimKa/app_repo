from django.db import models


class VersionCount(models.Model):
    aRelease = models.CharField(primary_key=True, max_length=32)
    aInstances = models.PositiveIntegerField()
    report_date = models.DateField()

    class Meta:
        managed = False
        db_table = 'v_version_count_last'

class ClientOS(models.Model):
    os = models.CharField(primary_key=True, max_length=128)
    count = models.PositiveIntegerField()
    report_date = models.DateField()

    class Meta:
        managed = False
        db_table = ''
