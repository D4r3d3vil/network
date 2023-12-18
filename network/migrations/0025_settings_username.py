# Generated by Django 4.2.3 on 2023-09-08 13:24

from django.db import migrations, models
import network.models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0024_settings'),
    ]

    operations = [
        migrations.AddField(
            model_name='settings',
            name='username',
            field=models.CharField(default='', max_length=100, verbose_name=network.models.User),
            preserve_default=False,
        ),
    ]