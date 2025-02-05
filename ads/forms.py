from django import forms
from ckeditor.widgets import CKEditorWidget
from .models import Ads, Author, County, City, Category, CITY_COUNTY_MAPPING
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
        max_digits=1000,
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

    images = forms.ImageField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control ad-post-form',
            'multiple': True,
            'accept': 'image/*'
        }),
        required=False,
        help_text='Max 5 images, 3MB each'
    )

    video_url = forms.URLField(
        widget=forms.URLInput(attrs={
            'class': 'form-control ad-post-form',
            'placeholder': 'e.g. YouTube video URL'
        }),
        required=False
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].required = True
        
        self.fields['brand'].required = False
        self.fields['video_url'].required = False
        self.fields['city'].required = False

        self.fields['city'].queryset = City.objects.none()

        if 'county' in self.data:
            try:
                county_id = int(self.data.get('county'))
                self.fields['city'].queryset = City.objects.filter(county_id=county_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['city'].queryset = City.objects.filter(county=self.instance.county)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.author = self.user.author
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Ads
        fields = [
            'title',
            'description',
            'category',
            'price',
            'condition',
            'county',
            'city',
            'phone_number',
            'email',
            'brand',
            'video_url',
            'images'
        ]