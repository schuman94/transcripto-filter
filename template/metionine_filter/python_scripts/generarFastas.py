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
        vector_alineamiento = fila['Vector_alineamiento']

        posicion_subcadena_alineada = obtener_posicion_subcadena_alineada(vector_alineamiento)
        # Lista con el identificador del frame y la posicion de su subcadena alineada
        par_frame_subcadena = (frame_id, posicion_subcadena_alineada)

        # Añadir al diccionario
        if seq_file not in diccionario:
            diccionario[seq_file] = {'frame': set(),
                                     'ref': set()}

        diccionario[seq_file]['frame'].add(par_frame_subcadena)
        diccionario[seq_file]['ref'].add(ref_id)

    return diccionario

def obtener_posicion_subcadena_alineada(vector_alineamiento):
    # Dividir la cadena en subcadenas por los asteriscos
    subcadenas = vector_alineamiento.split('*')

    # Diccionario para almacenar la cuenta de "1" para cada subcadena
    cuenta_1s = {}

    # Recorrer cada subcadena y contar los "1"
    for i, subcadena in enumerate(subcadenas):
        cuenta_1s[i] = subcadena.count('1')

    # Encontrar la subcadena con la mayor cantidad de "1"
    subcadena_max_1s = max(cuenta_1s, key=cuenta_1s.get)

    return subcadena_max_1s

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

def trim_seq(secuencia, posicion):
    subcadenas = secuencia.split('*')
    return subcadenas[posicion]

def generar_fastas(diccionario, directorio_fasta_original, directorio_salida_Alineamientos_pre_mafft):
    if not os.path.exists(directorio_salida_Alineamientos_pre_mafft):
        os.makedirs(directorio_salida_Alineamientos_pre_mafft)

    for seq_file, contenido in diccionario.items():
        archivo_salida = os.path.join(directorio_salida_Alineamientos_pre_mafft, f"seq_{seq_file}.fasta")
        with open(archivo_salida, 'w') as salida:
            for par_frame in contenido['frame']:
                frame_id = par_frame[0]
                posicion_subcadena = par_frame[1]

                secuencia_frame = obtener_secuencia(frame_id, directorio_fasta_original)
                secuencia_frame = trim_seq(secuencia_frame,posicion_subcadena)
                if secuencia_frame:
                    salida.write(f">{frame_id}\n{secuencia_frame}\n")

            for ref_id in contenido['ref']:
                secuencia_ref = obtener_secuencia(ref_id, directorio_fasta_original)
                if secuencia_ref:
                    # TODO: AQUI ES INTERESANTE OBTENER EL IDENTIFICADOR COMPLETO BUSCANDOLO EN LA BBDD ORIGINAL
                    salida.write(f">{ref_id}\n{secuencia_ref}\n")

# Rutas
ruta_informe= '../../curation_filter/Alineamientos_filtrados/informe.tsv'
directorio_fasta_original = '../../alignments/Alineamientos'
directorio_salida_Alineamientos_pre_mafft = '../mafft/Alineamientos_pre_mafft'

# Ejecucion
diccionario_resultado = procesar_informe(ruta_informe)
generar_fastas(diccionario_resultado, directorio_fasta_original, directorio_salida_Alineamientos_pre_mafft)
