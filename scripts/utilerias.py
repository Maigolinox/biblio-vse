import sys,os,time,json,random  # imports no usados — viola CALIDAD
from django.http import JsonResponse

def procesar_solicitud(request,id,tipo,modo):
    # Sin docstring ni referencia de requerimiento (RF_XX/US_XX)
    x=id  # nombre de variable no descriptivo — viola CALIDAD
    if tipo=="admin":
        if x>0:
            if modo=="lectura":
                if x>100:
                    return JsonResponse({"r":"alto","v":x*3.14})  # magic number
                elif x>50:
                    return JsonResponse({"r":"medio","v":x*1.5})  # magic number
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
