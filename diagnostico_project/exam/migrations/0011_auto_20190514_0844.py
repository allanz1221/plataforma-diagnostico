# Generated by Django 2.1.7 on 2019-05-14 15:44

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('exam', '0010_auto_20190508_1317'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='answer',
            options={'ordering': ('question__id', 'id', 'created_at')},
        ),
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ('-section__subject__id', '-section__id', 'id')},
        ),
        migrations.AlterModelOptions(
            name='section',
            options={'ordering': ('subject', 'id')},
        ),
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ('exam__id', 'id', 'title', 'created_at')},
        ),
        migrations.AlterField(
            model_name='result',
            name='deadline',
            field=models.DateTimeField(default=datetime.datetime(2019, 5, 14, 17, 44, 0, 32607, tzinfo=utc), null=True),
        ),
    ]
