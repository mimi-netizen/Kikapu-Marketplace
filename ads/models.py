from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid

# Phone Number Validator
phone_validator = RegexValidator(
    regex=r'^\+?254?\d{9}$', 
    message="Phone number must be a valid Kenyan phone number (e.g., +254712345678)"
)

# Author Model
class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(
        default="default-profile-pic.png", 
        upload_to='uploads/profile-pictures', 
        null=True, 
        blank=True
    )

    def __str__(self):
        return self.user.username

# County Model
class County(models.Model):
    COUNTY_CHOICES = [
        ('Mombasa', 'Mombasa'),
        ('Kwale', 'Kwale'),
        ('Kilifi', 'Kilifi'),
        ('Tana River', 'Tana River'),
        ('Lamu', 'Lamu'),
        ('Taita-Taveta', 'Taita-Taveta'),
        ('Nairobi', 'Nairobi'),
        ('Kiambu', 'Kiambu'),
        ('Muranga', 'Muranga'),
        ('Kirinyaga', 'Kirinyaga'),
        ('Nyandarua', 'Nyandarua'),
        ('Nyeri', 'Nyeri'),
        ('Nakuru', 'Nakuru'),
        ('Laikipia', 'Laikipia'),
        ('Samburu', 'Samburu'),
        ('Trans-Nzoia', 'Trans-Nzoia'),
        ('Uasin Gishu', 'Uasin Gishu'),
        ('Elgeyo-Marakwet', 'Elgeyo-Marakwet'),
        ('Nandi', 'Nandi'),
        ('Baringo', 'Baringo'),
        ('Bomet', 'Bomet'),
        ('Bungoma', 'Bungoma'),
        ('Busia', 'Busia'),
        ('Embu', 'Embu'),
        ('Garissa', 'Garissa'),
        ('Homa Bay', 'Homa Bay'),
        ('Isiolo', 'Isiolo'),
        ('Kajiado', 'Kajiado'),
        ('Kakamega', 'Kakamega'),
        ('Kericho', 'Kericho'),
        ('Kisii', 'Kisii'),
        ('Kisumu', 'Kisumu'),
        ('Kitui', 'Kitui'),
        ('Machakos', 'Machakos'),
        ('Makueni', 'Makueni'),
        ('Mandera', 'Mandera'),
        ('Marsabit', 'Marsabit'),
        ('Meru', 'Meru'),
        ('Migori', 'Migori'),
        ('Narok', 'Narok'),
        ('Nyamira', 'Nyamira'),
        ('Siaya', 'Siaya'),
        ('Tharaka-Nithi', 'Tharaka-Nithi'),
        ('Turkana', 'Turkana'),
        ('Vihiga', 'Vihiga'),
        ('Wajir', 'Wajir'),
        ('West Pokot', 'West Pokot')
    ]

    county_name = models.CharField(
        max_length=100, 
        unique=True, 
        choices=COUNTY_CHOICES
    )
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.county_name)
            unique_slug = base_slug
            counter = 1
            while County.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Counties"

    def __str__(self):
        return self.county_name

# City Model
class City(models.Model):
    CITY_CHOICES = [
        # Coast Region
        ('Mombasa', 'Mombasa'), ('Likoni', 'Likoni'), ('Kisauni', 'Kisauni'), ('Nyali', 'Nyali'), ('Mtwapa', 'Mtwapa'),
        ('Lamu', 'Lamu'), ('Mpeketoni', 'Mpeketoni'), ('Faza', 'Faza'), ('Witu', 'Witu'),
        ('Taita-Taveta', 'Taita-Taveta'), ('Voi', 'Voi'), ('Mwatate', 'Mwatate'), ('Taveta', 'Taveta'), ('Wundanyi', 'Wundanyi'),
        
        # Nairobi Region
        ('Nairobi', 'Nairobi'), ('Karen', 'Karen'), ("Lang'ata", "Lang'ata"), ('Westlands', 'Westlands'), 
        ('Embakasi', 'Embakasi'), ('Kasarani', 'Kasarani'),
        
        # Nyanza Region
        ('Kisumu', 'Kisumu'), ('Ahero', 'Ahero'), ('Muhoroni', 'Muhoroni'),
        ('Homa Bay', 'Homa Bay'), ('Kendu Bay', 'Kendu Bay'), ('Mbita', 'Mbita'), ('Oyugis', 'Oyugis'),
        ('Migori', 'Migori'), ('Rongo', 'Rongo'), ('Awendo', 'Awendo'), ('Uriri', 'Uriri'),
        ('Siaya', 'Siaya'), ('Bondo', 'Bondo'), ('Ugunja', 'Ugunja'), ('Yala', 'Yala'),
        
        # Rift Valley Region
        ('Nakuru', 'Nakuru'), ('Naivasha', 'Naivasha'), ('Gilgil', 'Gilgil'), ('Molo', 'Molo'), ('Njoro', 'Njoro'),
        ('Uasin Gishu', 'Uasin Gishu'), ('Kesses', 'Kesses'), ('Moiben', 'Moiben'), ('Burnt Forest', 'Burnt Forest'), 
        ('Ziwa', 'Ziwa'),
        ('Turkana', 'Turkana'), ('Kakuma', 'Kakuma'), ('Lokichogio', 'Lokichogio'), ('Kalokol', 'Kalokol'), 
        ('Lokichar', 'Lokichar'),
        ('West Pokot', 'West Pokot'), ('Kacheliba', 'Kacheliba'), ('Alale', 'Alale'), ('Sigor', 'Sigor'), 
        ('Lomut', 'Lomut'),
        ('Baringo', 'Baringo'), ('Marigat', 'Marigat'), ('Kabarnet', 'Kabarnet'), ('Mogotio', 'Mogotio'), 
        ('Eldama Ravine', 'Eldama Ravine'),
        ('Bomet', 'Bomet'), ('Longisa', 'Longisa'), ('Sotik', 'Sotik'), ('Chepalungu', 'Chepalungu'),
        ('Kericho', 'Kericho'), ('Litein', 'Litein'), ('Bureti', 'Bureti'), ('Sosiot', 'Sosiot'),
        ('Samburu', 'Samburu'), ('Baragoi', 'Baragoi'), ("Archer's Post", "Archer's Post"), ('Wamba', 'Wamba'),
        
        # Western Region
        ('Kakamega', 'Kakamega'), ('Mumias', 'Mumias'), ('Malava', 'Malava'), ('Butere', 'Butere'), ('Khayega', 'Khayega'),
        ('Bungoma', 'Bungoma'), ('Webuye', 'Webuye'), ('Malakisi', 'Malakisi'), ('Chwele', 'Chwele'), ('Naitiri', 'Naitiri'),
        ('Busia', 'Busia'), ('Malaba', 'Malaba'), ('Nambale', 'Nambale'), ('Funyula', 'Funyula'),
        ('Vihiga', 'Vihiga'), ('Mbale', 'Mbale'), ('Luanda', 'Luanda'), ('Majengo', 'Majengo'),
        
        # Eastern Region
        ('Embu', 'Embu'), ('Runyenjes', 'Runyenjes'), ('Siakago', 'Siakago'), ('Manyatta', 'Manyatta'),
        ('Kitui', 'Kitui'), ('Mwingi', 'Mwingi'), ('Mutomo', 'Mutomo'), ('Kwa Vonza', 'Kwa Vonza'),
        ('Machakos', 'Machakos'), ('Athi River', 'Athi River'), ('Mwala', 'Mwala'), ('Kathiani', 'Kathiani'),
        ('Makueni', 'Makueni'), ('Makindu', 'Makindu'), ('Sultan Hamud', 'Sultan Hamud'), ('Kibwezi', 'Kibwezi'),
        ('Meru', 'Meru'), ('Maua', 'Maua'), ('Nkubu', 'Nkubu'), ('Timau', 'Timau'),
        ('Tharaka-Nithi', 'Tharaka-Nithi'), ('Marimanti', 'Marimanti'), ('Gatunga', 'Gatunga'), ('Magutuni', 'Magutuni'),
        
        # North Eastern Region
        ('Garissa', 'Garissa'), ('Dadaab', 'Dadaab'), ('Fafi', 'Fafi'), ('Liboi', 'Liboi'),
        ('Isiolo', 'Isiolo'), ('Garba Tulla', 'Garba Tulla'), ('Merti', 'Merti'), ('Kinna', 'Kinna'),
        ('Mandera', 'Mandera'), ('El Wak', 'El Wak'), ('Takaba', 'Takaba'), ('Rhamu', 'Rhamu'),
        ('Marsabit', 'Marsabit'), ('Laisamis', 'Laisamis'), ('Loiyangalani', 'Loiyangalani'), ('Maikona', 'Maikona'),
        ('Wajir', 'Wajir'), ('Habaswein', 'Habaswein'), ('Tarbaj', 'Tarbaj'), ('Griftu', 'Griftu'),
        
        # Central Region
        ('Kiambu', 'Kiambu'), ('Thika', 'Thika'), ('Ruiru', 'Ruiru'), ('Kikuyu', 'Kikuyu'),
        ("Murang'a", "Murang'a"), ('Kenol', 'Kenol'), ('Maragua', 'Maragua'), ('Kangema', 'Kangema'),
        ('Kirinyaga', 'Kirinyaga'), ('Kerugoya', 'Kerugoya'), ('Sagana', 'Sagana'), ('Wanguru', 'Wanguru'), 
        ('Baricho', 'Baricho'),
        ('Nyandarua', 'Nyandarua'), ('Ol Kalou', 'Ol Kalou'), ('Ndaragwa', 'Ndaragwa'), ('Njabini', 'Njabini'), 
        ('Engineer', 'Engineer'),
        ('Nyeri', 'Nyeri'), ('Karatina', 'Karatina'), ('Othaya', 'Othaya'), ('Mweiga', 'Mweiga'),
        ('Laikipia', 'Laikipia'), ('Nanyuki', 'Nanyuki'), ('Rumuruti', 'Rumuruti'), ('Nyahururu', 'Nyahururu'), 
        ('Dol Dol', 'Dol Dol'),
    ]


    city_name = models.CharField(max_length=100, choices=CITY_CHOICES)
    slug = models.SlugField(blank=True, null=True)
    county = models.ForeignKey(
        'County', 
        on_delete=models.CASCADE,
        null=True,  
        blank=True  
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.city_name)
            unique_slug = base_slug
            counter = 1
            while City.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Cities"
        unique_together = ('city_name', 'county')

    def __str__(self):
        return f"{self.city_name} ({self.county.county_name if self.county else 'No County'})"

# Category Model
class Category(models.Model):
    MAIN_CATEGORY_CHOICES = [
        ('Vehicles', 'Vehicles'),
        ('Property', 'Property'),
        ('Electronics', 'Electronics'),
        ('Fashion', 'Fashion'),
        ('Home & Office', 'Home & Office'),
        ('Jobs & Services', 'Jobs & Services'),
        ('Agriculture', 'Agriculture'),
        ('Sports & Outdoors', 'Sports & Outdoors'),
        ('Food & Beverages', 'Food & Beverages'),
        ('Health & Beauty', 'Health & Beauty'),
        ('Other', 'Other'),
    ]

    SUBCATEGORY_CHOICES = {
        'Vehicles': [
            ('Cars', 'Cars'),
            ('Buses & Microbuses', 'Buses & Microbuses'),
            ('Heavy Equipment', 'Heavy Equipment'),
            ('Motorcycles', 'Motorcycles'),
            ('Trucks', 'Trucks'),
            ('Other Vehicles', 'Other Vehicles'),
        ],
        'Property': [
            ('New Builds', 'New Builds'),
            ('Houses & Apartments for Rent', 'Houses & Apartments for Rent'),
            ('Land for Sale', 'Land for Sale'),
            ('Commercial Property', 'Commercial Property'),
            ('Other Property', 'Other Property'),
        ],
        'Electronics': [
            ('Phones', 'Phones'),
            ('Laptops', 'Laptops'),
            ('Desktops', 'Desktops'),
            ('Tablets', 'Tablets'),
            ('Televisions', 'Televisions'),
            ('Other Electronics', 'Other Electronics'),
        ],
        'Fashion': [
            ('Men\'s Fashion', 'Men\'s Fashion'),
            ('Women\'s Fashion', 'Women\'s Fashion'),
            ('Kids\' Fashion', 'Kids\' Fashion'),
            ('Other Fashion', 'Other Fashion'),
        ],
        'Home & Office': [
            ('Furniture', 'Furniture'),
            ('Appliances', 'Appliances'),
            ('Home Decor', 'Home Decor'),
            ('Office Equipment', 'Office Equipment'),
            ('Other Home & Office', 'Other Home & Office'),
        ],
        'Jobs & Services': [
            ('Jobs', 'Jobs'),
            ('Services', 'Services'),
        ],
        'Agriculture': [
            ('Livestock', 'Livestock'),
            ('Farming Equipment', 'Farming Equipment'),
            ('Other Agriculture', 'Other Agriculture'),
        ],
        'Sports & Outdoors': [
            ('Fitness', 'Fitness'),
            ('Sports Equipment', 'Sports Equipment'),
            ('Other Sports & Outdoors', 'Other Sports & Outdoors'),
        ],
        'Food & Beverages': [
            ('Food', 'Food'),
            ('Beverages', 'Beverages'),
        ],
        'Health & Beauty': [
            ('Health', 'Health'),
            ('Beauty', 'Beauty'),
        ],
        'Other': [
            ('Other', 'Other'),
        ]
    }

    main_category = models.CharField(
        max_length=50, 
        choices=MAIN_CATEGORY_CHOICES, 
        default='Other'
    )
    subcategory = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
    )
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.main_category} {self.subcategory}" if self.subcategory else self.main_category)
            unique_slug = base_slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug

        if self.subcategory:
            valid_subcategories = self.SUBCATEGORY_CHOICES.get(self.main_category, [])
            if not any(self.subcategory in subcat for subcat in valid_subcategories):
                raise ValueError(f"{self.subcategory} is not a valid subcategory for {self.main_category}")

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.main_category} - {self.subcategory}" if self.subcategory else self.main_category

    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ('main_category', 'subcategory')

# Ads Model
class Ads(models.Model):
    CONDITION_CHOICES = [
        ('Excellent', 'Excellent'),
        ('Good', 'Good'),
        ('Fair', 'Fair'),
    ]

    ad_id = models.UUIDField(
        default=uuid.uuid4, 
        editable=False, 
        unique=True
    )
    author = models.ForeignKey(Author, on_delete=models.CASCADE, null=True)
    county = models.ForeignKey(County, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='ads'
    )
    title = models.CharField(max_length=200)
    description = RichTextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Maximum price: 9,999,999.99"
    )
    condition = models.CharField(
        max_length=20, 
        choices=CONDITION_CHOICES, 
        default='Good'
    )
    brand = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(
        max_length=15, 
        validators=[phone_validator]
    )
    date_created = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Ads"
        ordering = ['-date_created']

    def __str__(self):
        author_name = self.author.user.username if self.author else 'No Author'
        county_name = self.county.county_name if self.county else 'No County'
        city_name = self.city.city_name if self.city else 'No City'
    
        return f"{self.title} - {author_name} - {city_name}, {county_name}"

# Images Model for Ads
class AdsImages(models.Model):
    ad = models.ForeignKey(Ads, related_name='images', on_delete=models.CASCADE, default=None, null=True)
    image = models.ImageField(upload_to='uploads/ads_images')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name_plural = "Ad Images"

    def __str__(self):
        return f"Image for {self.ad.title}"


# Banner Models
class AdsTopBanner(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Banner Title'))
    image = models.ImageField(upload_to='banners/top/', verbose_name=_('Banner Image'))
    link = models.URLField(blank=True, null=True, verbose_name=_('Banner Link'))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Top Banner')
        verbose_name_plural = _('Top Banners')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class AdsRightBanner(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Banner Title'))
    image = models.ImageField(upload_to='banners/right/', verbose_name=_('Banner Image'))
    link = models.URLField(blank=True, null=True, verbose_name=_('Banner Link'))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Right Banner')
        verbose_name_plural = _('Right Banners')
        ordering = ['-created_at']

    def __str__(self):
        return self.title

class AdsBottomBanner(models.Model):
    title = models.CharField(max_length=255, verbose_name=_('Banner Title'))
    image = models.ImageField(upload_to='banners/bottom/', verbose_name=_('Banner Image'))
    link = models.URLField(blank=True, null=True, verbose_name=_('Banner Link'))
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Bottom Banner')
        verbose_name_plural = _('Bottom Banners')
        ordering = ['-created_at']

    def __str__(self):
        return self.title