# Generated by Django 2.2.3 on 2021-03-31 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard_usuario', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='balance',
            name='value',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='moneydelivery',
            name='value',
            field=models.FloatField(default=0.0),
        ),
    ]