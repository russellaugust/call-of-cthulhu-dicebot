# Generated by Django 4.0.4 on 2022-08-16 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charactersheet', '0016_discordchannel_roll_channel_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='discordchannel',
            name='name',
            field=models.CharField(default=1, max_length=32),
            preserve_default=False,
        ),
    ]