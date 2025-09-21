# Generated migration for front/back design support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('design_tool', '0004_auto_20250830_1715'),
    ]

    operations = [
        migrations.AddField(
            model_name='designtemplate',
            name='side',
            field=models.CharField(
                choices=[('front', 'Front'), ('back', 'Back'), ('single', 'Single Side')],
                default='single',
                help_text='Which side this template is for',
                max_length=10
            ),
        ),
        migrations.AddField(
            model_name='userdesign',
            name='design_type',
            field=models.CharField(
                choices=[('single', 'Single Side'), ('front_only', 'Front Only'), ('back_only', 'Back Only'), ('both_sides', 'Both Sides')],
                default='single',
                max_length=15
            ),
        ),
        migrations.AddField(
            model_name='userdesign',
            name='front_design_data',
            field=models.JSONField(blank=True, help_text='Front side canvas data', null=True),
        ),
        migrations.AddField(
            model_name='userdesign',
            name='back_design_data',
            field=models.JSONField(blank=True, help_text='Back side canvas data', null=True),
        ),
        migrations.AddField(
            model_name='userdesign',
            name='front_preview_image',
            field=models.ImageField(blank=True, upload_to='user_designs/previews/front/'),
        ),
        migrations.AddField(
            model_name='userdesign',
            name='back_preview_image',
            field=models.ImageField(blank=True, upload_to='user_designs/previews/back/'),
        ),
        migrations.AlterField(
            model_name='userdesign',
            name='design_data',
            field=models.JSONField(blank=True, help_text='Legacy canvas data for single-sided designs', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='designtemplate',
            unique_together={('category', 'side', 'name')},
        ),
    ]