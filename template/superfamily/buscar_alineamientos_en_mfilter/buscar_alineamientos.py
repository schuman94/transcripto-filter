import os
import csv
import argparse
from Bio import SeqIO

def parse_arguments():
    parser = argparse.ArgumentParser(description="Procesar un archivo CSV y generar su archivo FASTA correspondiente.")
    parser.add_argument("--csv", required=True, help="Ruta al archivo CSV de entrada.")
    parser.add_argument("--fasta_base_dir", required=True, help="Ruta base que contiene los subdirectorios con los archivos FASTA.")
    parser.add_argument("--output_dir", required=True, help="Ruta al directorio donde se guardarán los resultados.")
    parser.add_argument("--max_sequences", type=int, default=8, help="Número máximo de secuencias a incluir por archivo FASTA (por defecto: 8).")
    return parser.parse_args()

def find_matching_subdirectory(csv_name, fasta_base_dir):
    # Determinar la cadena clave en el nombre del CSV
    keywords = ["previa", "multiframe", "perfectos", "revision_manual"]
    for keyword in keywords:
        if keyword.lower() in csv_name.lower():
            # Buscar un subdirectorio que coincida con la clave
            for subdir in os.listdir(fasta_base_dir):
                if keyword.lower() in subdir.lower():
                    return os.path.join(fasta_base_dir, subdir)
    return None

def process_csv_and_fasta(output_file, csv_file, fasta_dir, max_sequences):
    with open(csv_file, "r") as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Saltar encabezado

        with open(output_file, "w") as outfile:
            for row in reader:
                number = int(row[0])  # Leer el número de la primera columna
                fasta_filename = os.path.join(fasta_dir, f"seq_{number}.mafft.fasta")

                if os.path.exists(fasta_filename):
                    # Leer secuencias del archivo FASTA
                    sequences = list(SeqIO.parse(fasta_filename, "fasta"))
                    sequences_to_write = sequences[:max_sequences]

                    # Escribir las secuencias seleccionadas en el archivo de salida
                    for seq in sequences_to_write:
                        outfile.write(f">{seq.id}\n{str(seq.seq)}\n")
                else:
                    print(f"Advertencia: Archivo {fasta_filename} no encontrado.")

def main():
    args = parse_arguments()

    # Crear directorio de salida si no existe
    os.makedirs(args.output_dir, exist_ok=True)

    # Determinar el subdirectorio correspondiente
    fasta_dir = find_matching_subdirectory(os.path.basename(args.csv), args.fasta_base_dir)

    output_file = os.path.join(args.output_dir, os.path.basename(args.csv).replace(".csv", ".mafft.fasta"))

    if fasta_dir:
        process_csv_and_fasta(output_file, args.csv, fasta_dir, args.max_sequences)
    else:
        print(f"Advertencia: No se encontró un subdirectorio para {args.csv}. Generando archivo vacío.")
        open(output_file, "w").close()

if __name__ == "__main__":
    main()
