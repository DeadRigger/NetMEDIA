# Generated by Django 2.1.5 on 2019-02-23 16:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_target_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='target',
            name='executor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='executor', to=settings.AUTH_USER_MODEL),
        ),
    ]