from django.db import models
from django.db import connection


def query(q):
    with connection.cursor() as c:
        c.execute(q)
        if q[0:6].lower()=="select":
            return dictfetchall(c)
        else :
            return "success"

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

PAYMENT_MODE = (
    ("ONLINE", "Online"),
    ("CASH", "Cash"),
)
class Stock(models.Model):
    battery_name = models.CharField(max_length=100,primary_key=True)
    qty = models.IntegerField(default=0)
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.battery_name)

class Battery(models.Model):
    serial_no = models.CharField(max_length=100)
    name = models.ForeignKey(Stock,on_delete=models.CASCADE)
    # date = models.DateField()

    def __str__(self) -> str:
        return str(self.serial_no)

class Buyer(models.Model):
    name = models.CharField(max_length=100,primary_key=True)
    outstanding = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.name

class PaymentAccount(models.Model):
    name = models.CharField(max_length=100,primary_key=True)
    balance = models.IntegerField(default=0)

    def __str__(self) -> str:
        return self.name

class Sale(models.Model):
    buyer = models.ForeignKey(Buyer,on_delete=models.CASCADE)
    battery_name = models.ForeignKey(Stock,on_delete=models.CASCADE)
    DC_no = models.CharField(max_length=1000)
    qty = models.IntegerField(default=0)
    serial_no = models.CharField(max_length=1000)
    details = models.TextField(null=True,blank=True)
    date = models.DateField()
    price = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.buyer) + " : " + str(self.date)
    
    def save(self, *args, **kwargs):

        predata = query(f"select * from api_sale where id='{self.id}' ")
        print(predata)
        
        if len(predata)>0:
            
            predata = predata[0]
            # add stock
            query(f"update api_stock set qty=qty+{predata['qty']} where battery_name='{predata['battery_name_id']}' ")

            # update outstanding
            query(f"update api_buyer set outstanding = outstanding - {predata['price']*predata['qty']} where name='{predata['buyer_id']}' ")
        
        #reduce stock
        prestock = query(f"select * from api_stock where battery_name='{self.battery_name}' ")[0]['qty']
        print(prestock)
        
        if prestock < self.qty :
            raise Exception("Not Enough Stock")

        query(f"update api_stock set qty=qty-{self.qty} where battery_name='{self.battery_name}'")

        # update outstanding
        query(f"update api_buyer set outstanding = outstanding + {self.price*self.qty} where name='{self.buyer}' ")        

        super().save(*args, **kwargs)   

    def delete(self,*args,**kwargs):

        predata = query(f"select * from api_sale where id='{self.id}' ")[0]

        # add stock
        query(f"update api_stock set qty=qty+{predata['qty']} where battery_name='{predata['battery_name_id']}' ")

        # update outstanding
        query(f"update api_buyer set outstanding = outstanding - {predata['price']*predata['qty']} where name='{predata['buyer_id']}' ")

        super().delete(*args, **kwargs)   

    
class Payment(models.Model):
    payment_from = models.ForeignKey(Buyer,on_delete=models.CASCADE)
    payment_to = models.ForeignKey(PaymentAccount,on_delete=models.CASCADE)
    date = models.DateField()
    amount = models.IntegerField(default=0)
    payment_mode = models.CharField(max_length=100,choices=PAYMENT_MODE,default="CASH")

    def __str__(self) -> str:
        return str(self.payment_from) + ' -> ' + str(self.payment_to) + ' Rs.' + str(self.amount)

    def save(self,*args,**kwargs):
        
        predata = query(f"select * from api_payment where id='{self.id}' ")
        if len(predata)>0:

            predata = predata[0]

            # update outstanding
            query(f"update api_buyer set outstanding = outstanding + {predata['amount']} where name='{predata['payment_from_id']}' ")

            # update balance 
            query(f"update api_paymentaccount set balance = balance - {predata['amount']} where name = '{predata['payment_to_id']}' ")   
        
        #update outstanding
        query(f"update api_buyer set outstanding = outstanding - {self.amount} where name='{self.payment_from}' ")

        # update balance 
        query(f"update api_paymentaccount set balance = balance + {self.amount} where name='{self.payment_to}' ")

        super().save(*args, **kwargs)   

    def delete(self,*args,**kwargs):

        predata = query(f"select * from api_payment where id='{self.id}' ")[0]

        # update outstanding
        query(f"update api_buyer set outstanding = outstanding + {predata['amount']} where name='{predata['payment_from_id']}' ")

        # update balance 
        query(f"update api_paymentaccount set balance = balance - {predata['amount']} where name = '{predata['payment_to_id']}' ")

        super().delete(*args, **kwargs)

class Purchase(models.Model):

    battery_name = models.ForeignKey(Stock,on_delete=models.CASCADE)
    qty = models.IntegerField(default=0)
    date = models.DateField()

    def __str__(self) -> str:
        return str(self.battery_name) + "   x" + str(self.qty)
    
    def save(self,*args,**kwargs):

        predata = query(f"select * from api_purchase where id='{self.id}' ")
        if len(predata)>0 :
            predata = predata[0]

            query(f"update api_stock set qty=qty-{predata['qty']} where battery_name='{predata['battery_name_id']}' ")
        
        query(f"update api_stock set qty=qty+{self.qty} where battery_name='{self.battery_name}' ")

        super().save(*args,**kwargs)
        
    def delete(self,*args,**kwargs):

        predata = query(f"select * from api_purchase where id='{self.id}' ")[0]

        query(f"update api_stock set qty=qty-{predata['qty']} where battery_name='{predata['battery_name_id']}' ")

        super().delete(*args,**kwargs)