"""simpleecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import os
from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from cms import views as cms_views
from products import views as prod_views
from orders import views as order_views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^$', cms_views.HomePage.as_view(), name='home_page'),
    url(r'^cake-compose/$', cms_views.CakeCompose.as_view(), name='cake_compose'),
    url(r'api/order/add/', order_views.CreateOrderView.as_view(), name='api_order_add'),
    url(r'^(?P<slug>[\w-]+),(?P<pk>[0-9]+)\.htm', prod_views.CategoryView.as_view(), name="category_view"),
    url(r'^(?P<category_path>[\w/-]+)/(?P<slug>[\w-]+),(?P<pk>[0-9]+)\.htm', prod_views.ProductView.as_view(), name="product_view"),
    url(r'^(?P<slug>[\w-]+),p(?P<pk>[0-9]+)\.htm', prod_views.ProductView.as_view(), name="product_view2"),

]
if settings.DEBUG:
    urlpatterns += [
        url(r'^upload/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': os.path.join(settings.BASE_DIR, 'upload'),
        }),
    ]
# this should be as the last pattern
urlpatterns += [
    url(r'', cms_views.StaticPageView.as_view(), name='static_page'),
]
