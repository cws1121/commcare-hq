# Generated by Django 2.2.19 on 2021-04-02 11:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fhir', '0003_auto_20210319_0948'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='fhirresourcetype',
            name='template',
        ),
    ]