# Generated by Django 3.1.4 on 2021-01-25 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='VersionCount',
            fields=[
                ('aRelease', models.CharField(max_length=32, primary_key=True, serialize=False)),
                ('aInstances', models.PositiveIntegerField()),
                ('report_date', models.DateField()),
            ],
            options={
                'db_table': 'v_version_count_last',
                'managed': False,
            },
        ),
    ]