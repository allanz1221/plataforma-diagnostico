# Generated by Django 2.1.7 on 2019-04-04 18:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0007_auto_20190404_1803'),
    ]

    operations = [
        migrations.AlterField(
            model_name='result',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2019, 4, 4, 20, 14, 16, 546160, tzinfo=utc), null=True),
        ),
    ]
