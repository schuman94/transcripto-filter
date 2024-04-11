import pandas as pd
import sys

def procesar_csv_revision_manual(csv_blast, csv_inicial, csv_match_output, csv_no_match_output):
    # Leer el archivo CSV del blast sin encabezados, interesados solo en la primera columna
    df_blast = pd.read_csv(csv_blast, header=None, usecols=[0])
    df_blast.columns = ['id']  # Asignamos nombres a las columnas

    # Leer el archivo CSV inicial, que sí tiene encabezados
    df_inicial = pd.read_csv(csv_inicial)

    # Verificar si 'id' está en la segunda columna de df_inicial
    if df_inicial.columns[1] != 'id':
        print("La columna 'id' no se encuentra en la posición esperada en el archivo csv_inicial.")
        sys.exit(1)

    # Filtrar las filas de df_inicial basándonos en si 'id' está presente en df_blast
    df_match = df_inicial[df_inicial['id'].isin(df_blast['id'])]
    df_no_match = df_inicial[~df_inicial['id'].isin(df_blast['id'])]

    # Guardar los nuevos DataFrames resultantes en archivos CSV
    df_match.to_csv(csv_match_output, index=False)
    df_no_match.to_csv(csv_no_match_output, index=False)

    print(f'Archivos guardados: {csv_match_output} y {csv_no_match_output}')

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python procesar_csv_revision_manual.py <csv_blast> <csv_inicial> <csv_match_output> <csv_no_match_output>")
        sys.exit(1)

    csv_blast = sys.argv[1]
    csv_inicial = sys.argv[2]
    csv_match_output = sys.argv[3]
    csv_no_match_output = sys.argv[4]

    procesar_csv_revision_manual(csv_blast, csv_inicial, csv_match_output, csv_no_match_output)
