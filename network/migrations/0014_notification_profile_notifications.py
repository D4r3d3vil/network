# Generated by Django 4.2.3 on 2023-08-13 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0013_profile_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('text', models.TextField()),
                ('read', models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(
            model_name='profile',
            name='notifications',
            field=models.ManyToManyField(blank=True, related_name='notifications', to='network.notification'),
        ),
    ]
