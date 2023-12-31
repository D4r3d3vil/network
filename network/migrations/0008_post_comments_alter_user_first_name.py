# Generated by Django 4.2.3 on 2023-08-08 20:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0007_auto_20200729_1836'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='comments',
            field=models.JSONField(default=None),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
    ]
