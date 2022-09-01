from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Customer(models.Model):
    # one to one relationship means  that a user can have one customer and a customer can only have one user
    user = models.OneToOneField(User, null= True, on_delete=models.CASCADE, blank= True)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200, null= True)

    def __str__(self):
        return self.name
        # this is the value that is going to show up on our admin panel or when we create the model


class Product(models.Model):
    name = models.CharField(max_length=200, null= True)
    price = models.FloatField()
    digital = models.BooleanField(default= False, null=True, blank= True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url = ''
        return url


class Order(models.Model):
    # on_delete=models.SET_NULL means that when a customer gets deleted we dont want to delete the order we just want to set customer value to NULL
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add= True)
    # if complete is false,that is an open cart and we can continue adding to that cart
    complete = models.BooleanField(default= False,null= True, blank= False)
    transaction_id = models.CharField(max_length=100, null= True)

    def __str__(self):
        return str(self.id)
        # because id is an integer thus we change it into a string


    @property
    def shipping(self):
        shipping = False
        orderitems = self.orderitem_set.all()
        for i in orderitems:
            if i.product.digital == False:
                shipping = True
            return shipping


    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total


# order is our cart and our orderItem is the item within our cart
# cart can have multiple orderItem thus why we need this relationship
class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order,on_delete=models.SET_NULL,null=True,blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)


    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total



class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True,blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank= True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.address