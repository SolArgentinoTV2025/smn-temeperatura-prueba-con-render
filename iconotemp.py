import requests
import zipfile
import io
import time

# Configuración
URL_DESCARGA = 'https://ssl.smn.gob.ar/dpd/zipopendata.php?dato='
PARAM_TIEMPO = 'tiepre'
TEXT_ENCODING = 'latin-1'

# Función para descargar y procesar datos desde el archivo zip
def descargar_datos(param):
    r = requests.get(URL_DESCARGA + param)
    if r.status_code == 200:
        z = zipfile.ZipFile(io.BytesIO(r.content))
        nombre = z.namelist()[0]
        return list(io.TextIOWrapper(z.open(nombre), TEXT_ENCODING))
    else:
        raise Exception(f"Error al descargar datos: {r.status_code}")

# Función para convertir el estado del clima en emojis
def convertir_a_emoji(estado_clima):
    emojis_clima = {
        "Despejado": "☀️",
        "Ligeramente nublado": "🌤️",
        "Algo nublado": "⛅",
        "Parcialmente nublado": "⛅",
        "Mayormente nublado": "🌥️",
        "Nublado": "☁️",
        "Cubierto con llovizna en la hora anterior": "🌪️",
        "Cubierto": "🌫️",
        "Cubierto con llovizna": "🌦️",
        "Nublado con tormenta": "⛈️",
        "Nublado con tormenta en la hora anterior": "🌩️",
        "Nublado con lluvia en la hora anterior": "🌦️",
        "Nublado con lluvia": "🌧️",
        "Cubierto con lluvia": "🌨️",
        "Cubierto con lluvia en la hora anterior": "🌫️",
        "Lluvia": "🌧️",
        "Tormenta": "⛈️",
        "Tormentas eléctricas": "🌩️",
        "Llovizna": "🌦️",
        "Nieve": "❄️",
        "Granizo": "🌨️",
        "Neblina": "🌁",
        "Ventoso": "🌬️",
        "No disponible": "❓"
    }
    return emojis_clima.get(estado_clima, "❓")  # Predeterminado: Desconocido

# Función para extraer datos climáticos
def extraer_datos_climaticos():
    data = [renglon.lstrip().rstrip()[:-2].split(';') for renglon in descargar_datos(PARAM_TIEMPO)]
    tiempo = {}
    for linea in data:
        estacion = linea[0]
        
        # Procesar temperatura
        temperatura_str = linea[5]
        temperatura = round(float(temperatura_str), 1) if temperatura_str != '---' else None
        
        # Procesar sensación térmica
        sensacion_termica_str = linea[6]
        sensacion_termica = round(float(sensacion_termica_str), 1) if sensacion_termica_str != '---' and 'No se calcula' not in sensacion_termica_str else temperatura
        
        # Procesar humedad
        humedad_str = linea[7]
        humedad = int(humedad_str) if humedad_str != '---' and 'No se calcula' not in humedad_str else None
        
        # Procesar estado del clima (columna 3)
        estado_clima = linea[3] if len(linea) > 3 and linea[3] != '---' else "No disponible"
        estado_clima_emoji = convertir_a_emoji(estado_clima)
        
        # Procesar fecha y hora de la última actualización
        fecha_actualizacion = linea[1]
        hora_actualizacion = linea[2]
        ultima_actualizacion = f"{fecha_actualizacion} {hora_actualizacion}"
        
        tiempo[estacion] = {
            'temperatura': temperatura,
            'sensacion_termica': sensacion_termica,
            'humedad': humedad,
            'estado_clima': estado_clima,
            'estado_clima_emoji': estado_clima_emoji,
            'ultima_actualizacion': ultima_actualizacion
        }
    return tiempo

# Función para actualizar datos climáticos en archivos
def actualizar_datos_climaticos_en_archivos():
    while True:
        try:
            datos_climaticos = extraer_datos_climaticos()
            if 'Buenos Aires' in datos_climaticos:
                temperatura_actual = datos_climaticos['Buenos Aires']['temperatura']
                sensacion_termica_actual = datos_climaticos['Buenos Aires']['sensacion_termica']
                humedad_actual = datos_climaticos['Buenos Aires']['humedad']
                estado_clima_actual = datos_climaticos['Buenos Aires']['estado_clima']
                estado_clima_emoji = datos_climaticos['Buenos Aires']['estado_clima_emoji']
                ultima_actualizacion = datos_climaticos['Buenos Aires']['ultima_actualizacion']
                
                # Mostrar en la consola
                print(f' {temperatura_actual}° ')
                if sensacion_termica_actual is not None:
                    print(f' ST {sensacion_termica_actual}° ')
                else:
                    print(' ST No disponible ')
                
                if humedad_actual is not None:
                    print(f' H {humedad_actual}% ')
                else:
                    print(' H No disponible ')
                
                print(f' Clima: {estado_clima_actual} {estado_clima_emoji}')
                print(f' Última actualización: {ultima_actualizacion}')
                
                # Guardar en el archivo de temperatura
                with open('temperatura_actual_buenos_aires.txt', 'w', encoding='utf-8') as archivo_temperatura:
                    if temperatura_actual is not None:
                        archivo_temperatura.write(f' {temperatura_actual}° ')
                    else:
                        archivo_temperatura.write(' No disponible ')
                    
                # Guardar en el archivo de sensación térmica
                with open('sensacion_termica_buenos_aires.txt', 'w', encoding='utf-8') as archivo_sensacion_termica:
                    if sensacion_termica_actual is not None:
                        archivo_sensacion_termica.write(f' ST {sensacion_termica_actual}° ')
                    else:
                        archivo_sensacion_termica.write(' No disponible ')
                
                # Guardar en el archivo de humedad
                with open('humedad_buenos_aires.txt', 'w', encoding='utf-8') as archivo_humedad:
                    if humedad_actual is not None:
                        archivo_humedad.write(f' H {humedad_actual}% ')
                    else:
                        archivo_humedad.write(' No disponible ')
                
                # Guardar en el archivo de estado del clima con emoji
                with open('estado_clima_buenos_aires.txt', 'w', encoding='utf-8') as archivo_estado_clima:
                    archivo_estado_clima.write(f'{estado_clima_emoji}')
                
                # Guardar la última actualización
                with open('ultima_actualizacion_buenos_aires.txt', 'w', encoding='utf-8') as archivo_actualizacion:
                    archivo_actualizacion.write(f' Última actualización: {ultima_actualizacion}')
            
            # Espera 5 minutos antes de la próxima actualización
            time.sleep(300)
        
        except Exception as e:
            print(f"Error: {e}")
            # Evitar que el bucle se detenga por un error inesperado
            time.sleep(300)

# Punto de entrada
if __name__ == "__main__":
    actualizar_datos_climaticos_en_archivos()