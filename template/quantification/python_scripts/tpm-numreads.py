import os
import pandas as pd
import argparse

# Argumentos del script
parser = argparse.ArgumentParser(description="Añadir TPM y NumReads a los CSVs")
parser.add_argument('--quant_file', required=True, help="Ruta del archivo quant.sf")
parser.add_argument('--results_dir', required=True, help="Carpeta donde se guardarán los CSV procesados")
parser.add_argument('--csv_dir', required=True, help="Carpeta donde están los CSV originales")

args = parser.parse_args()

# Cargar los valores de TPM y NumReads desde el archivo quant.sf
tpm_data = pd.read_csv(args.quant_file, sep='\t')

# Crear diccionarios que mapean los nombres de transcritos con TPM y NumReads
tpm_dict = dict(zip(tpm_data['Name'], tpm_data['TPM']))
numreads_dict = dict(zip(tpm_data['Name'], tpm_data['NumReads']))

# Función para extraer el ID de los transcritos antes del "_Frame"
def extract_id(full_id):
    return full_id.split('_Frame')[0]

# Procesar cada archivo CSV en la carpeta de resultados original
for csv_file in os.listdir(args.csv_dir):
    if csv_file.endswith(".csv"):
        # Cargar el CSV original
        csv_path = os.path.join(args.csv_dir, csv_file)
        df = pd.read_csv(csv_path)

        # Verificar que la columna "id" existe en el CSV
        if 'id' not in df.columns:
            print(f"Advertencia: El archivo {csv_file} no tiene una columna 'id'.")
            continue

        # Extraer los valores TPM y NumReads correspondientes para cada fila
        df['tpm'] = df['id'].apply(lambda x: tpm_dict.get(extract_id(x), 0))
        df['numreads'] = df['id'].apply(lambda x: numreads_dict.get(extract_id(x), 0))

        # Reorganizar las columnas para que 'tpm' y 'numreads' queden justo antes de 'secuencia'
        cols = df.columns.tolist()
        if 'secuencia' in cols:
            dest = cols.index('secuencia')  # posición de 'secuencia'
            # Inserta en orden: primero tpm, luego numreads, justo antes de 'secuencia'
            for col in ['tpm', 'numreads']:
                cols.insert(dest, cols.pop(cols.index(col)))
                dest += 1  # avanzar porque hemos insertado antes de 'secuencia'
            df = df[cols]


        # Guardar el CSV procesado en la carpeta de resultados
        result_csv_path = os.path.join(args.results_dir, csv_file)
        df.to_csv(result_csv_path, index=False)
        print(f"Procesado: {csv_file}")
