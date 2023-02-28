from django.shortcuts import render
from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework import viewsets
from store.models import Category, SubCategory, Product, Contact
from . forms import FormContact
from . serializers import ProductSerializer
from cart.cart import Cart
# from . models import Category, SubCategory, Product


def index(request):
    cart = Cart(request)
    # tbgd_subcategory = SubCategory.objects.filter(category=1)
    tbgd_subcategory = SubCategory.objects.filter(category__slug='thiet-bi-gia-dinh').values_list('slug')
    ddnb_subcategory = SubCategory.objects.filter(category__slug='do-dung-nha-bep').values_list('slug')
    
    tbgd_list_sub = []
    ddnb_list_sub = []

    for sub in tbgd_subcategory:
        tbgd_list_sub.append(sub[0])

    for sub in ddnb_subcategory:
        ddnb_list_sub.append(sub[0])

    tbgd_products = Product.objects.filter(subcategory__slug__in=tbgd_list_sub)
    ddnb_products = Product.objects.filter(subcategory__slug__in=ddnb_list_sub)

    return render(request, 'store/index.html', {
        'tbgd_products': tbgd_products,
        'ddnb_products': ddnb_products,
        'cart': cart
    })


def productlist(request, slug):
    cart = Cart(request)
    sub_cats = SubCategory.objects.all()

    if slug == 'tat-ca-san-pham':
        products = Product.objects.all()
        sub_name = 'Tất cả sản phẩm (' + str(len(products)) + ')'
    else:
        products = Product.objects.filter(subcategory__slug = slug)
        select_name = SubCategory.objects.get(slug=slug)
        sub_name = select_name.name + ' (' + str(len(products)) + ')'

    #lọc giá
    from_price=0
    to_price=0
    
    if request.GET.get('from_price'):
        from_price = int(request.GET.get('from_price'))
        to_price = int(request.GET.get('to_price'))
        products = [product for product in products if from_price <= product.price <= to_price] #list comprehension
        sub_name = f'Số sản phẩm có giá từ "{from_price}VND" đến "{to_price}VND" là: ' + '(' + str(len(products)) + ')'

    page = request.GET.get('page', 1)
    paginator = Paginator(products, 20)
    products_page = paginator.page(page)

    return render(request, 'store/product-list.html', {
        'slug': slug,
        'sub_cats': sub_cats,
        'products': products_page,
        'sub_name': sub_name,
        'from_price': from_price,
        'to_price': to_price,
        'cart': cart
    })


def productdetail(request, pk):
    cart = Cart(request)
    product = Product.objects.get(pk=pk)
    sub_category_id = Product.objects.filter(pk=pk).values_list("subcategory")
    same_products = Product.objects.filter(subcategory__in=sub_category_id).exclude(pk=pk)

    sub_cats = SubCategory.objects.all()
    all_products = Product.objects.all()

    return render(request, 'store/product-detail.html', {
        'product': product,
        'same_products': same_products,
        'sub_cats': sub_cats,
        'all_products': all_products,
        'cart': cart
    })


def search(request):
    cart = Cart(request)
    if request.GET.get('product_name'):
        sub_cats = SubCategory.objects.all()
        product_name = request.GET.get('product_name').strip()
        search_products = Product.objects.filter(name__contains=product_name)
        sub_name = f'Số sản phẩm có từ khóa "{product_name}": ' + '(' + str(len(search_products)) + ')'

    page = request.GET.get('page', 1)
    paginator = Paginator(search_products, 15)
    products_pager = paginator.page(page)

    return render(request, 'store/product-list.html', {
        'sub_cats': sub_cats,
        'products': products_pager,
        'sub_name': sub_name,
        'cart': cart
    })


def contact(request):
    form = FormContact()
    result = ''
    if request.POST.get('btnSend'):
        form = FormContact(request.POST, Contact)
        if form.is_valid():
            post = form.save(commit=False)
            post.name = form.cleaned_data['name']
            post.email = form.cleaned_data['email']
            post.subject = form.cleaned_data['subject']
            post.message = form.cleaned_data['message']
            post.save()

            result = '''
                <div class="alert alert-success" role="alert">
                    Submit Successfully!!!
                </div>
            '''

    return render(request, 'store/contact.html', {
        'form': form,
        'result': result
    })


def products_service(request):
    product = Product.objects.all()
    result_list = list(product.values('name', 'price', 'content', 'image'))

    return JsonResponse(result_list, safe=False)


def products_service_detail(request, pk):
    product = Product.objects.filter(pk=pk)
    result_list = list(product.values())[0]

    return JsonResponse(result_list, safe=False)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer