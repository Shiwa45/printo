# Generated migration for front/back design support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='front_back_design_enabled',
            field=models.BooleanField(default=False, help_text='Enable front and back design options'),
        ),
    ]