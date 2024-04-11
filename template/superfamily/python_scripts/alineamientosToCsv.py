import os
import csv
from Bio import SeqIO

def extract_sequences_to_csv(directory_path, output_csv_path, inicio_metionina=False):
    """
    Extrae la primera secuencia de cada archivo fasta en el directorio especificado,
    eliminando los guiones de las secuencias. Si inicio_metionina es True, las secuencias
    comenzarán desde la primera metionina encontrada.

    :param directory_path: Ruta al directorio que contiene los archivos fasta.
    :param output_csv_path: Ruta al archivo CSV de salida.
    :param inicio_metionina: Booleano que indica si las secuencias deben comenzar desde la primera metionina.
    """
    rows = []  # Lista para almacenar las filas que luego serán ordenadas y escritas en el CSV

    for filename in os.listdir(directory_path):
        if filename.endswith(".mafft.fasta"):
            number = int(filename.split('_')[1].split('.')[0])  # Convertir el número a entero para el ordenamiento
            filepath = os.path.join(directory_path, filename)

            with open(filepath, 'r') as fasta_file:
                for record in SeqIO.parse(fasta_file, 'fasta'):
                    sequence = str(record.seq).replace('-', '')
                    if inicio_metionina:
                        m_index = sequence.find('M')
                        if m_index != -1:
                            sequence = sequence[m_index:]
                        else:
                            print(f"Advertencia: No se encontró 'M' en la secuencia de {filename}.")
                    rows.append([number, record.id, sequence])  # Añadir fila a la lista
                    break  # Solo procesar la primera secuencia

    # Ordenar las filas por el número (primera columna) en orden ascendente
    rows.sort(key=lambda x: x[0])

    # Escribir las filas ordenadas en el archivo CSV
    with open(output_csv_path, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['n', 'id', 'secuencia'])  # Escribir encabezados
        for row in rows:
            csvwriter.writerow(row)

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 4:
        print("Uso: python script.py <ruta_directorio> <archivo_salida.csv> <inicio_metionina>")
    else:
        directory_path = sys.argv[1]
        output_csv_path = sys.argv[2]
        inicio_metionina = sys.argv[3].lower() in ['true', '1', 't', 'y', 'yes']
        extract_sequences_to_csv(directory_path, output_csv_path, inicio_metionina)
