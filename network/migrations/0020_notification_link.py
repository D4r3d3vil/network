# Generated by Django 4.2.3 on 2023-08-14 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0019_remove_post_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='link',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
