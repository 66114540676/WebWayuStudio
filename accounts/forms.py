from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.contrib.auth.forms import AuthenticationForm

# ==================== ฟอร์มสมัครสมาชิก ====================
class CustomUserCreationForm(UserCreationForm):
    
    image = forms.ImageField(label='รูปโปรไฟล์:', required=False,error_messages={'required': 'กรุณาเลือกรูปโปรไฟล์'})
    username = forms.CharField(label='ชื่อผู้ใช้:', max_length=150, required=True,error_messages={'required': 'กรุณากรอกชื่อผู้ใช้'})
    first_name = forms.CharField(label='ชื่อจริง:', max_length=150, required=True,error_messages={'required': 'กรุณากรอกชื่อจริง'})
    password1 = forms.CharField(label='รหัสผ่าน:', widget=forms.PasswordInput, required=True,error_messages={'required': 'กรุณากรอกรหัสผ่าน'})
    password2 = forms.CharField(label='ยืนยันรหัสผ่าน:', widget=forms.PasswordInput, required=True,error_messages={'required': 'กรุณากรอกยืนยันรหัสผ่าน'})
    last_name = forms.CharField(label='นามสกุล:', max_length=150, required=True,error_messages={'required': 'กรุณากรอกนามสกุล'})
    email = forms.EmailField(label='อีเมล:', required=True,error_messages={'required': 'กรุณากรอกอีเมล'})
    phone_number = forms.CharField(label='เบอร์โทรศัพท์:', max_length=20, required=True,error_messages={'required': 'กรุณากรอกเบอร์โทรศัพท์'})
    address = forms.CharField(label='ที่อยู่:', widget=forms.Textarea(attrs={'rows': 3}), required=True,error_messages={'required': 'กรุณากรอกที่อยู่'})

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("อีเมลนี้ถูกใช้งานไปแล้ว โปรดใช้อีเมลอื่น")
        return email
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("ชื่อผู้ใช้นี้มีอยู่ในระบบแล้ว โปรดใช้ชื่ออื่น")
        return username
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
            'phone_number',
            'address',
            'image',
        )
        labels = {
            'username':'ชื่อผู้ใช้:',
            'phone_number': 'เบอร์โทรศัพท์:',
            'address': 'ที่อยู่:',
            'image': 'รูปโปรไฟล์:',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['address'].widget = forms.Textarea(attrs={'rows': 3})
        self.fields['phone_number'].required = True
        self.fields['address'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)

        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.phone_number = self.cleaned_data.get('phone_number')
        user.address = self.cleaned_data.get('address')

        if commit:
            user.save()

        return user

    
# ==================== ฟอร์มแก้ไขโปรไฟล์ ====================
class CustomUserUpdateForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        
        fields = ['first_name', 'last_name', 'email', 
                  'image', 'phone_number', 'address']
        
        labels = {
            'first_name': 'ชื่อจริง',
            'last_name': 'นามสกุล',
            'email': 'อีเมล',
            'image': 'เปลี่ยนรูปโปรไฟล์',
            'phone_number': 'เบอร์โทรศัพท์',
            'address': 'ที่อยู่'
        }
        
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }
        
        
# ==================== ฟอร์มล็อกอิน ====================
class UserLoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # เปลี่ยนข้อความ Error ของช่อง Username
        self.fields['username'].error_messages.update({
            'required': 'กรุณากรอกชื่อผู้ใช้',
            'invalid': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
        })
        
        # เปลี่ยนข้อความ Error ของช่อง Password
        self.fields['password'].error_messages.update({
            'required': 'กรุณากรอกรหัสผ่าน',
            'invalid': 'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง'
        })