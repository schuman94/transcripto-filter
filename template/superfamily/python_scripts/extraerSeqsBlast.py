import pandas as pd
from Bio import SeqIO
import sys
import os

def leer_blast_csv(archivo_blast_csv):
    return pd.read_csv(archivo_blast_csv, header=None, names=['qseqid', 'sseqid', 'pident', 'length', 'mismatch', 'gapopen', 'qstart', 'qend', 'sstart', 'send', 'evalue', 'bitscore'])

def leer_info_csv(archivo_info_csv):
    return pd.read_csv(archivo_info_csv, header=0, names=['n', 'qseqid', 'secuencia'])

def leer_fasta_grande(archivo_fasta_grande):
    seq_records = {}
    for record in SeqIO.parse(archivo_fasta_grande, "fasta"):
        if record.id not in seq_records:
            # Añade el registro al diccionario solo si el id no existe ya,
            # asegurando que solo la primera aparición se mantenga
            seq_records[record.id] = record
    return seq_records

def crear_archivos_fasta(df_blast, df_info, seq_records, directorio_salida):
    for qseqid, grupo in df_blast.groupby('qseqid'):
        info_fila = df_info[df_info['qseqid'] == qseqid]
        if not info_fila.empty:
            n = info_fila.iloc[0]['n']
            qseqid_secuencia = info_fila.iloc[0]['secuencia']
            archivo_fasta_salida = f"seq_{n}.fasta"
            ruta_completa = os.path.join(directorio_salida, archivo_fasta_salida)
            with open(ruta_completa, "w") as archivo_salida:
                archivo_salida.write(f">{qseqid}\n{qseqid_secuencia}\n")
                for sseqid in grupo['sseqid']:
                    if sseqid in seq_records:
                        SeqIO.write(seq_records[sseqid], archivo_salida, "fasta")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: script.py <archivo_blast_csv> <archivo_info_csv> <archivo_fasta_grande> <directorio_salida>")
        sys.exit(1)

    archivo_blast_csv = sys.argv[1]
    archivo_info_csv = sys.argv[2]
    archivo_fasta_grande = sys.argv[3]
    directorio_salida = sys.argv[4]

    df_blast = leer_blast_csv(archivo_blast_csv)
    df_info = leer_info_csv(archivo_info_csv)
    seq_records = leer_fasta_grande(archivo_fasta_grande)

    crear_archivos_fasta(df_blast, df_info, seq_records, directorio_salida)
