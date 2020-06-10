# Generated by Django 2.1.7 on 2019-05-08 20:14

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0008_auto_20190404_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='text',
            field=models.CharField(blank=True, default='', max_length=1024),
        ),
        migrations.AlterField(
            model_name='result',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2019, 5, 8, 22, 14, 12, 915819, tzinfo=utc), null=True),
        ),
    ]