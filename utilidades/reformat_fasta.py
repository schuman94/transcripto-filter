import os
import sys
from Bio import SeqIO

def reformat_fasta(input_directory, output_directory):
    # Crear el directorio de salida si no existe
    if not os.path.exists(output_directory):
        print(f"El directorio {output_directory} no existe. Creándolo...")
        os.makedirs(output_directory)
    else:
        print(f"El directorio {output_directory} ya existe.")

    # Iterar sobre todos los archivos en el directorio de entrada
    for filename in os.listdir(input_directory):
        if filename.endswith(".fasta"):
            print(f"Procesando archivo: {filename}")

            # Crear el path completo al archivo de entrada y al archivo de salida
            input_filepath = os.path.join(input_directory, filename)
            output_filepath = os.path.join(output_directory, filename)

            # Leer las secuencias del archivo de entrada y escribirlas en el archivo de salida
            with open(input_filepath, "r") as input_file, open(output_filepath, "w") as output_file:
                for record in SeqIO.parse(input_file, "fasta"):
                    sequence_upper = str(record.seq).upper()  # Convertir la secuencia a mayúsculas
                    output_file.write(f">{record.id}\n")
                    output_file.write(sequence_upper + "\n")

            print(f"{filename} ha sido procesado y guardado en {output_directory}.")

        else:
            print(f"El archivo {filename} no es un archivo .fasta, saltándolo...")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python reformat_fasta.py /path/to/input_directory /path/to/output_directory")
        sys.exit(1)

    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    reformat_fasta(input_dir, output_dir)
