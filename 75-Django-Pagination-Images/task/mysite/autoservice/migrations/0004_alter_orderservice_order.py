# Generated by Django 4.1.4 on 2023-01-29 11:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('autoservice', '0003_alter_car_options_alter_carmake_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderservice',
            name='order',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='autoservice.order'),
        ),
    ]
