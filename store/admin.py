from django.contrib import admin
from .models import *

# Register your models here.
from .models import *


admin.site.register(Customer)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)

# registering this models enables you to see them in the admin panel