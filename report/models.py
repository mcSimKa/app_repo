from django.db import models


class VersionCount(models.Model):
    aRelease = models.CharField(primary_key=True, max_length=32)
    aInstances = models.PositiveIntegerField()
    report_date = models.DateField()

    query = ("""SELECT substring_index(dv.string_value,".",2) AS aRelease, COUNT(*) AS aInstances, ds.report_date
            FROM dataset ds JOIN data_values dv ON ds.id=dv.dataset_id
            JOIN property pr ON dv.property_id=pr.id 
            WHERE pr.property_name = "version" 
                AND ds.report_date =  "{}"
                AND dv.string_value IN (select version FROM releases)
                AND EXISTS (select 1 from data_values dv1, property p1
					 WHERE ds.id=dv1.dataset_id AND dv1.property_id=p1.id and p1.property_name='version'
					 and dv1.string_value IN (select version from releases)) 
            GROUP BY ds.report_date, substring_index(dv.string_value,".",2)
            ORDER BY aRelease;""")

    class Meta:
        managed = False
        db_table = 'v_version_count_last'


class ClientOS(models.Model):
    os = models.CharField(primary_key=True, max_length=128)
    count = models.PositiveIntegerField()
    report_date = models.DateField()

    query = ("""select 
substring(p.property_name,19,255) AS os,
             sum(CONVERT(dv.string_value, UNSIGNED)) AS count,
             ds.report_date 
             FROM data_values dv 
				JOIN property p on p.id=dv.property_id
                JOIN dataset ds on ds.id = dv.dataset_id
             WHERE p.property_name LIKE 'backend.client.os%%' 
                 AND p.property_name not in (  'backend.client.os.VmWare','backend.client.os.VMware', 
                 'backend.client.os.Hyper V','backend.client.os.Hyper-V', 
                 'backend.client.os.Unknown')
                 AND ds.report_date='{}' 
                 AND  not ifnull( (select dv2.string_value from data_values dv2, property p2
									where p2.property_name = 'replication.mode' and dv2.property_id=p2.id
									and dv2.dataset_id=ds.id ), '') = 'DELTA_SECONDARY' 
				AND EXISTS (select 1 from data_values dv1, property p1
					 WHERE ds.id=dv1.dataset_id AND dv1.property_id=p1.id and p1.property_name='version'
					 and dv1.string_value IN (select version from releases)) 
             GROUP BY p.property_name ORDER BY count desc;"""
             )
    class Meta:
        managed = False
        db_table = ''


class MissingImplementation(models.Model):
    uuid = models.CharField(primary_key=True, max_length=32)
    hostname = models.CharField(max_length=32)
    ip_address = models.CharField(max_length=32)
    model = models.CharField(max_length=32)
    version = models.CharField(max_length=32)
    property_name = models.CharField(max_length=32)
    data_value = models.CharField(max_length=32)


    query = ("""
    SELECT 	(select dv.string_value from data_values dv, property p
	 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='GUID') as uuid,
	(select dv.string_value from data_values dv, property p
	 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='hostname') as hostname,
     	(select dv.string_value from data_values dv, property p
	 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='netif.ip.0') as ip_address,
	(select dv.string_value from data_values dv, property p
	 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='model') as model,
	(select dv.string_value from data_values dv, property p
	 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='version') as version,
     p1.property_name ,
	dv1.string_value as data_value

    FROM appliance a, dataset ds, property p1, data_values dv1
    WHERE ds.appliance_id=a.id  AND ds.report_date = '{}'
    AND p1.property_name LIKE 'netif.unimplemented%%'  AND dv1.property_id=p1.id
                        and dv1.dataset_id=ds.id
    ORDER BY appliance_id
    """)

    class Meta:
        managed = False
        db_table = ''


class BondingSet(models.Model):
    uuid = models.CharField(primary_key=True, max_length=32)
    hostname = models.CharField(max_length=32)
    ip_address = models.CharField(max_length=32)
    model = models.CharField(max_length=32)
    version = models.CharField(max_length=32)
    repl_mode = models.CharField(max_length=32)
    query=("""
        select uuid,
            hostname,
            ip_address,
            model,
            repl_mode,
            version
        from 
        (
        SELECT (select dv.string_value from data_values dv, property p
             WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='GUID') as uuid,
                (select dv.string_value from data_values dv, property p
             WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='hostname') as hostname,
                (select dv.string_value from data_values dv, property p
             WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='model') as Model,
            (select dv.string_value from data_values dv, property p
             WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='version') as Version,
			(select dv.string_value from data_values dv, property p
				WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='netif.ip.0') as ip_address,
                (select dv.string_value from data_values dv, property p
             WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='replication.mode') as repl_mode,
             (CASE WHEN EXISTS (select 1 from property p1, data_values dv1 
                            WHERE p1.property_name ='netif.ip.bond' AND dv1.property_id=p1.id
                            and dv1.dataset_id=ds.id
                            )
             THEN 1
             ELSE 0
            END) as bonding
        FROM appliance a, dataset ds
        WHERE ds.appliance_id=a.id  AND ds.report_date = '{}'
        ) as report
        WHERE bonding=1
        AND version in (select version from releases)
        ORDER BY version, model
    """)

    class Meta:
        managed = False
        db_table = ''

class VMwareConnection(models.Model):
    version = models.CharField(primary_key=True, max_length=32)
    vmversion = models.CharField(max_length=32)
    amount = models.CharField(max_length=32)

    query = ("""
        SELECT 	(select dv.string_value from data_values dv, property p
             WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='version') as version,
            dv1.string_value as vmversion,
            count(*) as amount
        FROM appliance a, dataset ds, property p1, data_values dv1
        WHERE ds.appliance_id=a.id  AND ds.report_date= '{0}'
        AND p1.property_name LIKE 'vmware.host._.product.version'  AND dv1.property_id=p1.id
                            and dv1.dataset_id=ds.id
        AND EXISTS (select 1 from data_values dv1, property p1
	                WHERE ds.id=dv1.dataset_id AND dv1.property_id=p1.id and p1.property_name='version'
                    and dv1.string_value IN (select version from releases)) 
        GROUP BY Version,vmversion
        UNION
        SELECT 	'TOTAL' as version,
            dv1.string_value as vmversion,
            count(*) as amount
        FROM appliance a, dataset ds, property p1, data_values dv1
        WHERE ds.appliance_id=a.id  AND ds.report_date= '{0}'
        AND p1.property_name LIKE 'vmware.host._.product.version'  AND dv1.property_id=p1.id
                            and dv1.dataset_id=ds.id
        AND EXISTS (select 1 from data_values dv1, property p1
	                WHERE ds.id=dv1.dataset_id AND dv1.property_id=p1.id and p1.property_name='version'
                    and dv1.string_value IN (select version from releases)) 

        GROUP BY vmversion
        ORDER BY vmversion, version;
        """)

    class Meta:
        managed = False
        db_table = ''

class EnginesCount(models.Model):
    Model = models.CharField(primary_key=True, max_length=32)
    Version = models.CharField(max_length=32)
    hostname = models.CharField(max_length=32)
    HyperVCount = models.PositiveIntegerField()
    OS_HyperV = models.PositiveIntegerField()
    EngineAutoCount = models.PositiveIntegerField()
    EngineIgnyteCount = models.PositiveIntegerField()
    EnginePrmCount = models.PositiveIntegerField()
    uuid = models.CharField(max_length=128)

    query = ("""
            select  
            Model,	Version,	hostname,	HyperVCount,	OS_HyperV,	EngineAutoCount,	EngineIgnyteCount,	EnginePrmCount, uuid
            from 
            (SELECT (select dv.string_value from data_values dv, property p
                 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='model') as Model,
                (select dv.string_value from data_values dv, property p
                 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='version') as Version,
                (select dv.string_value from data_values dv, property p
                         WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='hostname') as hostname,
                    (select CONVERT(dv.string_value, UNSIGNED) from data_values dv, property p
                 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='backend.client.hyperv.count') as HyperVCount,
                    (select CONVERT(dv.string_value, UNSIGNED) from data_values dv, property p
                 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='backend.client.os.Hyper-V') as OS_HyperV,
                    (select CONVERT(dv.string_value, UNSIGNED) from data_values dv, property p
                 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='backend.client.engine.auto.count') as EngineAutoCount,
                    (select CONVERT(dv.string_value, UNSIGNED) from data_values dv, property p
                 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='backend.client.engine.ignyte.count') as EngineIgnyteCount,
                    (select CONVERT(dv.string_value, UNSIGNED) from data_values dv, property p
                 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='backend.client.engine.prm.count') as EnginePrmCount,
                    (select dv.string_value from data_values dv, property p
                 WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='GUID') as uuid,
                    (select dv.string_value from data_values dv, property p
                  WHERE ds.id=dv.dataset_id AND dv.property_id=p.id and p.property_name='replication.mode') as ReplicationMode
                 
            FROM appliance a 
            JOIN dataset ds ON ds.appliance_id=a.id and ds.report_date = '{}'
            ) report 
            WHERE 
             hypervcount>0
             and (EngineIgnyteCount>0 and EnginePrmCount=0) 
             and not ReplicationMode = 'DELTA_SECONDARY'
            and version in (select version from releases);
    """)

    class Meta:
        managed = False
        db_table = ''

class ReportValues(models.Model):
    property_name = models.CharField(primary_key=True, max_length=128)
    string_value = models.CharField(max_length=256)

    query = ("""select p.property_name, dv.string_value from data_values dv 
                join property p on p.id=dv.property_id 
                join dataset ds on ds.id=dv.dataset_id
                join appliance a on a.id=ds.appliance_id
            WHERE a.license='{}' and ds.report_date='{}'; """
             )
    class Meta:
        managed = False
        db_table = ''