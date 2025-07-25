# Generated by Django 5.2.4 on 2025-07-19 08:22

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='requete',
            name='city',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.city'),
        ),
        migrations.AddField(
            model_name='requete',
            name='country',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.country'),
        ),
        migrations.AddField(
            model_name='response',
            name='requete',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='responses', to='base.requete'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='video',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='videos', to=settings.AUTH_USER_MODEL),
        ),
    ]
