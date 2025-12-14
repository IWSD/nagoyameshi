"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from mysite import views
from django.conf import settings
from django.conf.urls.static import static
from mysite.views import CreateCheckoutSessionView, stripe_webhook, cancel_subscription,ShopUpdateView, MyShopListView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.TopView.as_view(), name = "top"),
    path('login/', views.LoginView.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name="logout"),
    path('shop/<int:pk>/', views.ShopDetailView.as_view(), name="shop_detail"),
    path("<int:pk>/edit/", ShopUpdateView.as_view(), name="shop_edit"),
    path("mine/", MyShopListView.as_view(), name="my_shops"),
    path('shop/<int:pk>/review/', views.ReviewCreateView.as_view(), name='review_create'),
    path('shop/<int:pk>/reserve/', views.ReservationInitialView.as_view(), name='reservation_initial'),
    # path("edit/<int:shop_id>/", edit_shop, name="edit_shop"),
    path('reservation/success/<int:reservation_id>/', views.ReservationSuccessView.as_view(), name='reservation_success'),
    path("mypage/", views.MyPageView.as_view(), name="mypage"),
    path("create-checkout-session/", views.CreateCheckoutSessionView.as_view(), name="create_checkout_session"),
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
    path("payment/success/", views.payment_success, name="payment_success"),
    path("payment/cancel/", views.payment_cancel, name="payment_cancel"),
    path('subscription/cancel/', cancel_subscription, name='cancel_subscription'),
    path('accounts/', include('accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)