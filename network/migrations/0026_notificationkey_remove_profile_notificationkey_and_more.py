# Generated by Django 4.2.3 on 2023-09-09 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0025_settings_username'),
    ]

    operations = [
        migrations.CreateModel(
            name='notificationKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=1000)),
            ],
        ),
        migrations.RemoveField(
            model_name='profile',
            name='notificationKey',
        ),
        migrations.DeleteModel(
            name='Settings',
        ),
        migrations.AddField(
            model_name='profile',
            name='notificationKeys',
            field=models.ManyToManyField(blank=True, related_name='notificationKeys', to='network.notificationkey'),
        ),
    ]
