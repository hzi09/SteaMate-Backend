# Generated by Django 4.2 on 2025-03-25 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0018_alter_userlibrarygame_playtime'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_syncing',
            field=models.BooleanField(default=False),
        ),
    ]
