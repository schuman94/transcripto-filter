import os
import csv
from Bio import SeqIO
from Bio.SeqRecord import SeqRecord
from Bio.Seq import Seq

def seleccionar_mejor_frame(csv_path, sequence_id, criterios):
    """
    Selecciona el mejor frame según los criterios en orden de prioridad.
    """
    # Leer el archivo CSV y buscar las filas correspondientes a la secuencia
    with open(csv_path, "r") as archivo_csv:
        lector = csv.reader(archivo_csv)
        filas = [fila for fila in lector if fila[0] == sequence_id]

    if not filas:
        raise ValueError(f"No se encontraron filas en el CSV para la secuencia: {sequence_id}")

    # Ordenar las filas por los criterios en orden de prioridad
    filas_ordenadas = sorted(
        filas,
        key=lambda x: (
            float(x[criterios[0]]),   # evalue (menor es mejor)
            -float(x[criterios[1]]),  # pident (mayor es mejor)
            -float(x[criterios[2]]),  # bitscore (mayor es mejor)
            -int(x[criterios[3]])     # length (mayor es mejor)
        )
    )

    return filas_ordenadas  # Lista de filas ordenadas según el criterio

def filtrar_frames(input_dir, output_dir, csv_path):
    """
    Filtra los frames en cada archivo de la carpeta input_dir y guarda el mejor en output_dir.
    """
    for filename in os.listdir(input_dir):
        if filename.endswith(".fasta"):
            fasta_path = os.path.join(input_dir, filename)

            # Leer el primer encabezado del archivo FASTA y extraer el sequence_id
            with open(fasta_path, "r") as fasta_file:
                first_record = next(SeqIO.parse(fasta_file, "fasta"))
                # Extraer la parte antes de "_Frame"
                sequence_id = first_record.id.split("_Frame")[0]

            print(f"Procesando archivo: {filename}")
            print(f"ID de la secuencia extraído del FASTA: {sequence_id}")

            # Seleccionar el mejor frame en función del CSV
            filas_ordenadas = seleccionar_mejor_frame(
                csv_path,
                sequence_id,
                criterios=[9, 2, 10, 3]  # Columnas de evalue, pident, bitscore, length
            )

            frame_seleccionado = None
            for fila in filas_ordenadas:
                frame = fila[-1]  # Columna del qframe (última columna)
                # Verificar si el frame está presente en el archivo FASTA
                with open(fasta_path, "r") as fasta_file:
                    for record in SeqIO.parse(fasta_file, "fasta"):
                        if record.id.endswith(frame):
                            frame_seleccionado = record
                            break
                if frame_seleccionado:
                    break

            # Si no se encuentra ningún frame, generar un error
            if not frame_seleccionado:
                raise ValueError(f"No se encontró un frame válido para {sequence_id} en {filename}")

            # Limpiar la secuencia (eliminar guiones) y guardar en un nuevo archivo
            frame_seleccionado.seq = Seq(str(frame_seleccionado.seq).replace("-", ""))
            output_path = os.path.join(output_dir, filename)
            SeqIO.write(frame_seleccionado, output_path, "fasta")

if __name__ == "__main__":
    import argparse

    # Parsear argumentos
    parser = argparse.ArgumentParser(description="Filtrar frames de mejor puntuación en FASTA.")
    parser.add_argument("input_dir", help="Carpeta con los archivos FASTA multiframe.")
    parser.add_argument("output_dir", help="Carpeta donde guardar los FASTA filtrados.")
    parser.add_argument("csv_path", help="Ruta al archivo CSV generado por BLAST.")
    args = parser.parse_args()

    # Ejecutar el script
    filtrar_frames(args.input_dir, args.output_dir, args.csv_path)
