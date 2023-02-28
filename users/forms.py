from django import forms
from django.contrib.auth.models import User
from . models import KhachHang, Customer


class FormDangKy(forms.ModelForm):
    ho = forms.CharField(max_length=264, label="Họ", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Họ",
        "required": "required"
    }))
    ten = forms.CharField(max_length=264, label="Tên", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Tên",
        "required": "required"
    }))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Email"
    }))
    mat_khau = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Mật khẩu",
        "required": "required"
    }))
    xac_nhan_mat_khau = forms.CharField(label="Xác nhận Mật khẩu", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Xác nhận Mật khẩu",
        "required": "required"
    }))
    dien_thoai = forms.CharField(max_length=20, label="Điện thoại", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Điện thoại",
        "required": "required"
    }))
    dia_chi = forms.CharField(label="Địa chỉ", widget=forms.Textarea(attrs={
        "class": "form-control",
        "placeholder": "Địa chỉ",
        "rows": "3",
        "required": "required"
    }))

    class Meta:
        model = KhachHang
        fields = ['ho', 'ten', 'email', 'mat_khau', 'dien_thoai', 'dia_chi']


class FormUser(forms.ModelForm):
    last_name = forms.CharField(max_length=264, label="Họ", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Họ",
        "required": "required"
    }))
    first_name = forms.CharField(max_length=264, label="Tên", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Tên",
        "required": "required"
    }))
    username = forms.CharField(max_length=264, label="Username", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Username",
        "required": "required"
    }))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={
        "class": "form-control",
        "placeholder": "Email"
    }))
    password = forms.CharField(label="Mật khẩu", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Mật khẩu",
        "required": "required"
    }))
    confirm_password = forms.CharField(label="Xác nhận Mật khẩu", widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "placeholder": "Xác nhận Mật khẩu",
        "required": "required"
    }))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password')


class FormCustomer(forms.ModelForm):
    dien_thoai = forms.CharField(max_length=20, label="Điện thoại", widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Điện thoại",
        "required": "required"
    }))
    dia_chi = forms.CharField(label="Địa chỉ", widget=forms.Textarea(attrs={
        "class": "form-control",
        "placeholder": "Địa chỉ",
        "rows": "3",
        "required": "required"
    }))

    class Meta:
        model = Customer
        exclude = ('user',)
        #fields = ('dien_thoai','dia_chi')