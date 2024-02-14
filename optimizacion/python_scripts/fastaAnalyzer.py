import os
import re
from Bio import SeqIO
from alignment import Alignment

class FastaAnalyzer:
    def __init__(self, file_path: str, params: dict, generate_report: bool = True):
        # Inicialización con la ruta del archivo y los parámetros ajustables
        self.file_path = file_path
        self.params = params  # Parámetros ajustables pasados al inicializar

        # Parsea el archivo FASTA y almacena las secuencias
        self.records = list(SeqIO.parse(self.file_path, "fasta"))
        self.frames = self.records[:6]  # Las primeras 6 secuencias son frames
        self.references = self.records[6:]  # Las secuencias restantes son referencias

        # Extracción del nombre del archivo de secuencia
        match = re.search(r'seq_(\d+)', self.file_path)
        self.seq_file = match.group(1) if match else os.path.basename(file_path)

        # print(f"Analizando {os.path.basename(file_path)}")

        # Controla si se debe generar un informe
        self.generate_report = generate_report

    def update_tsv(self, alignment: Alignment, output_directory: str):
        # Salir de la función si no se debe generar un informe
        if not self.generate_report:
            return

        """
        Actualiza o crea un fichero TSV con la información de filtros no superados de un objeto de alineación.
        """
        # Crear directorio de salida si no existe
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        file_path = os.path.join(output_directory, "informe.tsv")
        file_exists = os.path.exists(file_path)

        # Definir encabezados para el archivo TSV
        headers = [
            "Seq_file", "Frame_ID", "Ref_ID", "Pasa_filtro",
            "Hay_segmento_de_subsecuencias_validas", "longitud_minima_total_subseqs_superada",
            "ratio_minimo_longitud_superado", "Stop_codon_en_mitad_de_dos_segmentos_subsecuencias_validas",
            "Vector_alineamiento"
        ]

        with open(file_path, "a") as file:
            # Escribir encabezado si el archivo no existía
            if not file_exists:
                file.write("\t".join(headers) + "\n")

            # Escribir información del alineamiento en el archivo TSV
            values = [self.seq_file] + [str(alignment.informe_alineamiento[header]) for header in headers[1:]]
            file.write("\t".join(values) + "\n")

            # print(f"Se ha añadido una línea de {self.seq_file} al informe en la ruta: {os.path.abspath(file_path)}")

    def analyze_fasta(self, output_directory) -> dict:
        """
        Analiza un archivo FASTA y determina qué frames pasan el criterio del filtro.
        Devuelve un diccionario con los IDs de los frames como claves y valores booleanos indicando si pasaron el filtro.
        """
        results = {frame.id: False for frame in self.frames}  # Inicializando el diccionario de resultados

        # Procesamiento de cada frame con cada referencia
        for frame in self.frames:
            for ref in self.references:
                # Creación de un objeto de alineamiento con los parámetros
                alignment = Alignment(frame.id, str(frame.seq), ref.id, str(ref.seq), self.params)

                # Comprobación del filtro
                if alignment.passes_filter():
                    results[frame.id] = True
                    # Actualizar el archivo TSV con la información del alineamiento actual, si se requiere generar un informe
                    if self.generate_report:
                        self.update_tsv(alignment, output_directory)
                else:
                    # Actualizar el archivo TSV con la información del alineamiento actual, si se requiere generar un informe
                    if self.generate_report:
                        self.update_tsv(alignment, output_directory)

        return results
