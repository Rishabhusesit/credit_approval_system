# Generated by Django 5.2.4 on 2025-07-17 08:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('loan_id', models.IntegerField(unique=True)),
                ('loan_amount', models.FloatField()),
                ('tenure', models.PositiveIntegerField()),
                ('interest_rate', models.FloatField()),
                ('monthly_installment', models.FloatField()),
                ('emis_paid_on_time', models.PositiveIntegerField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='loans', to='customers.customer')),
            ],
        ),
    ]
