from django.urls import path,include
from .import views 


urlpatterns = [
    # leave as empty string for base url
    path('',views.store, name= "store"),
    path('cart/', views.cart, name= "cart"),
    path('checkout/', views.checkout, name="checkout"),

    path('update_item/', views.updateItem, name="update_item"),
    
    path('process_order/', views.processOrder, name="process_order"),
    # below is a url that comes with the paypal library and allows us to use automatically
    path('paypal/', include('paypal.standard.ipn.urls')),
]