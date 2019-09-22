# Generated by Django 2.2.2 on 2019-09-20 14:24

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rentshop', '0003_auto_20190918_1200'),
    ]

    operations = [
        migrations.AlterField(
            model_name='art',
            name='rent_end_date',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 9, 20, 14, 24, 40, 362659, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='art',
            name='rent_start_date',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 9, 20, 14, 24, 40, 362659, tzinfo=utc)),
        ),
    ]
