from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.db import transaction
from .models import User, LocalCouncil, DistrictCSO, MDA, MLGRD, Assignment, Role, Ministry
from email import message
from django.core.validators import RegexValidator, FileExtensionValidator
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from schools.models import District

GENDER = (
    ('', 'Select a gender'),
    ('Male', 'Male'),
    ('Female','Female')
)

DISTRICT = (
        ('', 'Select a district'),
        ('Falaba', 'Falaba'),
        ('Karene', 'Karene'),
        ('Kono', 'Kono'),
        ('Moyamba', 'Moyamba'),
        ('Tonkolili', 'Tonkolili'),
        ('Western Rural', 'Western Rural'),
)

class LocalCouncilRegisterForm(UserCreationForm):
    username = forms.CharField(label="Username", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Username cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Username', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    password1 = forms.CharField(label="Password", min_length=3, required=True, error_messages={'required':'Password cannot be empty'},
                                widget=forms.PasswordInput(attrs={'placeholder':'Password', 'style':'font-size: 13px;'}))
    
    password2 = forms.CharField(label="Password confirmation", min_length=3, required=True, error_messages={'required':'Confirm password cannot be empty'},
                                widget=forms.PasswordInput(attrs={'placeholder':'Password confirmation', 'style':'font-size: 13px;'}))
    
    first_name = forms.CharField(label="First Name", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'First name cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'First name', 'autofocus': 'autofocus', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    last_name = forms.CharField(label="Last Name", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Last name cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Last name', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    email = forms.CharField(label="Email", min_length=8, required=True, error_messages={'required':'Email cannot be empty'}, widget=forms.TextInput(attrs={'placeholder':'Email',
                            'style':'font-size: 13px; text-transform: lowercase'}))
    
    gender = forms.ChoiceField(widget=forms.Select(attrs={"class":"form-control"}), choices=GENDER, error_messages={'required':'Gender cannot be empty'},)
    
    phone_number = PhoneNumberField(label="Phone Number", required=True, error_messages={'required':'Phone number cannot be empty'},
                                widget=forms.TextInput(attrs={'class':" form-control", 'style':'font-size: 13px', 'placeholder':'Example: +23276000000'}))
    
    position = forms.CharField(label="Position/Title", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Position cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Last name', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    profile_pic = forms.FileField(label="Upload your profile picture", required=False, help_text="Allowed file type: JPG, JPEG, PNG. Maximum file size: 5MB.",
                                widget=forms.ClearableFileInput(attrs={'class':'form-control', 'style':'font-size: 13px', 'accept': 'image/png, image/jpeg, image/jpg'}))
    
    district = forms.ChoiceField(widget=forms.Select(attrs={"class":"form-control"}), choices=DISTRICT, error_messages={'required':'District cannot be empty'},)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        for obj in LocalCouncil.objects.all():
            if obj.email == email:
                raise forms.ValidationError("Denied! " + email + " is already registered.")
        return email

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'district', 'gender', 'profile_pic',
                'position')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_local_council = True
        user.username = self.cleaned_data.get('username')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.password1 = self.cleaned_data.get('password1')
        user.password2 = self.cleaned_data.get('password2')
        user.save()
        local_council = LocalCouncil.objects.create(user=user)
        local_council.username = self.cleaned_data.get('username')
        local_council.first_name = self.cleaned_data.get('first_name')
        local_council.last_name = self.cleaned_data.get('last_name')
        local_council.email = self.cleaned_data.get('email')
        local_council.password1 = self.cleaned_data.get('password1')
        local_council.password2 = self.cleaned_data.get('password2')
        local_council.phone_number = self.cleaned_data.get('phone_number')
        local_council.district = self.cleaned_data.get('district')
        local_council.gender = self.cleaned_data.get('gender')
        local_council.profile_pic = self.cleaned_data.get('profile_pic')
        local_council.position = self.cleaned_data.get('position')
        local_council.save()
        return user


class DistrictCSORegisterForm(UserCreationForm):
    username = forms.CharField(label="Username", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Username cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Username', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    password1 = forms.CharField(label="Password", min_length=3, required=True, error_messages={'required':'Password cannot be empty'},
                                widget=forms.PasswordInput(attrs={'placeholder':'Password', 'style':'font-size: 13px;'}))
    
    password2 = forms.CharField(label="Password confirmation", min_length=3, required=True, error_messages={'required':'Confirm password cannot be empty'},
                                widget=forms.PasswordInput(attrs={'placeholder':'Password confirmation', 'style':'font-size: 13px;'}))
    
    first_name = forms.CharField(label="First Name", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'First name cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'First name', 'autofocus': 'autofocus', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    last_name = forms.CharField(label="Last Name", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Last name cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Last name', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    email = forms.CharField(label="Email", min_length=8, required=True, error_messages={'required':'Email cannot be empty'}, widget=forms.TextInput(attrs={'placeholder':'Email',
                            'style':'font-size: 13px; text-transform: lowercase'}))
    
    gender = forms.ChoiceField(widget=forms.Select(attrs={"class":"form-control"}), choices=GENDER, error_messages={'required':'Gender cannot be empty'},)
    
    phone_number = PhoneNumberField(label="Phone Number", required=True, error_messages={'required':'Phone number cannot be empty'},
                                widget=forms.TextInput(attrs={'class':" form-control", 'style':'font-size: 13px', 'placeholder':'Example: +23276000000'}))
    
    position = forms.CharField(label="Position/Title", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Position cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Last name', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    profile_pic = forms.FileField(label="Upload your profile picture", required=False, help_text="Allowed file type: JPG, JPEG, PNG. Maximum file size: 5MB.",
                                widget=forms.ClearableFileInput(attrs={'class':'form-control', 'style':'font-size: 13px', 'accept': 'image/png, image/jpeg, image/jpg'}))
    
    district = forms.ChoiceField(widget=forms.Select(attrs={"class":"form-control"}), choices=DISTRICT, error_messages={'required':'District cannot be empty'},)
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        for obj in DistrictCSO.objects.all():
            if obj.email == email:
                raise forms.ValidationError("Denied! " + email + " is already registered.")
        return email

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'district', 'gender', 'profile_pic',
                'position')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_district_cso = True
        user.username = self.cleaned_data.get('username')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.password1 = self.cleaned_data.get('password1')
        user.password2 = self.cleaned_data.get('password2')
        user.save()
        district_cso = DistrictCSO.objects.create(user=user)
        district_cso.username = self.cleaned_data.get('username')
        district_cso.first_name = self.cleaned_data.get('first_name')
        district_cso.last_name = self.cleaned_data.get('last_name')
        district_cso.email = self.cleaned_data.get('email')
        district_cso.password1 = self.cleaned_data.get('password1')
        district_cso.password2 = self.cleaned_data.get('password2')
        district_cso.phone_number = self.cleaned_data.get('phone_number')
        district_cso.district = self.cleaned_data.get('district')
        district_cso.gender = self.cleaned_data.get('gender')
        district_cso.profile_pic = self.cleaned_data.get('profile_pic')
        district_cso.position = self.cleaned_data.get('position')
        district_cso.save()
        return user


class MDARegisterForm(UserCreationForm):
    username = forms.CharField(label="Username", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Username cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Username', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    password1 = forms.CharField(label="Password", min_length=3, required=True, error_messages={'required':'Password cannot be empty'},
                                widget=forms.PasswordInput(attrs={'placeholder':'Password', 'style':'font-size: 13px;'}))
    
    password2 = forms.CharField(label="Password confirmation", min_length=3, required=True, error_messages={'required':'Confirm password cannot be empty'},
                                widget=forms.PasswordInput(attrs={'placeholder':'Password confirmation', 'style':'font-size: 13px;'}))
    
    first_name = forms.CharField(label="First Name", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'First name cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'First name', 'autofocus': 'autofocus', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    last_name = forms.CharField(label="Last Name", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Last name cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Last name', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    email = forms.CharField(label="Email", min_length=8, required=True, error_messages={'required':'Email cannot be empty'}, widget=forms.TextInput(attrs={'placeholder':'Email',
                            'style':'font-size: 13px; text-transform: lowercase'}))
    
    gender = forms.ChoiceField(widget=forms.Select(attrs={"class":"form-control"}), choices=GENDER, error_messages={'required':'Gender cannot be empty'},)
    
    phone_number = PhoneNumberField(label="Phone Number", required=True, error_messages={'required':'Phone number cannot be empty'},
                                widget=forms.TextInput(attrs={'class':" form-control", 'style':'font-size: 13px', 'placeholder':'Example: +23276000000'}))
    
    position = forms.CharField(label="Position/Title", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Position cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Last name', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    profile_pic = forms.FileField(label="Upload your profile picture", required=False, help_text="Allowed file type: JPG, JPEG, PNG. Maximum file size: 5MB.",
                                widget=forms.ClearableFileInput(attrs={'class':'form-control', 'style':'font-size: 13px', 'accept': 'image/png, image/jpeg, image/jpg'}))
    
    district = forms.ChoiceField(widget=forms.Select(attrs={"class":"form-control"}), choices=DISTRICT, error_messages={'required':'District cannot be empty'},)
    
    ministry = forms.ModelChoiceField(queryset=Ministry.objects.all(), empty_label="Select Ministry", required=True, error_messages={'required': 'Ministry cannot be empty'},
        widget=forms.Select(attrs={"class": "form-control"}))
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        for obj in MDA.objects.all():
            if obj.email == email:
                raise forms.ValidationError("Denied! " + email + " is already registered.")
        return email

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'district', 'gender', 'profile_pic',
                'position', 'ministry')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_mda = True
        user.username = self.cleaned_data.get('username')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.password1 = self.cleaned_data.get('password1')
        user.password2 = self.cleaned_data.get('password2')
        user.save()
        mda = MDA.objects.create(user=user)
        mda.username = self.cleaned_data.get('username')
        mda.first_name = self.cleaned_data.get('first_name')
        mda.last_name = self.cleaned_data.get('last_name')
        mda.email = self.cleaned_data.get('email')
        mda.password1 = self.cleaned_data.get('password1')
        mda.password2 = self.cleaned_data.get('password2')
        mda.phone_number = self.cleaned_data.get('phone_number')
        mda.district = self.cleaned_data.get('district')
        mda.gender = self.cleaned_data.get('gender')
        mda.profile_pic = self.cleaned_data.get('profile_pic')
        mda.position = self.cleaned_data.get('position')
        mda.ministry = self.cleaned_data.get('ministry')
        mda.save()
        return user
    
class MLGRDRegisterForm(UserCreationForm):
    username = forms.CharField(label="Username", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Username cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Username', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    password1 = forms.CharField(label="Password", min_length=3, required=True, error_messages={'required':'Password cannot be empty'},
                                widget=forms.PasswordInput(attrs={'placeholder':'Password', 'style':'font-size: 13px;'}))
    
    password2 = forms.CharField(label="Password confirmation", min_length=3, required=True, error_messages={'required':'Confirm password cannot be empty'},
                                widget=forms.PasswordInput(attrs={'placeholder':'Password confirmation', 'style':'font-size: 13px;'}))
    
    first_name = forms.CharField(label="First Name", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'First name cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'First name', 'autofocus': 'autofocus', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    last_name = forms.CharField(label="Last Name", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Last name cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Last name', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    email = forms.CharField(label="Email", min_length=8, required=True, error_messages={'required':'Email cannot be empty'}, widget=forms.TextInput(attrs={'placeholder':'Email',
                            'style':'font-size: 13px; text-transform: lowercase'}))
    
    gender = forms.ChoiceField(widget=forms.Select(attrs={"class":"form-control"}), choices=GENDER, error_messages={'required':'Gender cannot be empty'},)
    
    phone_number = PhoneNumberField(label="Phone Number", required=True, error_messages={'required':'Phone number cannot be empty'},
                                widget=forms.TextInput(attrs={'class':" form-control", 'style':'font-size: 13px', 'placeholder':'Example: +23276000000'}))
    
    position = forms.CharField(label="Position/Title", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$', message="Only letter is allowed!")], error_messages={'required':'Position cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Last name', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    profile_pic = forms.FileField(label="Upload your profile picture", required=False, help_text="Allowed file type: JPG, JPEG, PNG. Maximum file size: 5MB.",
                                widget=forms.ClearableFileInput(attrs={'class':'form-control', 'style':'font-size: 13px', 'accept': 'image/png, image/jpeg, image/jpg'}))
    
    district = forms.ChoiceField(widget=forms.Select(attrs={"class":"form-control"}), choices=DISTRICT, error_messages={'required':'District cannot be empty'},)
    
    ministry = forms.ModelChoiceField(queryset=Ministry.objects.all(), empty_label="Select Ministry", required=True, error_messages={'required': 'Ministry cannot be empty'},
        widget=forms.Select(attrs={"class": "form-control"}))
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        for obj in MLGRD.objects.all():
            if obj.email == email:
                raise forms.ValidationError("Denied! " + email + " is already registered.")
        return email

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'district', 'gender', 'profile_pic',
                'position', 'ministry')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_mlgrd = True
        user.username = self.cleaned_data.get('username')
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.password1 = self.cleaned_data.get('password1')
        user.password2 = self.cleaned_data.get('password2')
        user.save()
        mlgrd = MLGRD.objects.create(user=user)
        mlgrd.username = self.cleaned_data.get('username')
        mlgrd.first_name = self.cleaned_data.get('first_name')
        mlgrd.last_name = self.cleaned_data.get('last_name')
        mlgrd.email = self.cleaned_data.get('email')
        mlgrd.password1 = self.cleaned_data.get('password1')
        mlgrd.password2 = self.cleaned_data.get('password2')
        mlgrd.phone_number = self.cleaned_data.get('phone_number')
        mlgrd.district = self.cleaned_data.get('district')
        mlgrd.gender = self.cleaned_data.get('gender')
        mlgrd.profile_pic = self.cleaned_data.get('profile_pic')
        mlgrd.position = self.cleaned_data.get('position')
        mlgrd.ministry = self.cleaned_data.get('ministry')
        mlgrd.save()
        return user
    
    
def login_form(request):
    username = forms.CharField(label="Username", min_length=3, validators= [RegexValidator(r'^[a-zA-Z\s]*$',
                                message="Only letter is allowed!")], error_messages={'required':'Username cannot be empty'}, required=True,
                                widget=forms.TextInput(attrs={'placeholder':'Username', 'autofocus': 'autofocus', 'style':'font-size: 13px; text-transform: capitalize'}))
    
    password1 = forms.CharField(label="Password", min_length=3, required=True, error_messages={'required':'Password cannot be empty'},
                                widget=forms.PasswordInput(attrs={'placeholder':'Password', 'style':'font-size: 13px;'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1')

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['indicator', 'district', 'assigned_to', 'role']