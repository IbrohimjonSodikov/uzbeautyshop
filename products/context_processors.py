# products/context_processors.py

from .models import Cart, Favorite

def cart_and_favorites_count(request):
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()
        favorite_count = Favorite.objects.filter(user=request.user).count()
    else:
        cart_count = 0
        favorite_count = 0

    return {
        'cart_count': cart_count,
        'favorite_count': favorite_count,
    }
