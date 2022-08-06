# Generated by Django 4.0.6 on 2022-07-25 15:07

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='OTM',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Sponsor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(message='Faqat O`zbekiston mobil raqamlari tasdiqlanadi!', regex='^998[0-9]{2}[0-9]{7}$')], verbose_name='Telefon raqam')),
                ('amount_pay', models.FloatField()),
                ('is_company', models.BooleanField(default=False)),
                ('status', models.CharField(choices=[('Yangi', 'Yangi'), ('Moderatsiyada', 'Moderatsiyada'), ('Tasdiqlangan', 'Tasdiqlangan'), ('Bekor qilingan', 'Bekor qilingan')], default='Yangi', max_length=30)),
                ('company_name', models.CharField(blank=True, max_length=100, null=True)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('pay_type', models.CharField(blank=True, choices=[('Naqd', 'Naqd'), ('Pul o`tkazmasi', 'Pul o`tkazmasi')], default=None, max_length=30, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('phone', models.CharField(max_length=17, unique=True, validators=[django.core.validators.RegexValidator(message='Faqat O`zbekiston mobil raqamlari tasdiqlanadi!', regex='^998[0-9]{2}[0-9]{7}$')], verbose_name='Telefon raqam')),
                ('type_student', models.CharField(choices=[('bakalavr', 'Bakalavr'), ('magistr', 'Magistr')], max_length=20)),
                ('amount_contract', models.FloatField()),
                ('created_date', models.DateField(auto_now_add=True)),
                ('otm', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metsenat.otm')),
            ],
        ),
        migrations.CreateModel(
            name='StudentSponsor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('created_date', models.DateField(auto_now_add=True)),
                ('sponsor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metsenat.sponsor')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='metsenat.student')),
            ],
        ),
        migrations.AddField(
            model_name='student',
            name='sponsor',
            field=models.ManyToManyField(related_name='student', through='metsenat.StudentSponsor', to='metsenat.sponsor'),
        ),
    ]
