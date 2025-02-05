from django.db import models
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import uuid
from django.db.models import Q, Count, F

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

# Messages Model   
class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    ad = models.ForeignKey('Ads', on_delete=models.CASCADE, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_time = models.DateTimeField(null=True, blank=True)
    unread_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-updated_at']
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=['ad'],
        #         condition=Q(participants__isnull=False),
        #         name='unique_conversation_per_ad'
        #     )
        # ]
        indexes = [
            models.Index(fields=['-updated_at']),
            models.Index(fields=['-last_message_time']),
            models.Index(fields=['unread_count']),
        ]

    def __str__(self):
        participants = self.participants.values_list('username', flat=True)
        return f"Conversation about {self.ad} between {', '.join(participants)}"

    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()

    @property
    def unread_messages(self):
        return self.messages.filter(read=False, receiver=self.user).count()

    def get_unread_messages_for_user(self, user):
        return self.messages.filter(read=False, receiver=user).count() 
    
    def latest_message(self):
        return self.messages.select_related('sender', 'receiver').first()

    def update_unread_count(self, user=None):
        query = self.messages.filter(is_read=False)
        if user:
            query = query.filter(receiver=user)
        self.unread_count = query.count()
        self.save(update_fields=['unread_count'])

    def mark_messages_read(self, user):
        messages_updated = self.messages.filter(
            receiver=user,
            is_read=False
        ).update(is_read=True)
        
        if messages_updated:
            self.update_unread_count(user)
            self.save(update_fields=['updated_at'])
        
        return messages_updated

    @classmethod
    @classmethod
    def get_or_create_conversation(cls, user1, user2, ad):
        conversation = cls.objects.filter(
            participants=user1
        ).filter(
            participants=user2
        ).filter(
            ad=ad
        ).first()
        
        if not conversation:
            conversation = cls.objects.create(ad=ad)
            conversation.participants.add(user1, user2)
        
        return conversation

    def get_other_participant(self, user):
        return self.participants.exclude(id=user.id).first()
    
    
    @classmethod
    def get_user_conversations(cls, user):
        return cls.objects.filter(
            participants=user
        ).annotate(
            unread_messages=Count(
                'messages',
                filter=Q(messages__is_read=False, messages__receiver=user)
            )
        ).select_related('ad').prefetch_related('participants')

    @classmethod
    def get_conversation_with_messages(cls, conversation_id, user):
        return cls.objects.filter(
            id=conversation_id,
            participants=user
        ).prefetch_related(
            models.Prefetch(
                'messages',
                queryset=Message.objects.select_related('sender', 'receiver')
            )
        ).first()

    def update_last_message_time(self):
        latest = self.messages.first()
        if latest:
            self.last_message_time = latest.created_at
            self.save(update_fields=['last_message_time', 'updated_at'])

class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, 
        related_name='messages', 
        on_delete=models.CASCADE, 
        null=True,  # Keep this temporarily
        default=None  
    )
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    ad = models.ForeignKey('Ads', on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_read']),
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} about {self.ad}"

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        
        if not hasattr(self, 'conversation'):
            self.conversation = Conversation.get_or_create_conversation(
                self.sender,
                self.receiver,
                self.ad
            )

        super().save(*args, **kwargs)

        if is_new:
            self.conversation.last_message_time = self.created_at
            self.conversation.unread_count = F('unread_count') + 1
            self.conversation.save(
                update_fields=['last_message_time', 'updated_at', 'unread_count']
            )

        read = models.BooleanField(default=False)

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


# City-County Mapping
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
    county = models.ForeignKey(County, on_delete=models.CASCADE)

    def clean(self):
        if self.city_name and self.county:
            expected_county = CITY_COUNTY_MAPPING.get(self.city_name)
            if expected_county and expected_county != self.county.county_name:
                raise ValidationError({
                    'county': f'This city belongs to {expected_county} county, not {self.county.county_name}'
                })

    def save(self, *args, **kwargs):
        # First validate
        self.clean()
        
        # Auto-assign county if not set
        if not self.county:
            county_name = CITY_COUNTY_MAPPING.get(self.city_name)
            if county_name:
                county, _ = County.objects.get_or_create(county_name=county_name)
                self.county = county
        
        # Generate slug
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
        ordering = ['city_name']

    def __str__(self):
        return f"{self.city_name} ({self.county.county_name})"
    

# category model
class Category(models.Model):
    CATEGORY_CHOICES = [
        ('Cars', 'Cars'),
        ('Buses & Microbuses', 'Buses & Microbuses'),
        ('Heavy Equipment', 'Heavy Equipment'),
        ('Motorcycles', 'Motorcycles'),
        ('Trucks', 'Trucks'),
        ('Other Vehicles', 'Other Vehicles'),
        ('New Builds', 'New Builds'),
        ('Houses & Apartments for Rent', 'Houses & Apartments for Rent'),
        ('Houses & Apartments for Sale', 'Houses & Apartments for Sale'),
        ('Land for Sale', 'Land for Sale'),
        ('Commercial Property', 'Commercial Property'),
        ('Other Property', 'Other Property'),
        ('Phones', 'Phones'),
        ('Laptops', 'Laptops'),
        ('Desktops', 'Desktops'),
        ('Tablets', 'Tablets'),
        ('Televisions', 'Televisions'),
        ('Other Electronics', 'Other Electronics'),
        ('Men\'s Fashion', 'Men\'s Fashion'),
        ('Women\'s Fashion', 'Women\'s Fashion'),
        ('Kids\' Fashion', 'Kids\' Fashion'),
        ('Other Fashion', 'Other Fashion'),
        ('Furniture', 'Furniture'),
        ('Appliances', 'Appliances'),
        ('Home Decor', 'Home Decor'),
        ('Office Equipment', 'Office Equipment'),
        ('Other Home & Office', 'Other Home & Office'),
        ('Jobs', 'Jobs'),
        ('Services', 'Services'),
        ('Livestock', 'Livestock'),
        ('Farming Equipment', 'Farming Equipment'),
        ('Other Agriculture', 'Other Agriculture'),
        ('Fitness', 'Fitness'),
        ('Sports Equipment', 'Sports Equipment'),
        ('Other Sports & Outdoors', 'Other Sports & Outdoors'),
        ('Food', 'Food'),
        ('Beverages', 'Beverages'),
        ('Health', 'Health'),
        ('Beauty', 'Beauty'),
        ('Other', 'Other'),
        ('Adult Products', 'Adult Products'),
        ('Intimacy & Relationships', 'Intimacy & Relationships')
    ]

    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        default='Other'
    )
    
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.category)
            unique_slug = base_slug
            counter = 1
            while Category.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name_plural = "Categories"

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