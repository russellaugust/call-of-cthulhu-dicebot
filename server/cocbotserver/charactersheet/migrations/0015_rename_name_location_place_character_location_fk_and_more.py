# Generated by Django 4.0.4 on 2022-08-16 00:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('charactersheet', '0014_location'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='name',
            new_name='place',
        ),
        migrations.AddField(
            model_name='character',
            name='location_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='charactersheet.location'),
        ),
        migrations.AlterField(
            model_name='location',
            name='description',
            field=models.CharField(blank=True, max_length=2000),
        ),
    ]