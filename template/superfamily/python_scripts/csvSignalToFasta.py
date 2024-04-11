import pandas as pd
import sys
import os

def csv_a_fasta(csv_path, original_csv_path, fasta_output_dir):
    # Leer el archivo CSV generado previamente para obtener los IDs de secuencia
    df_ids = pd.read_csv(csv_path, usecols=[0])  # Asumiendo que el ID está en la primera columna

    # Leer el archivo CSV original para obtener las secuencias de aminoácidos
    df_original = pd.read_csv(original_csv_path, usecols=[1, 2], header=0)  # Asumiendo que el ID está en la segunda columna y la secuencia en la tercera

    # Filtrar df_original para quedarnos solo con las filas que tienen un ID presente en df_ids
    df_secuencias = df_original[df_original.iloc[:,0].isin(df_ids.iloc[:,0])]

    # Crear el archivo FASTA
    fasta_filename = os.path.basename(csv_path).replace('.csv', '.fasta')
    fasta_filepath = os.path.join(fasta_output_dir, fasta_filename)

    with open(fasta_filepath, 'w') as fasta_file:
        for index, row in df_secuencias.iterrows():
            fasta_file.write(f">{row.iloc[0]}\n{row.iloc[1]}\n")

    print(f"Archivo FASTA guardado en {fasta_filepath}")

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print("Uso: python script.py <archivo_csv_generado> <archivo_csv_original> <ruta_salida_fasta>")
        sys.exit(1)

    csv_path = sys.argv[1]
    original_csv_path = sys.argv[2]
    fasta_output_dir = sys.argv[3]
    csv_a_fasta(csv_path, original_csv_path, fasta_output_dir)
