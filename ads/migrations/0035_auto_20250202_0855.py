# Generated by Django 2.2.15 on 2025-02-02 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0034_auto_20250131_0901'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='category',
            field=models.CharField(choices=[('Cars', 'Cars'), ('Buses & Microbuses', 'Buses & Microbuses'), ('Heavy Equipment', 'Heavy Equipment'), ('Motorcycles', 'Motorcycles'), ('Trucks', 'Trucks'), ('Other Vehicles', 'Other Vehicles'), ('New Builds', 'New Builds'), ('Houses & Apartments for Rent', 'Houses & Apartments for Rent'), ('Houses & Apartments for Sale', 'Houses & Apartments for Sale'), ('Land for Sale', 'Land for Sale'), ('Commercial Property', 'Commercial Property'), ('Other Property', 'Other Property'), ('Phones', 'Phones'), ('Laptops', 'Laptops'), ('Desktops', 'Desktops'), ('Tablets', 'Tablets'), ('Televisions', 'Televisions'), ('Other Electronics', 'Other Electronics'), ("Men's Fashion", "Men's Fashion"), ("Women's Fashion", "Women's Fashion"), ("Kids' Fashion", "Kids' Fashion"), ('Other Fashion', 'Other Fashion'), ('Furniture', 'Furniture'), ('Appliances', 'Appliances'), ('Home Decor', 'Home Decor'), ('Office Equipment', 'Office Equipment'), ('Other Home & Office', 'Other Home & Office'), ('Jobs', 'Jobs'), ('Services', 'Services'), ('Livestock', 'Livestock'), ('Farming Equipment', 'Farming Equipment'), ('Other Agriculture', 'Other Agriculture'), ('Fitness', 'Fitness'), ('Sports Equipment', 'Sports Equipment'), ('Other Sports & Outdoors', 'Other Sports & Outdoors'), ('Food', 'Food'), ('Beverages', 'Beverages'), ('Health', 'Health'), ('Beauty', 'Beauty'), ('Other', 'Other')], default='Other', max_length=50),
        ),
        migrations.AlterUniqueTogether(
            name='category',
            unique_together=set(),
        ),
        migrations.RemoveField(
            model_name='category',
            name='main_category',
        ),
        migrations.RemoveField(
            model_name='category',
            name='subcategory',
        ),
    ]
