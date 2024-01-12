import pandas as pd
import os

def procesar_informe(ruta_informe):
    # Leer el archivo TSV usando Pandas
    df = pd.read_csv(ruta_informe, delimiter='\t', header=0)

    # Filtrar filas donde Pasa_filtro es True
    df_filtrado = df[df['Pasa_filtro'] == True]

    # Crear un diccionario vacío
    diccionario = {}

    # Iterar a través de las filas del DataFrame filtrado
    for _, fila in df_filtrado.iterrows():
        seq_file = fila['Seq_file']
        frame_id = fila['Frame_ID']
        ref_id = fila['Ref_ID']

        # Añadir al diccionario
        if seq_file not in diccionario:
            diccionario[seq_file] = {'frame': set(), 'ref': set()}

        diccionario[seq_file]['frame'].add(frame_id)
        diccionario[seq_file]['ref'].add(ref_id)

    return diccionario

def obtener_secuencia(identificador, directorio_fasta_original):
    for archivo in os.listdir(directorio_fasta_original):
        if archivo.endswith('.fasta'):
            with open(os.path.join(directorio_fasta_original, archivo), 'r') as fasta_file:
                secuencia_encontrada = False
                secuencia = ""
                for linea in fasta_file:
                    if linea.startswith(f">{identificador}"):
                        secuencia_encontrada = True
                    elif secuencia_encontrada:
                        if linea.startswith('>'):
                            break
                        secuencia += linea.strip()
                if secuencia_encontrada:
                    return secuencia
    return None

def generar_fastas(diccionario, directorio_fasta_original, directorio_salida_Alineamientos_pre_mafft):
    if not os.path.exists(directorio_salida_Alineamientos_pre_mafft):
        os.makedirs(directorio_salida_Alineamientos_pre_mafft)

    for seq_file, contenido in diccionario.items():
        archivo_salida = os.path.join(directorio_salida_Alineamientos_pre_mafft, f"seq_{seq_file}.fasta")
        with open(archivo_salida, 'w') as salida:
            for frame_id in contenido['frame']:
                secuencia_frame = obtener_secuencia(frame_id, directorio_fasta_original)
                if secuencia_frame:
                    salida.write(f">{frame_id}\n{secuencia_frame}\n")

            for ref_id in contenido['ref']:
                secuencia_ref = obtener_secuencia(ref_id, directorio_fasta_original)
                if secuencia_ref:
                    salida.write(f">{ref_id}\n{secuencia_ref}\n")

# Rutas
ruta_informe= '../../curation_filter/Alineamientos_filtrados/informe.tsv'
directorio_fasta_original = '../../alignments/Alineamientos'
directorio_salida_Alineamientos_pre_mafft = '../Alineamientos_mafft'

# Ejecucion
diccionario_resultado = procesar_informe(ruta_informe)
generar_fastas(diccionario_resultado, directorio_fasta_original, directorio_salida_Alineamientos_pre_mafft)
