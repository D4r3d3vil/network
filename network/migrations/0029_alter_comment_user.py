# Generated by Django 4.2.3 on 2023-09-15 08:20

from django.db import migrations, models
import network.models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0028_alter_comment_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='user',
            field=models.CharField(max_length=100, verbose_name=network.models.User),
        ),
    ]
