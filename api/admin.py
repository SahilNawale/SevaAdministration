from django.contrib import admin
from .models import Buyer,Stock,Sale,PaymentAccount,Battery,Payment,Purchase

class saleAdmin(admin.ModelAdmin):
    search_fields = ['battery_name__battery_name','DC_no','serial_no','date','buyer__name']
    list_filter = ['battery_name','date','buyer']

class buyerAdmin(admin.ModelAdmin):
    search_fields = ['name','outstanding']
    list_filter = ['name','outstanding']

class stockAdmin(admin.ModelAdmin):
    search_fields = ['battery_name']
    list_filter = ['battery_name']
    
class paymentAdmin(admin.ModelAdmin):
    search_fields = ['payment_from__name','payment_to__name','date','payment_mode']
    list_filter = ['payment_from','payment_to','date','payment_mode']

class purchaseAdmin(admin.ModelAdmin):
    search_fields = ['battery_name__battery_name','date']
    list_filter = ['battery_name','date']



admin.site.register(Buyer,buyerAdmin)
admin.site.register(Stock,stockAdmin)
admin.site.register(Battery)
admin.site.register(Sale,saleAdmin)
admin.site.register(PaymentAccount)
admin.site.register(Payment,paymentAdmin)
admin.site.register(Purchase,purchaseAdmin)