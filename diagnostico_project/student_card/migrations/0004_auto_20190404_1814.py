# Generated by Django 2.1.7 on 2019-04-04 18:14

from django.db import migrations, models
import student_card.models


class Migration(migrations.Migration):

    dependencies = [
        ('student_card', '0003_auto_20190329_1957'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cardinfo',
            name='signature',
        ),
        migrations.AlterField(
            model_name='cardinfo',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=student_card.models.get_upload_path),
        ),
    ]
