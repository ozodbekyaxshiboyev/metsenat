# Generated by Django 4.0.6 on 2022-07-26 04:38

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('metsenat', '0003_alter_sponsor_phone_alter_student_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sponsor',
            name='phone',
            field=models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(message="Faqat O`zbekiston mobil raqamlari tasdiqlanadi('+' belgisiz!)", regex='^998[0-9]{2}[0-9]{7}$')], verbose_name='Telefon raqam'),
        ),
        migrations.AlterField(
            model_name='student',
            name='phone',
            field=models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(message="Faqat O`zbekiston mobil raqamlari tasdiqlanadi('+' belgisiz!)!", regex='^998[0-9]{2}[0-9]{7}$')], verbose_name='Telefon raqam'),
        ),
    ]
