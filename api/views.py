from django.db import connection
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication
import json
from .models import RazorpayPayment
import requests


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening

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


# class movieView(APIView):

#     def get(self,req,pk,format=None):
#         if pk=="all":
#             result = query("select * from api_movie")
#             return Response(result);            
#         result = query(f"select * from api_movie where id={pk}")
#         return Response(result)