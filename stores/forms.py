from django import forms
from .models import Product, Category

# --- 1. สร้าง Form สำหรับ Category ---
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        
        fields = ['name'] 

        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full p-2 border border-gray-300 rounded shadow-sm'
            }),
        }

# --- 2. อัปเดต ProductForm ให้เลือก Category ได้ ---
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        # --- อัปเดต 'fields' ให้ครบ ---
        fields = [
            'category', 
            'name', 
            'description', 
            'price',
            'stock',
            'image'
        ]
        
        # (ขั้นสูง) คุณสามารถใช้ widgets เพื่อจัดสไตล์ฟอร์มด้วย Tailwind ได้
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full p-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full p-2 border rounded', 'rows': 4}),
            'price': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'stock': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded'}),
            'image': forms.ClearableFileInput(attrs={'class': 'w-full p-2 border rounded'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # วนลูปทุก Field เพื่อใส่ Style ทีเดียว ไม่ต้องเขียนแยก
        for field_name, field in self.fields.items():
            # 1. กำหนด Class พื้นฐานให้สวยงาม และตัวหนังสือเข้ม (text-gray-900)
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f"{existing_classes} block w-full rounded-md border-0 py-1.5 text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-yellow-400 sm:text-sm sm:leading-6".strip()

            # 2. (ทางเลือก) ถ้าเป็นช่อง Image ไม่ต้องใส่ Style ของ Input text (เพราะเราทำ Custom Drag & Drop ไปแล้ว)
            if field_name == 'image':
                 field.widget.attrs['class'] = '' # ล้างค่าทิ้งเพื่อให้ตัว input file เดิมไม่กวนดีไซน์ใหม่