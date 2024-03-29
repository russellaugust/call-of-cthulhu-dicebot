# Generated by Django 4.0.4 on 2022-08-22 19:46

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charactersheet', '0024_remove_character_characterskill_fk_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='base_points',
            field=models.CharField(default='0', max_length=32, validators=[django.core.validators.RegexValidator(code='invalid_equation', message='Must be simple equation with STR|INT|APP|DEX|EDU|SIZ|CON|POW ie DEX/2', regex='^(?:STR|INT|APP|DEX|EDU|SIZ|CON|POW)[/*+-]\\d+$')]),
        ),
    ]
