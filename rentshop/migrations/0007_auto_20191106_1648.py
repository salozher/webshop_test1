# Generated by Django 2.2.2 on 2019-11-06 15:48

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rentshop', '0006_auto_20191106_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='art',
            name='rent_end_date',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 11, 6, 15, 48, 10, 215102, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='art',
            name='rent_start_date',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 11, 6, 15, 48, 10, 215102, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_end_date',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 11, 6, 15, 48, 10, 219102, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_start_date',
            field=models.DateField(blank=True, default=datetime.datetime(2019, 11, 6, 15, 48, 10, 219102, tzinfo=utc)),
        ),
    ]
