# Generated by Django 5.1.7 on 2025-03-17 07:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_customuser_profile_picture"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="full_name",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="social_media_link",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="customuser",
            name="verification_reason",
            field=models.TextField(blank=True, null=True),
        ),
    ]
