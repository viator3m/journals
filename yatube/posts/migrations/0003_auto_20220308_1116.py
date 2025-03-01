# Generated by Django 2.2.19 on 2022-03-08 08:16

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('posts', '0002_auto_20220306_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, null=True,
                                    on_delete=django.db.models.deletion.CASCADE,
                                    related_name='posts', to='posts.Group'),
        ),
    ]
