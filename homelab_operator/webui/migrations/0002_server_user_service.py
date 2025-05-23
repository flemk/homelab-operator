# Generated by Django 5.2 on 2025-04-12 15:41

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webui', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='server',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('port', models.IntegerField()),
                ('protocol', models.CharField(choices=[('TCP', 'TCP'), ('UDP', 'UDP')], max_length=10)),
                ('status', models.BooleanField(default=False)),
                ('server', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='webui.server')),
            ],
        ),
    ]
