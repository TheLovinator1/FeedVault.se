# Generated by Django 5.0.3 on 2024-03-15 16:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('feedvault', '0002_alter_feed_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='entry',
            old_name='_id',
            new_name='entry_id',
        ),
        migrations.RenameField(
            model_name='feed',
            old_name='_id',
            new_name='feed_id',
        ),
    ]
