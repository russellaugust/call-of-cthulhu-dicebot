# Generated by Django 4.0.4 on 2022-08-23 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('charactersheet', '0026_alter_character_player_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='character',
            name='passcode',
            field=models.CharField(blank=True, default='', help_text="Passcode for your character's safety.", max_length=255),
        ),
    ]
