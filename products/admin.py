from django.contrib import admin
from .models import Product, Category, Order, OrderItem
from .models import ContactMessage, Company

class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'date_created')
    list_filter = ('date_created',)
    search_fields = ('name', 'email', 'message')

admin.site.register(ContactMessage, ContactMessageAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'brand', 'original_price', 'price', 'created_at', 'is_hot_deal1', 'is_hot_deal2', 'is_hot_deal3')
    list_filter = ('country', 'brand')  # Filters to easily find products
    search_fields = ('name', 'brand')   # Search by product name or brand


# Custom admin action for changing the status of an order
def mark_as_shipped(modeladmin, request, queryset):
    queryset.update(status='Shipped')
mark_as_shipped.short_description = "Mark selected orders as Shipped"

def mark_as_delivered(modeladmin, request, queryset):
    queryset.update(status='Delivered')
mark_as_delivered.short_description = "Mark selected orders as Delivered"

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_price', 'status', 'created_at', 'address')  # Correct usage of 'status'
    list_filter = ('status', 'created_at')  # Correct usage of 'status'
    search_fields = ('customer__username', 'id')
    inlines = [OrderItemInline]
    actions = [mark_as_shipped, mark_as_delivered]


admin.site.register(Order, OrderAdmin)

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Company)
