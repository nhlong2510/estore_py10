from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings
from datetime import datetime
from .cart import Cart
from .vnpay import vnpay, get_client_ip
from . models import Order, OrderItem
from store.models import Product
from users.models import Customer


def cart_detail(request):
    cart = Cart(request)

    if request.POST.get('btnCoupon'):
        coupon_code = request.POST.get('coupon_code')
        if coupon_code=='PY10':
            cart_new={}
            for c in cart:
                product = c['product']
                product_cart = {
                    'quantity': c['quantity'],
                    'price': str(product.price),
                    'coupon': '0.9',
                }
                cart_new.update(product_cart)
                c['coupon'] = 0.9
            request.session['cart'] = cart_new
        else:
            messages.error(request, "Mã không hợp lệ")

    if request.POST.get('btnUpdateCart'):
        cart_new = {}
        for c in cart:
            product = c['product']
            quantity_new = int(request.POST.get('quantity_' + str(product.pk)))
            if quantity_new != 0:
                product_cart = {
                    str(product.pk): {
                        'quantity': quantity_new,
                        'price': str(product.price),
                        'coupon': str(c['coupon'])
                    }
                }
                cart_new.update(product_cart)
                c['quantity'] = quantity_new
            else:
                cart.remove(product)
        request.session['cart'] = cart_new

    return render(request, 'cart/cart.html', {
        'cart': cart
    })


@require_POST
def buy_now(request, product_id):
    cart = Cart(request)
    product = Product.objects.get(id=product_id)
    if request.POST.get('quantity'):
        cart.add(product=product, quantity=int(request.POST.get('quantity')))
    
    return redirect('cart:cart_detail')


@require_POST
def remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product=product)

    return redirect('cart:cart_detail')


def checkout(request):
    cart = Cart(request)
    customer = Customer.objects.get(user__id=request.user.id)
    if request.POST.get('btnCheckout'):
        order = Order()

        order.username = request.user.username
        order.last_name = request.user.last_name
        order.first_name = request.user.first_name
        order.phone = customer.dien_thoai
        order.address = customer.dia_chi
        order.total = cart.get_final_total_price()
        order.save()

        for c in cart:
            OrderItem.objects.create(order=order, product=c['product'], price=c['price'], quantity=c['quantity'])

        ipaddr = get_client_ip(request)

        vnp = vnpay()
        vnp.requestData['vnp_Version'] = '2.1.0'
        vnp.requestData['vnp_Command'] = 'pay'
        vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
        vnp.requestData['vnp_Amount'] = int(order.total) * 100
        vnp.requestData['vnp_CurrCode'] = 'VND'
        vnp.requestData['vnp_TxnRef'] = datetime.strftime(datetime.now(),'%Y%m%d%H%M%S')+str(order.id)
        vnp.requestData['vnp_OrderInfo'] = 'Thanh toan don hang thoi gian: ' + datetime.strftime(datetime.now(),'%d-%m-%Y %H:%M:%S')
        vnp.requestData['vnp_OrderType'] = 'Thanh toán hóa đơn'
        vnp.requestData['vnp_Locale'] = 'vn'
        vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
        vnp.requestData['vnp_IpAddr'] = ipaddr
        vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
        vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)        
        
        cart.clear()

        return redirect(vnpay_payment_url)

    return render(request, 'cart/checkout.html', {
        'cart': cart,
        'customer': customer
    })


def success(request):
    cart = Cart(request)
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = int(inputData['vnp_Amount']) / 100
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            if vnp_ResponseCode == "00":

                return render(request, "cart/result.html", {"title": "Kết quả thanh toán",
                                                               "result": "Thành công", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode,
                                                               "cart": cart})
            else:
                return render(request, "cart/result.html", {"title": "Kết quả thanh toán",
                                                               "result": "Lỗi", "order_id": order_id,
                                                               "amount": amount,
                                                               "order_desc": order_desc,
                                                               "vnp_TransactionNo": vnp_TransactionNo,
                                                               "vnp_ResponseCode": vnp_ResponseCode,
                                                               "cart": cart})
        else:
            return render(request, "cart/result.html",
                          {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id, "amount": amount,
                           "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
                           "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum",
                           "cart": cart})
    else:
        return render(request, "cart/result.html", {"title": "Kết quả thanh toán", "result": "", "cart": cart})
