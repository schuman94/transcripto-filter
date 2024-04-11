import csv
import sys
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO

def csv_to_fasta(csv_file_path, fasta_file_path):
    print(f"Leyendo el archivo CSV: {csv_file_path}")
    seq_records = []
    with open(csv_file_path, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader, None)  # Saltar los encabezados
        for row in csvreader:
            seq_id = row[1]
            seq = row[2]
            print(f"Procesando secuencia: ID={seq_id}...")
            seq_record = SeqRecord(Seq(seq), id=seq_id, description="")
            seq_records.append(seq_record)

    print(f"Se encontraron {len(seq_records)} secuencias. Escribiendo en FASTA: {fasta_file_path}")
    with open(fasta_file_path, 'w') as fasta_file:
        SeqIO.write(seq_records, fasta_file, 'fasta')
    print("Finalizado.")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso: python script.py <archivo_entrada.csv> <archivo_salida.fasta>")
    else:
        csv_file_path = sys.argv[1]
        fasta_file_path = sys.argv[2]
        csv_to_fasta(csv_file_path, fasta_file_path)
