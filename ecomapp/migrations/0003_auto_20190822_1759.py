# Generated by Django 2.2.2 on 2019-08-22 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0002_auto_20190822_1424'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artobject',
            name='slug',
            field=models.SlugField(blank=True, editable=False, max_length=100, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='product_alternative',
            name='slug',
            field=models.SlugField(default='6bgz3g9l0u', editable=False, max_length=200),
        ),
    ]