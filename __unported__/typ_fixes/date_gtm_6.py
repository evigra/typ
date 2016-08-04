import time
from datetime import datetime,timedelta

def fecha_actual():
    date_facturae = time.strftime('%Y-%m-%d %H:%M:%S')
    date_facturae_srtp = datetime.strptime(date_facturae, '%Y-%m-%d %H:%M:%S')
    date_facturae_6 = date_facturae_srtp - timedelta(hours=6)
    date_facturae_6 = date_facturae_6.strftime('%Y-%m-%d %H:%M:%S')
    return date_facturae_6

def suma_dias_fecha(fecha, dias):
    #Fecha Especificada en formato %Y-%m-%d %H:%M:%S
    nueva_fecha = ""
    date_facturae_srtp = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')

    nueva_fecha = date_facturae_srtp + timedelta(days=dias)

    nueva_fecha = nueva_fecha.strftime('%Y-%m-%d %H:%M:%S')

    return nueva_fecha

def resta_dias_fecha(fecha, dias):
    #Fecha Especificada en formato %Y-%m-%d %H:%M:%S
    nueva_fecha = ""
    date_facturae_srtp = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')

    nueva_fecha = date_facturae_srtp - timedelta(days=dias)

    nueva_fecha = nueva_fecha.strftime('%Y-%m-%d %H:%M:%S')

    return nueva_fecha

def suma_horas_fecha(fecha, horas):
    #Fecha Especificada en formato %Y-%m-%d %H:%M:%S
    nueva_fecha = ""
    date_facturae_srtp = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')

    nueva_fecha = date_facturae_srtp + timedelta(hours=dias)

    nueva_fecha = nueva_fecha.strftime('%Y-%m-%d %H:%M:%S')

    return nueva_fecha

def resta_horas_fecha(fecha, horas):
    #Fecha Especificada en formato %Y-%m-%d %H:%M:%S
    nueva_fecha = ""
    date_facturae_srtp = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')

    nueva_fecha = date_facturae_srtp - timedelta(hours=dias)

    nueva_fecha = nueva_fecha.strftime('%Y-%m-%d %H:%M:%S')

    return nueva_fecha

def numero_semana_fecha(fecha):
    #Fecha Especificada en formato %Y-%m-%d %H:%M:%S
    nueva_fecha = ""
    date_strp = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
    year = date_strp.year
    year = year
    month = date_strp.month
    day = date_strp.day           
    weeknum = date(year, month, day).isocalendar()[1]
    nueva_fecha = weeknum
    return nueva_fecha

def consulta_elementos_fecha(fecha):
    elementos = {}
    date_strp = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
    year = date_strp.year
    year = year
    month = date_strp.month
    day = date_strp.day
    elementos.update({
        'dia': day,
        'mes': month,
        'year': year,
        }) 
    return elementos
    

# variable = manejo_fechas_mx()
# fecha_actual = variable.fecha_actual()
# suma_fecha = variable.suma_dias_fecha('2015-03-02 12:45:07',5)
# print variable
