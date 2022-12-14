# Generated by Django 4.0.6 on 2022-07-27 04:54

from django.db import migrations, models
import django.db.models.deletion
import metsenat.models


class Migration(migrations.Migration):

    dependencies = [
        ('metsenat', '0009_alter_studentsponsor_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentsponsor',
            name='sponsor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metsenat.sponsor', validators=[metsenat.models.validate_activ]),
        ),
        migrations.AlterField(
            model_name='studentsponsor',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metsenat.student'),
        ),
    ]
