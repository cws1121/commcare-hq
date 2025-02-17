# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-31 10:00
from __future__ import unicode_literals

import custom.icds_reports.models.aggregate
from django.db import migrations, models

from custom.icds_reports.utils.migrations import (
    get_composite_primary_key_migrations,
)
from corehq.sql_db.operations import RawSQLMigration
from corehq.sql_db.connections import is_citus_db
from custom.icds_reports.const import AGG_MIGRATION_TABLE
from custom.icds_core.db import create_citus_distributed_table

migrator = RawSQLMigration(('custom', 'icds_reports', 'migrations', 'sql_templates', 'database_views'))


def _distribute_citus_tables(apps, schema_editor):
    with schema_editor.connection.cursor() as cursor:
        if not is_citus_db(cursor):
            return

        for table, col in [(AGG_MIGRATION_TABLE, 'supervisor_id')]:
            create_citus_distributed_table(cursor, table, col)


class Migration(migrations.Migration):

    dependencies = [
        ('icds_reports', '0164_auto_20200123_0702'),
    ]

    operations = [
        migrations.CreateModel(
            name='AggregateMigrationForms',
            fields=[
                ('state_id', models.CharField(max_length=40)),
                ('supervisor_id', models.TextField(null=True)),
                ('month', models.DateField(help_text='Will always be YYYY-MM-01')),
                ('person_case_id', models.CharField(max_length=40, primary_key=True, serialize=False)),
                ('is_migrated', models.PositiveSmallIntegerField(
                    blank=True, help_text='Status of the Migration', null=True)),
                ('migration_date', models.DateTimeField(help_text='Migration Date', null=True)),
            ],
            options={
                'db_table': 'icds_dashboard_migration_forms',
            },
            bases=(models.Model, custom.icds_reports.models.aggregate.AggregateMixin),
        ),
        migrations.AlterUniqueTogether(
            name='aggregatemigrationforms',
            unique_together=set([('month', 'supervisor_id', 'person_case_id')]),
        ),
    ]

    operations.extend(get_composite_primary_key_migrations(['aggregatemigrationforms']))
    operations.append(migrations.RunPython(_distribute_citus_tables, migrations.RunPython.noop))
