# Generated by Django 5.1.7 on 2025-03-15 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="kyc_document_back",
            field=models.ImageField(blank=True, null=True, upload_to="kyc_documents/"),
        ),
        migrations.AddField(
            model_name="customuser",
            name="kyc_document_front",
            field=models.ImageField(blank=True, null=True, upload_to="kyc_documents/"),
        ),
        migrations.AddField(
            model_name="customuser",
            name="kyc_document_selfie",
            field=models.ImageField(blank=True, null=True, upload_to="kyc_documents/"),
        ),
        migrations.AddField(
            model_name="customuser",
            name="kyc_verified",
            field=models.BooleanField(default=False),
        ),
    ]
