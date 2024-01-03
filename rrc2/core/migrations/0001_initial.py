# Generated by Django 4.2.6 on 2023-10-18 08:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SmartDevice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=100)),
                ('maximum_hourly_energy_consumption', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='UserDeviceMapping',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('user', models.IntegerField()),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.smartdevice')),
            ],
        ),
    ]
