# Generated by Django 4.2.7 on 2024-05-16 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.UUIDField(primary_key=True, serialize=False)),
                ('nama', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=50)),
                ('kontak', models.CharField(max_length=50)),
                ('id_pemilik_hak_cipta', models.UUIDField(null=True)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
    ]
