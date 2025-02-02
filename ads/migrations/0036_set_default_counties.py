from django.db import migrations

def set_default_counties(apps, schema_editor):
    City = apps.get_model('ads', 'City')
    County = apps.get_model('ads', 'County')
    
    # Default county mapping
    CITY_COUNTY_MAPPING = {
        # Coast Region
    'Voi': 'Taita-Taveta', 'Mwatate': 'Taita-Taveta', 'Taveta': 'Taita-Taveta', 'Wundanyi': 'Taita-Taveta',
    'Mombasa': 'Mombasa', 'Nyali': 'Mombasa', 'Likoni': 'Mombasa', 'Changamwe': 'Mombasa', 'Kisauni': 'Mombasa', 'Mtwapa': 'Kilifi',
    'Kwale': 'Kwale', 'Ukunda': 'Kwale', 'Msambweni': 'Kwale', 'Lunga Lunga': 'Kwale', 'Kinango': 'Kwale',
    'Kilifi': 'Kilifi', 'Malindi': 'Kilifi', 'Watamu': 'Kilifi', 'Kaloleni': 'Kilifi', 'Rabai': 'Kilifi',
    'Tana River': 'Tana River', 'Hola': 'Tana River', 'Garsen': 'Tana River', 'Bura': 'Tana River',
    'Lamu': 'Lamu', 'Mokowe': 'Lamu', 'Shela': 'Lamu', 'Faza': 'Lamu', 'Mpeketoni': 'Lamu', 'Witu': 'Lamu',
    
    # Nairobi Region
    'Nairobi': 'Nairobi', 'Karen': 'Nairobi', "Lang'ata": 'Nairobi', 'Westlands': 'Nairobi',
    'Embakasi': 'Nairobi', 'Kasarani': 'Nairobi', 'Gikambura': 'Nairobi', 'Kilimani': 'Nairobi', 
    'Donholm': 'Nairobi', 'Jogoo Road': 'Nairobi', 'Eastleigh': 'Nairobi', 'Buru Buru': 'Nairobi',
    'Pangani': 'Nairobi', 'Hurlingham': 'Nairobi', 'Parklands': 'Nairobi', 'Ziwani': 'Nairobi',
    'Kawangware': 'Nairobi', 'Kabete': 'Nairobi', 'South B': 'Nairobi', 'South C': 'Nairobi',
    'Kariobangi': 'Nairobi', 'Starehe': 'Nairobi',

    
    # Nyanza Region
    'Kisumu': 'Kisumu', 'Ahero': 'Kisumu', 'Muhoroni': 'Kisumu',
    'Homa Bay': 'Homa Bay', 'Kendu Bay': 'Homa Bay', 'Mbita': 'Homa Bay', 'Oyugis': 'Homa Bay',
    'Migori': 'Migori', 'Rongo': 'Migori', 'Awendo': 'Migori', 'Uriri': 'Migori',
    'Siaya': 'Siaya', 'Bondo': 'Siaya', 'Ugunja': 'Siaya', 'Yala': 'Siaya',
    'Kisii': 'Kisii', 'Ogembo': 'Kisii', 'Nyamache': 'Kisii', 'Suneka': 'Kisii',
    'Nyamira': 'Nyamira', 'Keroka': 'Nyamira', 'Nyansiongo': 'Nyamira', 'Ekerenyo': 'Nyamira',

    # Rift Valley Region
    'Nakuru': 'Nakuru', 'Naivasha': 'Nakuru', 'Gilgil': 'Nakuru', 'Molo': 'Nakuru', 'Njoro': 'Nakuru',
    'Uasin Gishu': 'Uasin Gishu', 'Kesses': 'Uasin Gishu', 'Moiben': 'Uasin Gishu', 'Burnt Forest': 'Uasin Gishu', 'Ziwa': 'Uasin Gishu',
    'Turkana': 'Turkana', 'Kakuma': 'Turkana', 'Lokichogio': 'Turkana', 'Kalokol': 'Turkana', 'Lokichar': 'Turkana',
    'West Pokot': 'West Pokot', 'Kacheliba': 'West Pokot', 'Alale': 'West Pokot', 'Sigor': 'West Pokot', 'Lomut': 'West Pokot',
    'Baringo': 'Baringo', 'Marigat': 'Baringo', 'Kabarnet': 'Baringo', 'Mogotio': 'Baringo', 'Eldama Ravine': 'Baringo',
    'Bomet': 'Bomet', 'Longisa': 'Bomet', 'Sotik': 'Bomet', 'Chepalungu': 'Bomet',
    'Kericho': 'Kericho', 'Litein': 'Kericho', 'Bureti': 'Kericho', 'Sosiot': 'Kericho',
    'Samburu': 'Samburu', 'Baragoi': 'Samburu', "Archer's Post": 'Samburu', 'Wamba': 'Samburu',
    'Trans-Nzoia': 'Trans-Nzoia', 'Kitale': 'Trans-Nzoia', 'Endebess': 'Trans-Nzoia', 'Kwanza': 'Trans-Nzoia',
    'Elgeyo-Marakwet': 'Elgeyo-Marakwet', 'Iten': 'Elgeyo-Marakwet', 'Kapsowar': 'Elgeyo-Marakwet', 'Chepkorio': 'Elgeyo-Marakwet',
    'Nandi': 'Nandi', 'Kapsabet': 'Nandi', 'Nandi Hills': 'Nandi', 'Mosoriot': 'Nandi',
    'Narok': 'Narok', 'Kilgoris': 'Narok', 'Emurua Dikirr': 'Narok', 'Ololulung\'a': 'Narok',

    # Western Region
    'Kakamega': 'Kakamega', 'Mumias': 'Kakamega', 'Malava': 'Kakamega', 'Butere': 'Kakamega', 'Khayega': 'Kakamega',
    'Bungoma': 'Bungoma', 'Webuye': 'Bungoma', 'Malakisi': 'Bungoma', 'Chwele': 'Bungoma', 'Naitiri': 'Bungoma',
    'Busia': 'Busia', 'Malaba': 'Busia', 'Nambale': 'Busia', 'Funyula': 'Busia',
    'Vihiga': 'Vihiga', 'Mbale': 'Vihiga', 'Luanda': 'Vihiga', 'Majengo': 'Vihiga',

    # Eastern Region
    'Embu': 'Embu', 'Runyenjes': 'Embu', 'Siakago': 'Embu', 'Manyatta': 'Embu',
    'Kitui': 'Kitui', 'Mwingi': 'Kitui', 'Mutomo': 'Kitui', 'Kwa Vonza': 'Kitui',
    'Machakos': 'Machakos', 'Athi River': 'Machakos', 'Mwala': 'Machakos', 'Kathiani': 'Machakos',
    'Makueni': 'Makueni', 'Makindu': 'Makueni', 'Sultan Hamud': 'Makueni', 'Kibwezi': 'Makueni',
    'Meru': 'Meru', 'Maua': 'Meru', 'Nkubu': 'Meru', 'Timau': 'Meru',
    'Tharaka-Nithi': 'Tharaka-Nithi', 'Marimanti': 'Tharaka-Nithi', 'Gatunga': 'Tharaka-Nithi', 'Magutuni': 'Tharaka-Nithi',

    # North Eastern Region
    'Garissa': 'Garissa', 'Dadaab': 'Garissa', 'Fafi': 'Garissa', 'Liboi': 'Garissa',
    'Isiolo': 'Isiolo', 'Garba Tulla': 'Isiolo', 'Merti': 'Isiolo', 'Kinna': 'Isiolo',
    'Mandera': 'Mandera', 'El Wak': 'Mandera', 'Takaba': 'Mandera', 'Rhamu': 'Mandera',
    'Marsabit': 'Marsabit', 'Laisamis': 'Marsabit', 'Loiyangalani': 'Marsabit', 'Maikona': 'Marsabit',
    'Wajir': 'Wajir', 'Habaswein': 'Wajir', 'Tarbaj': 'Wajir', 'Griftu': 'Wajir',

    # Central Region
    'Kiambu': 'Kiambu', 'Thika': 'Kiambu', 'Ruiru': 'Kiambu', 'Kikuyu': 'Kiambu',
    "Murang'a": "Murang'a", 'Kenol': "Murang'a", 'Maragua': "Murang'a", 'Kangema': "Murang'a",
    'Kirinyaga': 'Kirinyaga', 'Kerugoya': 'Kirinyaga', 'Sagana': 'Kirinyaga', 'Wanguru': 'Kirinyaga', 'Baricho': 'Kirinyaga',
    'Nyandarua': 'Nyandarua', 'Ol Kalou': 'Nyandarua', 'Ndaragwa': 'Nyandarua', 'Njabini': 'Nyandarua', 'Engineer': 'Nyandarua',
    'Nyeri': 'Nyeri', 'Karatina': 'Nyeri', 'Othaya': 'Nyeri', 'Mweiga': 'Nyeri',
    'Laikipia': 'Laikipia', 'Nanyuki': 'Laikipia', 'Rumuruti': 'Laikipia', 'Nyahururu': 'Laikipia', 'Dol Dol': 'Laikipia',

    # Kajiado County
    'Kajiado': 'Kajiado', 'Kitengela': 'Kajiado', 'Ngong': 'Kajiado', 'Kajiado Town': 'Kajiado', 'Isinya': 'Kajiado',
    }
    
    for city in City.objects.filter(county__isnull=True):
        county_name = CITY_COUNTY_MAPPING.get(city.city_name, 'Nairobi')
        county, _ = County.objects.get_or_create(county_name=county_name)
        city.county = county
        city.save()

def reverse_func(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0035_auto_20250202_0855')
    ]

    operations = [
        migrations.RunPython(set_default_counties, reverse_func),
    ]