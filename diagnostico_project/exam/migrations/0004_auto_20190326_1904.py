# Generated by Django 2.1.7 on 2019-03-26 19:04

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0003_auto_20190320_1554'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 26, 21, 4, 36, 967711, tzinfo=utc), null=True),
        ),
    ]