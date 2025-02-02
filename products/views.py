from django.shortcuts import render
from django.views.generic import ListView, TemplateView, DetailView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Product, Cart, Favorite, Category, Order, OrderItem, ContactMessage, Company
from django.contrib import messages
from django.db.models import Q
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import translation
from django.utils.decorators import method_decorator
from .forms import ReviewForm, ContactForm
from django.db.models import Avg
from django.contrib.auth.decorators import user_passes_test
from django.utils.translation import gettext as _
from random import sample
from django.urls import reverse

@user_passes_test(lambda u: u.is_superuser)
def admin_messages(request):
    messages = ContactMessage.objects.all().order_by('-date_created')
    return render(request, 'admin_messages.html', {'messages': messages})

class AboutPage(TemplateView):
    template_name = 'about.html'

def contact_us(request):
    success_message = None

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the message to the database
            ContactMessage.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                message=form.cleaned_data['message']
            )
            # Set success message to be displayed on the same page
            success_message = _("Thank you for your message! We'll get back to you shortly.")
        else:
            # In case of form errors, retain the form data (fields will show validation errors)
            success_message = None
    else:
        form = ContactForm()

    return render(request, 'contactus.html', {'form': form, 'success_message': success_message})



class ProductList(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        # Default order for products in the main section
        return Product.objects.all().order_by('created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # User's language

        # "On Sale" products (reversed order by creation date)
        context['on_sale_products'] = Product.objects.all().order_by('-created_at')

        # Top products (single product for each top category)
        context['is_hot_deal1'] = Product.objects.filter(is_hot_deal1=True).first()
        context['is_hot_deal2'] = Product.objects.filter(is_hot_deal2=True).first()
        context['is_hot_deal3'] = Product.objects.filter(is_hot_deal3=True).first()

        # Fetch 6 random products for "Best Sellers" section
        random_products = Product.objects.order_by('?')[:6]
        context['random_products_1'] = random_products[:3]
        context['random_products_2'] = random_products[3:6]

        # German Products Section
        context['german_products'] = Product.objects.filter(country='Germany')
        context['french_products'] = Product.objects.filter(country='France')
        context['italian_products'] = Product.objects.filter(country='Italy')

        return context

def country_products(request, country_name):
    # Get all categories
    all_categories = Category.objects.all()
    
    # Get selected category from query parameters
    selected_category = request.GET.get('category')  # Single category selection
    
    # Filter products by country
    products = Product.objects.filter(country=country_name)
    user_language = request.LANGUAGE_CODE
    # Apply category filter if a category is selected
    if selected_category:
        products = products.filter(categories__name=selected_category)
    
    return render(request, 'country_products.html', {
        'products': products,
        'selected_country': country_name,
        'categories': all_categories,
        'user_language': user_language,
        'selected_category': selected_category,  # For highlighting the selected category
    })


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product_detail.html'

    def get(self, request, *args, **kwargs):
        # Fetch the product and the user's language
        product = self.get_object()

        # Select the appropriate description based on the user's language
        user_language = translation.get_language()
        if user_language == 'ru':
            description = product.productdescription_ru
        elif user_language == 'uz':
            description = product.productdescription_uz
        else:
            description = product.description  # Default to the original description

        # Fetch reviews and calculate the average rating
        reviews = product.reviews.all().order_by('-created_at')
        average_rating = product.reviews.aggregate(Avg('rating'))['rating__avg'] or 0

        # Initialize the form for submitting a review
        form = ReviewForm()

        # Get random products for recommendations (excluding the current product)
        recommended_products = Product.objects.exclude(id=product.id).order_by('?')[:6]

        return render(request, self.template_name, {
            'product': product,
            'description': description,
            'reviews': reviews,
            'form': form,
            'average_rating': average_rating,
            'recommended_products': recommended_products,  # Ensure recommendations are passed
        })




    @method_decorator(login_required)  # Ensure only authenticated users can submit reviews
    def post(self, request, *args, **kwargs):
        product = self.get_object()
        form = ReviewForm(request.POST)

        if form.is_valid():
            # Save the review and associate it with the product and user
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', pk=product.pk)  # Redirect back to the product detail page

        # If the form is invalid, reload the page with the existing context
        user_language = translation.get_language()
        description = product.productdescription_ru if user_language == 'ru' else (
            product.productdescription_uz if user_language == 'uz' else product.description
        )
        reviews = product.reviews.all().order_by('-created_at')
        return render(request, self.template_name, {
            'product': product,
            'description': description,
            'reviews': reviews,
            'form': form,
        })


def AllProductsList(request):
    # Fetch all categories
    all_categories = Category.objects.all()
    
    # Get selected categories from the query parameters
    selected_categories = request.GET.getlist('categories')  # List of selected category names
    
    # Fetch all products or filter them by selected categories
    if selected_categories:
        # Filter products by categories (assumes many-to-many relationship)
        products = Product.objects.filter(categories__name__in=selected_categories).distinct()
    else:
        # No category filter applied, show all products
        products = Product.objects.all()
    
    # Get the current language for the user (for the template)
    user_language = request.LANGUAGE_CODE  # Ensure 'django.middleware.locale.LocaleMiddleware' is enabled
    
    # Render the template with context
    return render(request, "allproducts.html", {
        "products": products,
        "categories": all_categories,
        "user_language": user_language,
        "selected_categories": selected_categories,  # For highlighting selected categories in the template
    })


@login_required
def add_to_cart(request, product_id):
    # Retrieve the product, or 404 if not found
    product = get_object_or_404(Product, id=product_id)
    
    # Try to get or create a Cart item for the current user and the selected product
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        # If the cart item already exists, increase the quantity
        cart_item.quantity += 1
        cart_item.save()

    # Add a success message that the product was added to the cart
    messages.success(request, _('Product added to your cart! Go to your cart to order'))

    # Redirect the user to the product detail page (use 'pk' instead of 'product_id')
    return redirect(reverse('product_detail', kwargs={'pk': product.id}))



@login_required
def add_to_favorites(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    Favorite.objects.get_or_create(user=request.user, product=product)
    
    # Add a success message
    messages.success(request, _('Product added to your favorites!'))

    # Stay on the same page
    return redirect(reverse('product_detail', kwargs={'pk': product.id}))


@login_required
def favorites_view(request):
    # Fetch all favorite items for the current logged-in user
    favorite_items = Favorite.objects.filter(user=request.user)
    return render(request, 'favorites.html', {'favorite_items': favorite_items})

@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)  # Make sure this line is properly indented
    cart_items_with_total = [
        {
            'item': item,
            'total_price': item.product.price * item.quantity
        }
        for item in cart_items
    ]
    total_price = sum(item['total_price'] for item in cart_items_with_total)  # Make sure this is also aligned properly
    return render(request, 'cart.html', {'cart_items_with_total': cart_items_with_total, 'total_price': total_price})

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    
    if cart_item.quantity > 1:
        # Decrease the quantity by 1
        cart_item.quantity -= 1
        cart_item.save()
    else:
        # If the quantity is 1, delete the cart item
        cart_item.delete()
        
    return redirect('cart_view')  # Redirect to the updated cart view
@login_required
def remove_from_favorites(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Find the favorite item for the current user and product
    favorite = Favorite.objects.filter(user=request.user, product=product).first()
    
    if favorite:
        # Delete the favorite item
        favorite.delete()
    
    # Redirect back to the favorites page
    return redirect('favorites')

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)  # Get all items in the user's cart
    total_price = sum(item.product.price * item.quantity for item in cart_items)  # Calculate the total price

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }

    return render(request, 'checkout.html', context)


def search_view(request):
    query = request.GET.get('q', '')
    results = []
    user_language = request.LANGUAGE_CODE

    if query:
        results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)  # Extend as needed
        )
    return render(request, 'search_results.html', {'query': query, 'results': results, "user_language": user_language})


  # Import your relevant models

def process_checkout(request):
    # Ensure cart is passed to the template for rendering
    cart_items = Cart.objects.filter(user=request.user)

    if request.method == 'POST':
        # Get form data
        fullname = request.POST.get('firstname')
        email = request.POST.get('email')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        specifications = request.POST.get('specifications')

        # Check if the cart is empty
        if not cart_items.exists():
            messages.error(request, _('Your cart is empty. Please add something first!'))
            return redirect('cart_view')  # Redirect to cart page if empty

        # Calculate total price
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # Save order details
        order = Order.objects.create(
            customer=request.user,
            fullname=fullname,
            email=email,
            address=address,
            phone_number=phone_number,
            specifications=specifications,
            total_price=total_price,
        )

        # Process cart items and associate them with the order
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # Clear the cart after placing the order
        cart_items.delete()

        # Success message
        messages.success(request, _('Your order has been successfully placed!'))

        # Redirect to home page or order confirmation page
        return redirect('home')

    # Calculate total price when loading the page
    total_price = sum(item.product.price * item.quantity for item in cart_items)

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })




@staff_member_required
def admin_orders_view(request):
    orders = Order.objects.all().order_by('-created_at')
    # Collect product names for each order
    order_data = []
    for order in orders:
        products = [item.name for item in order.items.all()]  # Get product names
        order_data.append({
            'order': order,
            'products': ', '.join(products),  # Join the product names with commas
        })
    return render(request, 'admin_orders.html', {'order_data': order_data})

def order_history(request):
    # Retrieve the orders for the logged-in user
    orders = Order.objects.filter(customer=request.user)

    # Pass orders to the template
    return render(request, 'order_history.html', {'order_data': orders})

def change_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status:
            order.status = new_status
            order.save()
            # Add a success message or redirect
            messages.success(request, f"Order {order.id} status changed to {new_status}.")
    return redirect('admin_orders')
def admin_order_edit(request, id):
    order = get_object_or_404(Order, id=id)
    
    if request.method == 'POST':
        # Handle form submission to update the order
        order.status = request.POST.get('status')
        order.save()
        return redirect('admin_orders')  # Redirect back to the order list
    
    return render(request, 'order_edit.html', {'order': order})

def admin_order_delete(request, id):
    order = get_object_or_404(Order, id=id)

    if request.method == 'POST':
        order.delete()
        return redirect('admin_orders')  # Redirect back to the order list
    
    return render(request, 'order_delete_confirmation.html', {'order': order})

def admin_order_delete(request, order_id):
    # Fetch the order by ID
    order = get_object_or_404(Order, id=order_id)

    # Delete related OrderItems first
    order_items = OrderItem.objects.filter(order=order)
    order_items.delete()  # This will delete all related order items

    # Then delete the order itself
    order.delete()

    # Show a success message
    messages.success(request, "Order deleted successfully.")
    
    # Redirect to the order list page
    return redirect('admin_orders')


def brand_products(request, company_id):
    all_categories = Category.objects.all()
    
    # Get selected categories from the query parameters
    selected_categories = request.GET.getlist('categories')  # List of selected category names
    company = get_object_or_404(Company, id=company_id)  # Get the company by ID or return a 404 error

    # Fetch all products or filter them by selected categories
    if selected_categories:
        # Filter products by categories (assumes many-to-many relationship)
        products = Product.objects.filter(categories__name__in=selected_categories, brand=company).distinct()
    else:
        # No category filter applied, show all products
        products = Product.objects.filter(brand=company)
    
    # Get the current language for the user (for the template)
    user_language = request.LANGUAGE_CODE  # Ensure 'django.middleware.locale.LocaleMiddleware' is enabled

    # Render the template with context
    return render(request, "brand_products.html", {
        'company': company,
        "products": products,
        "categories": all_categories,
        "user_language": user_language,
        "selected_categories": selected_categories,  # For highlighting selected categories in the template
    })

