# Generated by Django 2.1.7 on 2019-03-29 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student_card', '0002_auto_20190327_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardinfo',
            name='emergency_phone_number',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]