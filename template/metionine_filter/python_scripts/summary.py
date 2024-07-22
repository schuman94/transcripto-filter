import os

# Ruta de la carpeta de resultados
resultados_path = "../resultados/"

# Nombres de los directorios y cómo se referirá a ellos
directorios = {
    "Alineamientos_Perfectos": "Perfectos",
    "Alineamientos_M_previa": "Metionina previa",
    "Alineamientos_Multiframe": "Multiframe",
    "Alineamientos_Revision_Manual": "Revision manual"
}

# Función para contar archivos en un directorio
def contar_archivos(directorio):
    return len([nombre for nombre in os.listdir(directorio) if os.path.isfile(os.path.join(directorio, nombre))])

# Contando archivos en cada directorio y preparando las líneas para el archivo de texto
lineas = []
for dir_name, ref_name in directorios.items():
    path_completo = os.path.join(resultados_path, dir_name)
    conteo = contar_archivos(path_completo)
    lineas.append(f"{ref_name}: {conteo}")

# Ordenando las líneas en el orden especificado
orden = ["Perfectos", "Metionina previa", "Multiframe", "Revision manual"]
lineas_ordenadas = sorted(lineas, key=lambda x: orden.index(x.split(":")[0]))

# Escribiendo los resultados en un archivo de texto
with open(os.path.join(resultados_path, "summary.txt"), "w") as archivo:
    for linea in lineas_ordenadas:
        archivo.write(linea + "\n")
