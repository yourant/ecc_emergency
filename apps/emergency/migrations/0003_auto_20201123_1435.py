# Generated by Django 2.2.6 on 2020-11-23 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emergency', '0002_auto_20201120_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emergencyomnibus',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='emergency.EmergencyOmnibusGroup', verbose_name='综合类告警聚合ID'),
        ),
        migrations.AlterField(
            model_name='emergencyovertime',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='emergency.EmergencyOvertimeGroup', verbose_name='交易类告警聚合ID'),
        ),
    ]