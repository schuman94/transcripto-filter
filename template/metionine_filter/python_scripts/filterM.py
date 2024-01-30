import os
import shutil
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

def same_M_position_frame_ref(frame, ref_seq):
    """
    Comprueba si la primera secuencia no '-' en ref_seq es 'M' y si el carácter correspondiente en frame también es 'M'.
    Si es así, devuelve la posición de la 'M'.

    Args:
    frame (SeqRecord): La primera secuencia en el archivo FASTA, utilizada como frame de referencia.
    ref_seq (SeqRecord): La secuencia actual que se está analizando.

    Returns:
    int/None: La posición de la 'M' si coincide en frame, None en caso contrario.
    """
    for i, char in enumerate(ref_seq.seq):
        if char != '-':
            if char == 'M' and frame.seq[i] == 'M':
                return i  # Devuelve la posición de 'M'
            break
    return None

def buscar_posM_anterior(frame, posM):
    """
    Busca la posición de 'M' más cercana antes de posM en la secuencia frame.

    Args:
    frame (SeqRecord): La secuencia en la que se buscará.
    posM (int): La posición desde la cual comenzar la búsqueda hacia atrás.

    Returns:
    int/None: La posición de la última 'M' encontrada antes de posM, o None si no se encuentra.
    """
    posM_anterior = None
    # Comienza desde posM - 1 y retrocede hasta el inicio de la secuencia
    for i in range(posM - 1, -1, -1):
        if frame.seq[i] == 'M':
            posM_anterior = i
        elif frame.seq[i] == '*':
            break

    return posM_anterior


def limpiar_secuencias(records, startPos):
    """
    Limpia las secuencias eliminando los caracteres '-' y ajustando el inicio según startPos.
    Además, cada secuencia terminará en el siguiente codón de parada '*'.
    Devuelve una lista de objetos SeqRecord.
    """
    secuencias_limpias = []
    for record in records:
        # Encuentra la posición del siguiente '*' después de startPos. No debería haber.
        fin = record.seq.find('*', startPos)
        if fin == -1:  # Al no encontrar '*', usa el final de la secuencia
            fin = len(record.seq)

        # Extrae la subsecuencia desde startPos hasta fin (excluyendo '*') y elimina los '-'
        secuencia_limpia = str(record.seq[startPos:fin]).replace('-', '')

        # Crea un nuevo objeto SeqRecord con la secuencia limpia
        secuencia_limpia_record = SeqRecord(Seq(secuencia_limpia), id=record.id, description=record.description)
        secuencias_limpias.append(secuencia_limpia_record)

    return secuencias_limpias


def escribir_fasta_secuencias_limpias(archivo_destino, secuencias):
    """
    Escribe las secuencias en un archivo FASTA con cada secuencia en una sola línea.

    Args:
    archivo_destino (str): Ruta al archivo FASTA de destino.
    secuencias (list of SeqRecord): Lista de objetos SeqRecord para escribir en el archivo.
    """
    with open(archivo_destino, "w") as archivo:
        for secuencia in secuencias:
            archivo.write(f">{secuencia.id}\n")
            archivo.write(str(secuencia.seq) + "\n")

def comprobar_secuencia(input_directory, multiframe_directory, limpios_directory, perfectos_directory,
                        metionina_previa_directory, revision_manual_directory):
    # Iterar sobre cada archivo en el directorio de entrada
    for filename in os.listdir(input_directory):
        # Procesar solo los archivos que terminan en .mafft.fasta
        if filename.endswith(".mafft.fasta"):
            file_path = os.path.join(input_directory, filename)
            # Leer las secuencias del archivo FASTA
            records = list(SeqIO.parse(file_path, "fasta"))

            # Compara los dos primeros identificadores sin los dos últimos caracteres
            if records[0].id[:-2] == records[1].id[:-2]:
                # Si los identificadores son iguales, copia el archivo al directorio multiframe:
                shutil.copy(file_path, os.path.join(multiframe_directory, filename))
            else:
                # Si no son iguales, ejecuta same_M_position_frame_ref para cada secuencia desde la segunda
                dudoso = True
                frame = records[0]
                for ref_seq in records[1:]:

                    posM = same_M_position_frame_ref(frame, ref_seq)
                    if posM is None: # No coinciden las Metioninas
                        dudoso = True
                        continue
                    # else: # Coinciden las Metioninas
                    dudoso = False
                    posM_anterior = buscar_posM_anterior(frame, posM)
                    if posM_anterior is None:

                        # Alineamiento 100% perfecto.
                        # Enviamos una copia del fichero a la carpeta Alineamientos_Perfectos:
                        shutil.copy(file_path, os.path.join(perfectos_directory, filename))
                        # Limpiamos las secuencias:
                        secuencias_limpias = limpiar_secuencias(records, posM)
                        # Crear un nuevo archivo en Alineamientos_Limpios:
                        nuevo_archivo = os.path.join(limpios_directory, filename)
                        escribir_fasta_secuencias_limpias(nuevo_archivo, secuencias_limpias)
                        break  # Terminamos el bucle de lectura de los ref_seq
                    else: # existe PosM_anterior
                        # Enviamos una copia del fichero a la carpeta Alineamientos_M_previa:
                        shutil.copy(file_path, os.path.join(metionina_previa_directory, filename))
                        break  # Terminamos el bucle de lectura de los ref_seq
                if dudoso:
                    shutil.copy(file_path, os.path.join(revision_manual_directory, filename))

if __name__ == "__main__":
    input_directory = '../mafft/Alineamientos_mafft'
    multiframe_directory = '../resultados/Alineamientos_Multiframe'
    limpios_directory = '../resultados/Alineamientos_Limpios'
    perfectos_directory = '../resultados/Alineamientos_Perfectos'
    metionina_previa_directory = '../resultados/Alineamientos_M_Previa'
    revision_manual_directory = '../resultados/Alineamientos_Revision_Manual'
    comprobar_secuencia(input_directory, multiframe_directory, limpios_directory,
                         perfectos_directory, metionina_previa_directory, revision_manual_directory)
