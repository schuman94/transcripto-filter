import pandas as pd
import sys
import os

def procesar_y_dividir(csv_path, original_csv_path, output_dir):
    # Asegurarse de que el directorio de salida existe
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Extraer el nombre base del archivo CSV original sin la extensión
    csv_base_name = os.path.splitext(os.path.basename(csv_path))[0]

    # Cargar el archivo CSV con los resultados BLAST, seleccionando solo las columnas de interés
    columnas = ['qseqid', 'sseqid', 'pident', 'length', 'evalue']
    df_blast = pd.read_csv(csv_path, usecols=[0, 1, 2, 3, 10], names=columnas)

    # Cargar el CSV original que contiene todos los IDs
    df_original = pd.read_csv(original_csv_path, usecols=[1], header=0)
    df_original.columns = ['qseqid']  # Renombrar la columna después de cargar el DataFrame


    # Ordenar por 'pident' de forma descendente y eliminar duplicados basándonos en 'qseqid', conservando el de mayor 'pident'
    df_unicos = df_blast.sort_values('pident', ascending=False).drop_duplicates('qseqid').copy()

    # Modificar la columna 'sseqid' para quedarnos solo con la parte después de "superfamily_"
    # y renombrar esa columna a 'superfamily'
    df_unicos['superfamily'] = df_unicos['sseqid'].apply(lambda x: x.split('superfamily_')[-1] if 'superfamily_' in x else x)
    # Eliminar la columna 'sseqid' original
    df_unicos.drop('sseqid', axis=1, inplace=True)

    # Dividir el DataFrame en dos: uno con 'pident' >= 70 y otro con 'pident' < 70
    df_SF = df_unicos[df_unicos['pident'] >= 70]
    df_NoSF = df_unicos[df_unicos['pident'] < 70]

    # Identificar IDs faltantes que están en df_original pero no en df_SF
    faltantes = df_original[~df_original['qseqid'].isin(df_SF['qseqid'])]

    # Preparar un DataFrame con estos IDs faltantes y columnas rellenadas según especificaciones
    df_faltantes = pd.DataFrame({
        'qseqid': faltantes['qseqid'],
        'superfamily': 'unknown',
        'pident': pd.NA,
        'length': pd.NA,
        'evalue': pd.NA
    })

    # Unir df_NoSF con df_faltantes
    df_NoSF_final = pd.concat([df_NoSF, df_faltantes], ignore_index=True)

    # Construir las rutas completas de los archivos de salida
    sf_path = os.path.join(output_dir, f"{csv_base_name}_SF.csv")
    nosf_path = os.path.join(output_dir, f"{csv_base_name}_NoSF.csv")

    # Guardar los DataFrames en archivos CSV
    df_SF.to_csv(sf_path, index=False)
    df_NoSF_final.to_csv(nosf_path, index=False)

    print(f"Procesamiento completo. Resultados guardados en '{sf_path}' y '{nosf_path}'.")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Uso: python script.py <archivo_resultados_blast.csv> <archivo_csv_original> <directorio_salida>")
        sys.exit(1)

    csv_path = sys.argv[1]
    original_csv_path = sys.argv[2]
    output_dir = sys.argv[3]
    procesar_y_dividir(csv_path, original_csv_path, output_dir)
