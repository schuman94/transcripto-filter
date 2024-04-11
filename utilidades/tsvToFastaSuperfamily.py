import csv
import sys

def tsv_to_fasta(tsv_file_path, fasta_file_path):
    """
    Convert a TSV file with columns [code, superfamily code, amino acid sequence]
    to a FASTA file.
    """
    with open(tsv_file_path, 'r') as tsv_file, open(fasta_file_path, 'w') as fasta_file:
        # Especifica el delimitador como tabulación ('\t')
        reader = csv.reader(tsv_file, delimiter='\t')
        for row in reader:
            # Asume que el TSV no tiene encabezado
            if len(row) == 3:  # Asegura que la fila tenga 3 columnas
                code, superfamily_code, peptide_sequence = row
                description_line = f">{code}_superfamily_{superfamily_code}\n"
                fasta_file.write(description_line)
                fasta_file.write(peptide_sequence + "\n")
            else:
                print(f"Skipping invalid row: {row}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python script.py input.tsv output.fasta")
    else:
        input_tsv = sys.argv[1]
        output_fasta = sys.argv[2]
        tsv_to_fasta(input_tsv, output_fasta)
