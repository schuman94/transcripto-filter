import pandas as pd
from Bio import SeqIO
import sys
import os

def extraer_SF_hormone(sseqid, fasta_path):
    for record in SeqIO.parse(fasta_path, "fasta"):
        if record.id == sseqid:
            descripcion = record.description.split(' ', 1)[1]
            if descripcion.startswith("Superfamily: "):
                return descripcion.replace("Superfamily: ", "")
            elif descripcion.startswith("[") and descripcion.endswith("]"):
                return descripcion[1:-1]
            return descripcion
    return "unknown"

def main(blast_out_csv, blast_signal_csv, db_fasta, csv_ini, output_csv):
    # Verificar si el archivo blast_out_csv está vacío
    if os.path.getsize(blast_out_csv) == 0:
        print(f"El archivo {blast_out_csv} está vacío. Se creará un archivo de salida vacío con encabezados.")
        # Crear un DataFrame vacío con los encabezados esperados
        df_final = pd.DataFrame(columns=['n', 'id', 'SF_signal', 'pident_signal', 'match', 'SF-hormone', 'evalue', 'secuencia'])
        df_final.to_csv(output_csv, index=False)
        return

    # Leer el archivo blast_out_csv
    df_blast_out = pd.read_csv(blast_out_csv, header=None).sort_values(by=[10]).drop_duplicates(subset=0, keep='first')

    # Leer los archivos CSV
    df_blast_signal = pd.read_csv(blast_signal_csv)  # Leer con encabezados
    df_ini = pd.read_csv(csv_ini)

    final_data = []

    for index, row in df_blast_out.iterrows():
        id = row[0]
        match = row[1]
        evalue = row[10]

        # Filtrar df_blast_signal usando el nombre de la columna
        SF_signal_row = df_blast_signal[df_blast_signal['qseqid'] == id]

        # Manejo del DataFrame vacío
        SF_signal = SF_signal_row.iloc[0]['superfamily'] if not SF_signal_row.empty else "unknown"
        pident = SF_signal_row.iloc[0]['pident'] if not SF_signal_row.empty else 0

        SF_hormone = extraer_SF_hormone(match, db_fasta)

        secuencia_row = df_ini[df_ini['id'] == id]
        if not secuencia_row.empty:
            secuencia = secuencia_row.iloc[0][2]
            n = secuencia_row.iloc[0][0]  # Asumimos que 'n' es numérico
        else:
            secuencia, n = "unknown", "unknown"  # Proporciona valores por defecto para 'n' y 'secuencia'

        final_data.append([n, id, SF_signal, pident, match, SF_hormone, evalue, secuencia])

    # Crear el DataFrame final con los encabezados, incluso si final_data está vacío
    df_final = pd.DataFrame(final_data, columns=['n', 'id', 'SF_signal', 'pident_signal', 'match', 'SF-hormone', 'evalue', 'secuencia'])

    if df_final.empty:
        print("No existen datos para: " + output_csv + ". Se creará un csv vacío.")
    else:
        # Convertir 'n' a entero para el ordenamiento
        df_final['n'] = pd.to_numeric(df_final['n'], errors='coerce')
        df_final = df_final.sort_values(by='n', ascending=True)

    # Guardar el DataFrame final en un archivo CSV, garantizando que los encabezados siempre se creen
    df_final.to_csv(output_csv, index=False)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Uso: python script.py <blast_out_csv> <blast_signal_csv> <DB_fasta> <csv_ini> <output_csv>")
        sys.exit(1)

    blast_out_csv = sys.argv[1]
    blast_signal_csv = sys.argv[2]
    db_fasta = sys.argv[3]
    csv_ini = sys.argv[4]
    output_csv = sys.argv[5]

    main(blast_out_csv, blast_signal_csv, db_fasta, csv_ini, output_csv)


"""
Datos del csv final

id, SF_signal, pident, match, SF-hormone, evalue, secuencia

id se extrae de "blast_out_csv" de la primera columna
SF_signal se extrae de "blast_signal_csv" de la quinta columna (llamada "superfamily"), para localizar la linea debemos comprobar que en su primera columna tengamos el mismo valor que "id"
pident se extrae igual que la anterior, esa misma linea tiene una columna llamada "pident" (la segunda columna)
match se extrae de "blast_out_csv" de la segunda columna, de la misma linea que obtuvimos id
SF-hormone se extrae buscando en "DB_fasta" una secuencia que tenga como identificador nuesto valor "match", una vez encontrada, debe quedarse con la descripción siguiendo la norma que usamos anteriormente en otro script.
evalue se obtiene de blast_out_csv, ya sabes de sobra en qué posicion está esa columna.
secuencia se obtiene de csv_ini, se buscará la linea que en su segunda columna tenga un valor igual a id y una vez encontrada esa linea, nos quedamos con su tercera columna.
"""
