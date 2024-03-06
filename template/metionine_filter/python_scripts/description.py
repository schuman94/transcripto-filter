import sys
import os
from Bio import SeqIO

def update_fasta_descriptions(directory, general_fasta):
    # Leer el archivo FASTA general y almacenar los identificadores y descripciones
    descriptions = {}
    for record in SeqIO.parse(general_fasta, "fasta"):
        descriptions[record.id] = record.description

    # Recorrer todos los archivos FASTA en el directorio
    for filename in os.listdir(directory):
        if filename.endswith(".fasta"):
            filepath = os.path.join(directory, filename)
            updated_records = []

            # Leer el archivo FASTA actual
            for record in SeqIO.parse(filepath, "fasta"):
                if record.id in descriptions:
                    # Actualizar la descripción si el identificador se encuentra en el archivo general
                    record.description = descriptions[record.id]
                updated_records.append(record)

            # Escribir los registros actualizados de vuelta al archivo sin insertar saltos de línea adicionales
            with open(filepath, "w") as output_handle:
                for record in updated_records:
                    output_handle.write(f">{record.description}\n{str(record.seq)}\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python script.py <directorio> <archivo_fasta_general>")
        sys.exit(1)

    directory = sys.argv[1]
    general_fasta = sys.argv[2]

    update_fasta_descriptions(directory, general_fasta)
