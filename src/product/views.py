from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.db.models import Avg
from django.shortcuts import render, get_object_or_404, redirect
from .forms import DeleteProductForm, FlagReviewForm, ProductForm, ReviewForm, UserForm
from .models import Product, Review
from vaderSentiment.vaderSentiment import sentiment as vaderSentiment

def admin(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        form = DeleteProductForm
        products = Product.objects.all()
        context = {
                'products': products,
                'message': 'none',
                'form': form
            }
        return render(request, 'admin.html', context)

def add_product(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        form = ProductForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            products = Product.objects.all()
            messages.success(request, 'Product added successfully')
            context = {
                'products': products,
            }
          
            return redirect(reverse('admin'), context=context)

        else:
            context = {
                'form': form
            }

            return render(request, 'add_product.html', context)

def create_review(request, product_id):
    form = ReviewForm(request.POST or None, request.FILES or None)
    product = get_object_or_404(Product, pk=product_id)
    product.average_score = product.review_set.aggregate(Avg('score')).get('score__avg', 0.00)
    if product.average_score != None:
        product.average_score = round(product.average_score, 1)
    if form.is_valid():
        review = form.save(commit=False)
        review.product = product
        review.review_text = form.cleaned_data['review_text']
        review.user = request.user
        s = vaderSentiment(review.review_text)
        if s['compound'] < 0:
            review.score = 5 - ((s['compound'] * -1) * 5)
        elif s['compound'] > 0:
            review.score = 5 + (s['compound'] * 5)
        else:
            review.score = 0

        review.save()
        product.average_score = product.review_set.aggregate(Avg('score')).get('score__avg', 0.00)
        if product.average_score != None:
            product.average_score = round(product.average_score, 1)
            product.save()

        context={
            'product': product
        }

        return redirect(reverse('detail', kwargs={'product_id': product_id}), context=context)

    context = {
        'product': product,
        'form': form,
    }
    return render(request, 'create_review.html', context)

def delete_product(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        product_id = (str(request.POST.get('product_id')))
        product = get_object_or_404(Product, pk=product_id)

        if request.method == 'POST':
            form = DeleteProductForm(request.POST)

            if form.is_valid():
                product.delete()

        else:
            form = DeleteProductForm()

        products = Product.objects.all()
        messages.success(request, 'Product removed successfully')
        context = {
                'products': products,
                'form': form,
            }
          
        return redirect(reverse('admin'), context=context)

def detail(request, product_id):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        user = request.user
        product = get_object_or_404(Product, pk=product_id)

        return render(request, 'detail.html', {'product': product, 'user': user})

def edit_product(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        product_id = (str(request.GET.get('product_id')))
        product = get_object_or_404(Product, pk=product_id)
        form = ProductForm(request.POST or None, request.FILES or None, instance=product)

        if form.is_valid():
            product = form.save(commit=False)
            product.save()
            products = Product.objects.all()
            messages.success(request, 'Product edited successfully')
            context = {
                'products': products,
            }
          
            return redirect(reverse('admin'), context=context)

        else:
            context = {
                'form': form
            }

            return render(request, 'edit_product.html', context)

def flag_review(request, product_id):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        user = request.user
        product = get_object_or_404(Product, pk=product_id)
        review_id = (str(request.POST.get('review_id')))
        review = get_object_or_404(Review, pk=review_id)

        if request.method == 'POST':
            form = FlagReviewForm(request.POST)

            if form.is_valid():
                review.flag = True
                review.save()

        else:
            form = FlagReviewForm()
                
        context = {
            'product': product,
            'user': user
        }

        return redirect(reverse('detail', kwargs={'product_id': product_id}), context=context)

def index(request):
    if not request.user.is_authenticated():
        return render(request, 'login.html')
    else:
        products = Product.objects.all()
        return render(request, 'index.html', {'products': products})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                products = Product.objects.all()
                return render(request, 'index.html', {'products': products})
            else:
                return render(request, 'login.html', {'error_message': 'Your account has been disabled'})
        else:
            return render(request, 'login.html', {'error_message': 'Invalid login'})
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    form = UserForm(request.POST or None)
    context = {
        "form": form,
    }
    return render(request, 'login.html', context)

def register(request):
    form = UserForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                products = Product.objects.all()
                return render(request, 'index.html', {'products': products})
    context = {
        "form": form,
    }
    return render(request, 'register.html', context)