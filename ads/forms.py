from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Ads, Author, County, City, Category
from django.core.validators import RegexValidator
from .models import phone_validator

class PostAdsForm(forms.ModelForm):
    # Phone number validator for Kenyan format
    phone_validator = RegexValidator(
        regex=r'^\+?254?\d{9}$',
        message="Phone number must be a valid Kenyan phone number (e.g., +254712345678)"
    )

    title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control ad-post-form',
            'placeholder': 'e.g. House for sale',
            'maxlength': '200'
        })
    )

    description = forms.CharField(
        widget=CKEditorWidget(attrs={
            'class': 'form-control ad-post-form',
            'rows': '6',
            'placeholder': 'Provide as much detail as possible'
        })
    )

    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control ad-post-form',
            'placeholder': 'e.g. 2500'
        })
    )

    condition = forms.ChoiceField(
        choices=Ads.CONDITION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control ad-post-form'
        })
    )

    county = forms.ModelChoiceField(
        queryset=County.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control ad-post-form'
        })
    )

    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control ad-post-form'
        })
    )


    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control ad-post-form',
            'placeholder': 'Select Category'
        })
    )

    subcategory = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={
            'class': 'form-control ad-post-form',
            'placeholder': 'Select Subcategory'
        }),
        required=False
    )

    phone_number = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control ad-post-form',
            'placeholder': '+254712345678'
        }),
        validators=[phone_validator]
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control ad-post-form',
            'placeholder': 'e.g. example@example.com'
        })
    )

    brand = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control ad-post-form',
            'placeholder': 'e.g. Sony, Samsung, etc.'
        }),
        required=False
    )

    video_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control ad-post-form',
            'placeholder': 'e.g. YouTube video URL'
        }),
        required=False
    )

    class Meta:
        model = Ads
        fields = [
            'title',
            'description',
            'category',
            'subcategory',
            'price',
            'condition',
            'county',
            'city',
            'phone_number',
            'email',
            'brand',
            'video_url',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set all fields as required by default
        for field in self.fields:
            self.fields[field].required = True
        
        # Set optional fields
        self.fields['brand'].required = False
        self.fields['video_url'].required = False
        self.fields['subcategory'].required = False

        