import pandas as pd
import os
from tkinter import Tk, filedialog

def extraer_nombre_base(archivo):
    return os.path.splitext(os.path.basename(archivo))[0]

def csvs_a_xlsx(directorio):
    archivo_xlsx = os.path.join(directorio, 'resultados.xlsx')
    writer = pd.ExcelWriter(archivo_xlsx, engine='xlsxwriter')

    for archivo in os.listdir(directorio):
        if archivo.endswith(".csv"):
            ruta_completa = os.path.join(directorio, archivo)
            df = pd.read_csv(ruta_completa)
            nombre_hoja = extraer_nombre_base(archivo)
            df.to_excel(writer, sheet_name=nombre_hoja, index=False)

    writer.save()
    print(f'Archivo {archivo_xlsx} creado con éxito.')

def seleccionar_directorio():
    root = Tk()
    root.withdraw() # Ocultamos la ventana principal de Tkinter
    directorio = filedialog.askdirectory() # Abrimos el diálogo para seleccionar directorio
    return directorio

if __name__ == "__main__":
    directorio_csv = seleccionar_directorio()
    if directorio_csv:
        csvs_a_xlsx(directorio_csv)
    else:
        print("No se seleccionó ningún directorio.")
