from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeroSlide',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('subtitle', models.CharField(blank=True, max_length=255)),
                ('description', models.TextField(blank=True)),
                ('image', models.ImageField(blank=True, upload_to='hero_slides/')),
                ('background_gradient_from', models.CharField(default='from-gray-100', max_length=50)),
                ('background_gradient_via', models.CharField(default='via-gray-200', max_length=50)),
                ('background_gradient_to', models.CharField(default='to-gray-300', max_length=50)),
                ('primary_cta_text', models.CharField(blank=True, max_length=50)),
                ('primary_cta_url', models.CharField(blank=True, max_length=255)),
                ('secondary_cta_text', models.CharField(blank=True, max_length=50)),
                ('secondary_cta_url', models.CharField(blank=True, max_length=255)),
                ('is_active', models.BooleanField(default=True)),
                ('sort_order', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['sort_order', 'id'],
            },
        ),
    ]


