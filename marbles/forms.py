from django import forms
from .models import CustomMarblesOrder

class CustomMarblesOrderForm(forms.ModelForm):
    class Meta:
        model = CustomMarblesOrder
        fields = [
            # ตัด customer_name, customer_tel ออกแล้ว
            'deceased_name', 'deceased_photo', 
            'birth_date', 'death_date', 
            'stone_style', 'size', 'note'
        ]
        widgets = {
            # Input วันที่
            'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'death_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            
            # Input อื่นๆ
            'deceased_name': forms.TextInput(attrs={'class': 'form-control'}),
            'deceased_photo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'stone_style': forms.Select(attrs={'class': 'form-select'}),
            'size': forms.Select(attrs={'class': 'form-select', 'id': 'id_size'}), # id ยังคงสำคัญสำหรับ script ราคา
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }