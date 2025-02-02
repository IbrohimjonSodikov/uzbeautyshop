from django.contrib import admin
from django.urls import path, include
from products.views import ProductList, AboutPage, contact_us, admin_messages
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns  # Import to support language-specific URLs
from django.views.i18n import set_language

urlpatterns = [
    path(r'jet/', include('jet.urls', 'jet')),
    path(r'jet/dashboard/', include('jet.dashboard.urls', 'jet-dashboard')), 
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('i18n/setlang/', set_language, name='set_language'),
] + i18n_patterns(  # Wrap your paths with i18n_patterns to enable language-specific URLs
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),  # Product URLs are now language-specific
    path('blog/', include('articles.urls')),
    path('', ProductList.as_view(), name='home'),
    path('about/', AboutPage.as_view(), name='about'),
    path('contacts/', contact_us, name='contact'),
    path('admin/messages/', admin_messages, name='admin_messages'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
