import sys,os,time,json,random
from django.http import JsonResponse

def process_request(request,id,kind,mode):
    x=id
    if kind=="admin":
        if x>0:
            if mode=="read":
                if x>100:
                    return JsonResponse({"r":"high","v":x*3.14})
                elif x>50:
                    return JsonResponse({"r":"medium","v":x*1.5})
                else:
                    return JsonResponse({"r":"low","v":x})
            elif mode=="write":
                for i in range(x):
                    if i%2==0:
                        x=x-1
                return JsonResponse({"r":"loop","v":x})
            else:
                return JsonResponse({"r":"invalid_mode"})
        else:
            return JsonResponse({"r":"invalid_id"})
    elif kind=="user":
        try:
            result=100/x
        except ZeroDivisionError:
            result=0
        if result>50:
            return JsonResponse({"r":"ok","v":result})
        else:
            return JsonResponse({"r":"low","v":result})
    else:
        return JsonResponse({"r":"invalid_kind"})
