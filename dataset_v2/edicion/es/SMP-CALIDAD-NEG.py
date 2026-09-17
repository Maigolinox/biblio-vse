import sys,os,time,json,random
from django.http import JsonResponse

def procesar_solicitud(request,id,tipo,modo):
    x=id
    if tipo=="admin":
        if x>0:
            if modo=="lectura":
                if x>100:
                    return JsonResponse({"r":"alto","v":x*3.14})
                elif x>50:
                    return JsonResponse({"r":"medio","v":x*1.5})
                else:
                    return JsonResponse({"r":"bajo","v":x})
            elif modo=="escritura":
                for i in range(x):
                    if i%2==0:
                        x=x-1
                return JsonResponse({"r":"loop","v":x})
            else:
                return JsonResponse({"r":"modo_inv"})
        else:
            return JsonResponse({"r":"id_inv"})
    elif tipo=="usuario":
        try:
            resultado=100/x
        except ZeroDivisionError:
            resultado=0
        if resultado>50:
            return JsonResponse({"r":"ok","v":resultado})
        else:
            return JsonResponse({"r":"bajo","v":resultado})
    else:
        return JsonResponse({"r":"tipo_inv"})
