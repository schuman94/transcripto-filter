import os
import argparse
import csv
from Bio import SeqIO
from fastaAnalyzer import FastaAnalyzer

def read_config(config_file):
    """
    Lee un archivo de configuración y devuelve un diccionario con los parámetros.
    """
    params = {}
    int_params = {"longitud_minima_subseq", "longitud_minima_subseq_estrica", "future_elements", "longitud_minima_total_subseqs"}  # Lista de parámetros que deben ser enteros
    with open(config_file, 'r') as file:
        for line in file:
            if line.startswith('#') or not line.strip():
                continue

            key, value = line.split('#')[0].strip().split('=')
            if key in int_params:
                params[key] = int(value)
            else:
                params[key] = float(value)
    return params



def filter_fasta_files(input_directory: str, output_directory: str, params: dict, generate_report: bool):
    """
    Filtra archivos FASTA basándose en criterios de alineamiento.
    """
    # Crear directorio de salida si no existe
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Procesar cada archivo FASTA en el directorio de entrada
    for filename in os.listdir(input_directory):
        if filename.endswith(".mafft.fasta"):
            file_path = os.path.join(input_directory, filename)
            analyzer = FastaAnalyzer(file_path, params, generate_report)
            results = analyzer.analyze_fasta(output_directory)

            # Guardar frames que pasan el filtro junto con las referencias
            if any(results.values()):
                output_file_path = os.path.join(output_directory, filename)
                with open(output_file_path, 'w') as output_file:
                    for record in analyzer.frames:
                        if results[record.id]:
                            output_file.write(f">{record.id}\n{str(record.seq)}\n")
                    for record in analyzer.references:
                        output_file.write(f">{record.id}\n{str(record.seq)}\n")

def sort_and_save_tsv_report(output_directory: str):
    """
    Ordena y guarda el informe TSV.
    """
    path = os.path.join(output_directory, "informe.tsv")
    with open(path, 'r', newline='') as file:
        reader = csv.reader(file, delimiter='\t')
        header = next(reader)
        sorted_rows = sorted(reader, key=lambda row: int(row[0]))

    with open(path, 'w', newline='') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(header)
        writer.writerows(sorted_rows)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Filter fasta files based on alignment criteria.")
    parser.add_argument("input_dir", type=str, help="Directory containing input .mafft.fasta files")
    parser.add_argument("output_dir", type=str, help="Directory where filtered fasta files will be stored")
    parser.add_argument("config_file", type=str, help="Configuration file with adjustable parameters")

    # En la sección de argumentos del script main.py
    parser.add_argument("--no_report", action="store_true", help="Disable report generation")

    # Lectura de parámetros ajustables y del argumento no_report
    args = parser.parse_args()
    params = read_config(args.config_file)

    # Pasar la opción de reporte a filter_fasta_files
    filter_fasta_files(args.input_dir, args.output_dir, params, not args.no_report)


    # Generar y ordenar el informe TSV solo si no_report no está activado
    if not args.no_report:
        sort_and_save_tsv_report(args.output_dir)
