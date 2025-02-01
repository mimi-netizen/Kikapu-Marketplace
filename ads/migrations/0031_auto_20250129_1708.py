# Generated by Django 2.2.15 on 2025-01-29 17:08

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0030_remove_ads_email'),
    ]

    operations = [
        migrations.CreateModel(
            name='County',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('county_name', models.CharField(choices=[('Mombasa', 'Mombasa'), ('Kwale', 'Kwale'), ('Kilifi', 'Kilifi'), ('Tana River', 'Tana River'), ('Lamu', 'Lamu'), ('Taita-Taveta', 'Taita-Taveta'), ('Nairobi', 'Nairobi'), ('Kiambu', 'Kiambu'), ('Muranga', 'Muranga'), ('Kirinyaga', 'Kirinyaga'), ('Nyandarua', 'Nyandarua'), ('Nyeri', 'Nyeri'), ('Nakuru', 'Nakuru'), ('Laikipia', 'Laikipia'), ('Samburu', 'Samburu'), ('Trans-Nzoia', 'Trans-Nzoia'), ('Uasin Gishu', 'Uasin Gishu'), ('Elgeyo-Marakwet', 'Elgeyo-Marakwet'), ('Nandi', 'Nandi'), ('Baringo', 'Baringo'), ('Kasaragom', 'Kasaragom'), ('Turkana', 'Turkana')], max_length=100, unique=True)),
                ('slug', models.SlugField(blank=True, null=True, unique=True)),
            ],
            options={
                'verbose_name_plural': 'Counties',
            },
        ),
        migrations.AlterModelOptions(
            name='ads',
            options={'ordering': ['-date_created'], 'verbose_name_plural': 'Ads'},
        ),
        migrations.AlterModelOptions(
            name='adsbottombanner',
            options={'verbose_name': 'Bottom Banner', 'verbose_name_plural': 'Bottom Banners'},
        ),
        migrations.AlterModelOptions(
            name='adsimages',
            options={'verbose_name_plural': 'Ad Images'},
        ),
        migrations.AlterModelOptions(
            name='adsrightbanner',
            options={'verbose_name': 'Right Banner', 'verbose_name_plural': 'Right Banners'},
        ),
        migrations.AlterModelOptions(
            name='adstopbanner',
            options={'verbose_name': 'Top Banner', 'verbose_name_plural': 'Top Banners'},
        ),
        migrations.RemoveField(
            model_name='ads',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='ads',
            name='state',
        ),
        migrations.RemoveField(
            model_name='ads',
            name='video',
        ),
        migrations.RemoveField(
            model_name='adsimages',
            name='ads',
        ),
        migrations.AddField(
            model_name='ads',
            name='ad_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name='adsbottombanner',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='adsbottombanner',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is Active'),
        ),
        migrations.AddField(
            model_name='adsbottombanner',
            name='link',
            field=models.URLField(blank=True, null=True, verbose_name='Banner Link'),
        ),
        migrations.AddField(
            model_name='adsbottombanner',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='adsimages',
            name='ad',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='ads.Ads'),
        ),
        migrations.AddField(
            model_name='adsimages',
            name='is_primary',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='adsimages',
            name='uploaded_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='adsrightbanner',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='adsrightbanner',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is Active'),
        ),
        migrations.AddField(
            model_name='adsrightbanner',
            name='link',
            field=models.URLField(blank=True, null=True, verbose_name='Banner Link'),
        ),
        migrations.AddField(
            model_name='adsrightbanner',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='adstopbanner',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='adstopbanner',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='Is Active'),
        ),
        migrations.AddField(
            model_name='adstopbanner',
            name='link',
            field=models.URLField(blank=True, null=True, verbose_name='Banner Link'),
        ),
        migrations.AddField(
            model_name='adstopbanner',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='category',
            name='main_category',
            field=models.CharField(choices=[('Vehicles', 'Vehicles'), ('Property', 'Property'), ('Electronics', 'Electronics'), ('Fashion', 'Fashion'), ('Home & Office', 'Home & Office'), ('Jobs & Services', 'Jobs & Services'), ('Agriculture', 'Agriculture'), ('Sports & Outdoors', 'Sports & Outdoors'), ('Food & Beverages', 'Food & Beverages'), ('Health & Beauty', 'Health & Beauty'), ('Other', 'Other')], default='Other', max_length=50),
        ),
        migrations.AddField(
            model_name='category',
            name='subcategory',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='ads',
            name='brand',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='ads',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ads', to='ads.Category'),
        ),
        migrations.AlterField(
            model_name='ads',
            name='city',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ads.City'),
        ),
        migrations.AlterField(
            model_name='ads',
            name='condition',
            field=models.CharField(choices=[('Excellent', 'Excellent'), ('Good', 'Good'), ('Fair', 'Fair')], default='Good', max_length=20),
        ),
        migrations.AlterField(
            model_name='ads',
            name='phone',
            field=models.CharField(max_length=15, validators=[django.core.validators.RegexValidator(message='Phone number must be a valid Kenyan phone number (e.g., +254712345678)', regex='^\\+?254?\\d{9}$')]),
        ),
        migrations.AlterField(
            model_name='ads',
            name='price',
            field=models.DecimalField(decimal_places=2, help_text='Maximum price: 9,999,999.99', max_digits=10),
        ),
        migrations.AlterField(
            model_name='adsbottombanner',
            name='image',
            field=models.ImageField(upload_to='banners/bottom/', verbose_name='Banner Image'),
        ),
        migrations.AlterField(
            model_name='adsbottombanner',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Banner Title'),
        ),
        migrations.AlterField(
            model_name='adsimages',
            name='image',
            field=models.ImageField(upload_to='uploads/ads_images'),
        ),
        migrations.AlterField(
            model_name='adsrightbanner',
            name='image',
            field=models.ImageField(upload_to='banners/right/', verbose_name='Banner Image'),
        ),
        migrations.AlterField(
            model_name='adsrightbanner',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Banner Title'),
        ),
        migrations.AlterField(
            model_name='adstopbanner',
            name='image',
            field=models.ImageField(upload_to='banners/top/', verbose_name='Banner Image'),
        ),
        migrations.AlterField(
            model_name='adstopbanner',
            name='title',
            field=models.CharField(max_length=255, verbose_name='Banner Title'),
        ),
        migrations.AlterField(
            model_name='author',
            name='profile_pic',
            field=models.ImageField(blank=True, default='default-profile-pic.png', null=True, upload_to='uploads/profile-pictures'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='city',
            name='city_name',
            field=models.CharField(choices=[('Mombasa', 'Mombasa'), ('Nairobi', 'Nairobi'), ('Nakuru', 'Nakuru'), ('Kisumu', 'Kisumu'), ('Eldoret', 'Eldoret')], max_length=100),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together={('main_category', 'subcategory')},
        ),
        migrations.DeleteModel(
            name='State',
        ),
        migrations.RemoveField(
            model_name='category',
            name='category_image',
        ),
        migrations.RemoveField(
            model_name='category',
            name='category_name',
        ),
        migrations.AddField(
            model_name='ads',
            name='county',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ads.County'),
        ),
        migrations.AddField(
            model_name='city',
            name='county',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ads.County'),
        ),
        migrations.AlterUniqueTogether(
            name='city',
            unique_together={('city_name', 'county')},
        ),
    ]
