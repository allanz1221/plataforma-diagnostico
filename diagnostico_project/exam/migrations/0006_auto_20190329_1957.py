# Generated by Django 2.1.7 on 2019-03-29 19:57

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0005_auto_20190327_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2019, 3, 29, 21, 57, 42, 864336, tzinfo=utc), null=True),
        ),
    ]
