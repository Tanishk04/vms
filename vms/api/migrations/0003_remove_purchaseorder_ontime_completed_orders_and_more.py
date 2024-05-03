# Generated by Django 5.0.4 on 2024-05-02 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_purchaseorder_ontime_completed_orders'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchaseorder',
            name='ontime_completed_orders',
        ),
        migrations.AddField(
            model_name='vendor',
            name='ontime_completed_orders',
            field=models.IntegerField(default=0),
        ),
    ]
