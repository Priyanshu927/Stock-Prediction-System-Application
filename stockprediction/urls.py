from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from predictor import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', views.index, name='index'),
    path('predict/<str:ticker>/<int:days>/', views.predict, name='predict'),
    path('predict/', views.predict, name='predict'),
    path('get_live_price/', views.get_live_price, name='get_live_price'),
    path('ticker/', views.ticker_info, name='ticker_info'),
    path('register/', views.register, name='register'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
