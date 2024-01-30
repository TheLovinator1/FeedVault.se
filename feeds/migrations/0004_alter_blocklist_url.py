# Generated by Django 5.0.1 on 2024-01-30 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('feeds', '0003_blocklist_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blocklist',
            name='url',
            field=models.CharField(help_text='The URL to block.', max_length=2000, unique=True),
        ),
    ]