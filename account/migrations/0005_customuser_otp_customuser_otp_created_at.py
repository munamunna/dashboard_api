# Generated by Django 4.2.21 on 2025-06-04 00:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='otp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
        migrations.AddField(
            model_name='customuser',
            name='otp_created_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
