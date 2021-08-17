# Generated by Django 2.2.24 on 2021-06-20 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditcare', '0004_add_couch_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditcareMigrationMeta',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(db_index=True, max_length=50)),
                ('state', models.CharField(choices=[('s', 'Started'), ('f', 'Finished'), ('e', 'Errored')], max_length=1)),
                ('record_count', models.PositiveIntegerField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]