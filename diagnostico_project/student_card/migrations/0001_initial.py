# Generated by Django 2.1.7 on 2019-03-26 20:24

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CardInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('disabled', models.BooleanField(default=False)),
                ('photo', models.ImageField(upload_to='')),
                ('blood_type', models.CharField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], default='O+', max_length=8)),
                ('signature', models.ImageField(upload_to='')),
                ('nss', models.CharField(max_length=11)),
                ('curp', models.CharField(max_length=18)),
                ('emergency_contact_name', models.CharField(max_length=255)),
                ('emergency_phone_number', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
