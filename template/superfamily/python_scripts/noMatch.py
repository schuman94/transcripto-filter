import pandas as pd
import sys

def crear_dataframe_diferencia(csv_final_1, csv_final_2, csv_inicial, salida_csv):
    # Leer los dos archivos CSV finales, usando el encabezado por defecto ya que tienen encabezados
    df_final_1 = pd.read_csv(csv_final_1)
    df_final_2 = pd.read_csv(csv_final_2)
    # Combina y elimina duplicados para obtener una lista única de 'n' en los archivos finales
    n_finales = pd.concat([df_final_1['n'], df_final_2['n']], ignore_index=True).drop_duplicates()

    # Leer el archivo CSV inicial
    df_inicial = pd.read_csv(csv_inicial)

    # Encontrar las filas donde `n` está en los datos iniciales pero no en los datos finales
    df_diferencia = df_inicial[~df_inicial['n'].isin(n_finales)]

    # Ordenar las filas de forma ascendente en función de 'n'
    df_diferencia = df_diferencia.sort_values(by='n', ascending=True)

    # Guardar el nuevo DataFrame resultante en un archivo CSV, incluyendo los encabezados
    df_diferencia.to_csv(salida_csv, index=False)
    print(f'Archivo guardado: {salida_csv}')

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python script.py <csv_final_1> <csv_final_2> <csv_inicial> <salida_csv>")
        sys.exit(1)

    csv_final_1 = sys.argv[1]
    csv_final_2 = sys.argv[2]
    csv_inicial = sys.argv[3]
    salida_csv = sys.argv[4]

    crear_dataframe_diferencia(csv_final_1, csv_final_2, csv_inicial, salida_csv)
