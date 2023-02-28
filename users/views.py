from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import PBKDF2SHA1PasswordHasher
from django.contrib.auth.models import User
from . models import KhachHang, Customer
from . forms import FormDangKy, FormCustomer, FormUser
from cart.cart import Cart
from cart.models import Order, OrderItem
from store.models import Product


def signup_login(request):
    form = FormDangKy()
    result = ''

    if request.POST.get('btnSignup'):
        form = FormDangKy(request.POST, KhachHang)
        if form.is_valid() and form.cleaned_data['mat_khau'] == form.cleaned_data['xac_nhan_mat_khau']:
            hasher = PBKDF2SHA1PasswordHasher()
            post = form.save(commit=False)
            post.ho = form.cleaned_data['ho']
            post.ten = form.cleaned_data['ten']
            post.dien_thoai = form.cleaned_data['dien_thoai']
            post.email = form.cleaned_data['email']
            # post.mat_khau = form.cleaned_data['mat_khau']
            post.mat_khau = hasher.encode(form.cleaned_data['mat_khau'], 'abcd1234')
            post.dia_chi = form.cleaned_data['dia_chi']
            post.save()

            result = '''
                <div class="alert alert-success" role="alert">
                    Submit Successfully!!!Đã đăng ký thành công
                </div>
            '''
        else:
            result = '''
                <div class="alert alert-danger" role="alert">
                    Submit Failed!!! Mật khẩu không trùng nhau!
                </div>
            '''

    if request.POST.get('btnLogin'):
        email = request.POST.get('email')
        password = request.POST.get('password')
        hasher = PBKDF2SHA1PasswordHasher()
        encrypt_password = hasher.encode(password, 'abcd1234')

        khachhang = KhachHang.objects.filter(email=email, mat_khau=encrypt_password)
        if khachhang.exists():
            request.session['s_customer'] = khachhang.values()[0]
            return redirect('store:index')
        else:
            result = '''
                <div class="alert alert-danger" role="alert">
                    Submit Failed!!! Email hoặc mật khẩu không đúng
                </div>
            '''

    return render(request, 'users/login.html', {
        'form': form,
        'result': result
    })


def user_logout(request):
    if 's_custormer' in request.session:
        del request.session['s_customer']

    return redirect('user:login')


def signup_login2(request):
    form_user = FormUser()
    form_customer = FormCustomer()
    result = ''
    
    if request.POST.get('btnSignup'):
        form_user = FormUser(request.POST)
        form_customer = FormCustomer(request.POST)
        if form_user.is_valid() and form_customer.is_valid():
            if form_user.cleaned_data['password'] == form_user.cleaned_data['confirm_password']:
                #User
                user = form_user.save()
                user.set_password(user.password)
                user.save()

                #Customer
                customer = form_customer.save(commit=False)
                customer.user = user
                customer.dien_thoai = form_customer.cleaned_data['dien_thoai']
                customer.dia_chi = form_customer.cleaned_data['dia_chi']
                customer.save()

                result = '''
                <div class="alert alert-success" role="alert">
                    Submit Successfully!!!Đã đăng ký thành công
                </div>
            '''
        else:
            result = '''
                <div class="alert alert-danger" role="alert">
                    Submit Failed!!! Mật khẩu không trùng nhau!
                </div>
            '''

    if request.POST.get('btnLogin'):
        username = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('store:index')
        else:
            result = '''
                <div class="alert alert-danger" role="alert">
                    Submit Failed!!! Email hoặc mật khẩu không đúng
                </div>
            '''

    return render(request, 'users/login2.html', {
        'form_user': form_user,
        'form_customer': form_customer,
        'result': result
    })


def user_logout2(request):
    logout(request)

    return redirect('user:login2')


def myaccount(request):
    if not request.user.username:
        return redirect('user:login2')
    
    cart = Cart(request)

    if request.POST.get('btnUpdateUser'):
        ho = request.POST.get('last_name')
        ten = request.POST.get('first_name')
        email = request.POST.get('email')
        dien_thoai = request.POST.get('mobile')
        dia_chi = request.POST.get('address')

        s_user = request.user
        customer = Customer.objects.get(user__id=s_user.id)
        customer.user.last_name = ho
        customer.user.first_name = ten
        customer.user.email = email
        customer.dia_chi = dia_chi
        customer.dien_thoai = dien_thoai
        customer.save()

        s_user.last_name = ho
        s_user.first_name = ten
        s_user.email = email

        messages.success(request, "Đã cập nhật thông tin thành công")

    orders = Order.objects.filter(username=request.user.username)
    dict_orders = {}
    for order in orders:
        order_items = list(OrderItem.objects.filter(order=order.id).values())
        for item in order_items:
            product = Product.objects.get(pk=item['product_id'])
            item['product_name'] = product.name
            item['product_image'] = product.image
            item['total_price'] = order.total
        else:
            dict_order_items = {
                order.pk: order_items
            }
            dict_orders.update(dict_order_items)

    return render(request, 'users/my-account.html',{
        'cart': cart,
        'orders': orders,
        'dict_orders': dict_orders
    })