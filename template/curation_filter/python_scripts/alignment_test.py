from typing import List
from alignment import Alignment

class Alignment_Test(Alignment):
    def __init__(self, frame_sequence: str, ref_sequence: str):

        frame_id = "Frame"
        ref_id = "Ref"
        params = {
            'porcentaje_minimo_coincidencia': 0.4,
            'longitud_minima_subseq': 8,
            'porcentaje_minimo_coincidencia_estricto': 0.5,
            'longitud_minima_subseq_estrica': 3,
            'future_elements': 20,
            'longitud_minima_total_subseqs': 25,
            'ratio_minimo_longitud': 0.5
        }

        # Llamada al constructor de la clase padre
        super().__init__(frame_id, frame_sequence, ref_id, ref_sequence, params)

        # PRINTS
        alignment_string = self.get_alignment_string()
        print("Construyendo vector de alineamiento:")
        print(alignment_string)

    def get_populated_subsequences(self) -> List[List[str]]:
        """
        Identifica y devuelve las subsecuencias que cumplen con los criterios de alineamiento especificados.
        """
        # Inicializamos una lista para almacenar las subsecuencias que cumplen los criterios
        candidate_list = []

        alignment_segments = [list(segment) for segment in self._split_on_stops(self.alignment_vector) if segment]

        print("Separamos en segmentos limitados por stop codon...")
        i_segment = 1
        for segment in alignment_segments:
            print(f"Buscando subsecuencias candidatas en el segmento {i_segment}")
            candidates_for_segment = self.checked_candidates(segment)
            if len(candidates_for_segment) > 0:
                candidate_list.append(candidates_for_segment)
            else:
                print("No hay subsecuencias candidatas en este segmento")
            i_segment += 1

        # Si no hay subsecuencias válidas, devolvemos una lista vacia
        if len(candidate_list) == 0:
            self.informe_alineamiento["Hay_segmento_de_subsecuencias_validas"] = False
            return []
        # Si tenemos un segmento válido, devolvemos la lista de subsecuencias dentro del segmento
        if len(candidate_list) == 1:
            self.informe_alineamiento["Hay_segmento_de_subsecuencias_validas"] = True
            self.informe_alineamiento["Stop_codon_en_mitad_de_dos_segmentos_subsecuencias_validas"] = False
            print("Hay un solo segmento con subsecuencias válidas. No interrumpe ningún stop codon")
            return candidate_list[0]
        # En caso contrario, si tenemos más de un segmento valido,
        # es decir, más de un candidato, significa que el alineamiento está mal porque implica que hay stop codons por medio
        # Por lo tanto, devolvemos lista vacía
        else:
            self.informe_alineamiento["Stop_codon_en_mitad_de_dos_segmentos_subsecuencias_validas"] = True
            print("Hay varios segmentos con subsecuencias válidas interrumpidos por stop codon")
            return []

    def checked_candidates(self, segment):
        """
        Verifica y devuelve las subsecuencias válidas dentro de un segmento dado.
        """

        # Comprueba si en un segmento hay subsecuencias validas.
        # Devuelve una lista llamada candidates donde sus elementos son listas, es decir, subsecuencias válidas
        # Por ejemplo: [[10101011111111] , [1010101111111], [1111111111111]]
        # Puede ocurrir que devuelva una lista vacia si ninguna subsecuencia es válida
        candidates = []

        # Inicializamos una lista para ir construyendo la subsecuencia actual
        current_subseq = []

        # Definimos una función para verificar si la subsecuencia actual puede ser extendida
        def check_future_elements(i: int) -> bool:
            for future_elements in range(self.future_elements, 1, -1):
                # Obtenemos un slice del array alignment_vector con el número actual de elementos futuros
                future_seq = segment[i:i+future_elements]

                # Si no hay elementos futuros, no podemos extender la subsecuencia
                if len(future_seq) <= 1 or "1" not in future_seq:
                    return False

                # Contamos los unos en los elementos futuros y en la subsecuencia actual
                future_ones = future_seq.count("1")
                current_ones = current_subseq.count("1")

                # Verificamos si la proporción de unos se mantiene o mejora con los elementos futuros disponibles
                if (future_ones + current_ones) / (len(current_subseq) + len(future_seq)) >= self.porcentaje_minimo_coincidencia:
                    return True  # Devolvemos True tan pronto como la condición se cumpla

            # Si después de probar todo el rango no se cumple la condición, devolvemos False
            return False

        # Iteramos a través del vector de alineación
        print("Analizando segmento...")
        for i, char in enumerate(segment):
            if char == "1" or (char == "0" and check_future_elements(i)):
                # Añadimos el caracter a la subsecuencia actual
                current_subseq.append(char)
            else:
                print("Ha terminado esta subsecuencia:")
                print(current_subseq)
                # Eliminamos los ceros al inicio y final de la subsecuencia actual
                current_subseq = self.trim_zeros(current_subseq)
                # Verificamos si la subsecuencia actual cumple los criterios para ser considerada
                if len(current_subseq) >= self.longitud_minima_subseq and current_subseq.count("1") >= len(current_subseq) * self.porcentaje_minimo_coincidencia:
                    candidates.append(current_subseq)
                    print("Se ha añadido a la lista de candidatos de este segmento una subsecuencia:")
                    print(current_subseq)
                elif len(current_subseq) >= self.longitud_minima_subseq_estrica and current_subseq.count("1") >= len(current_subseq) * self.porcentaje_minimo_coincidencia_estricto:
                    candidates.append(current_subseq)
                    print("Se ha añadido a la lista de candidatos de este segmento una subsecuencia:")
                    print(current_subseq)

                # Informar del porcentaje de coincidencia y longitud de la subsecuencia
                if current_subseq:
                    porcentaje_coincidencia = current_subseq.count("1") / len(current_subseq)
                    longitud_subseq = len(current_subseq)
                    print(f"Subsecuencia: {current_subseq}")
                    print(f"Porcentaje de coincidencia: {porcentaje_coincidencia:.2f}")
                    print(f"Longitud de subsecuencia: {longitud_subseq}")

                # Limpiamos la subsecuencia actual para empezar una nueva
                current_subseq = []

        # Si todavía tenemos una subsecuencia actual después de iterar a través de todo el vector de alineación
        if current_subseq:
            # Eliminamos los ceros al inicio y final de la subsecuencia actual
            current_subseq = self.trim_zeros(current_subseq)
            # Verificamos si la subsecuencia actual cumple los criterios para ser considerada
            if len(current_subseq) >= self.longitud_minima_subseq and current_subseq.count("1") >= len(current_subseq) * self.porcentaje_minimo_coincidencia:
                candidates.append(current_subseq)

            # Informar del porcentaje de coincidencia y longitud de la subsecuencia
            if current_subseq:
                porcentaje_coincidencia = current_subseq.count("1") / len(current_subseq)
                longitud_subseq = len(current_subseq)
                print(f"Subsecuencia: {current_subseq}")
                print(f"Porcentaje de coincidencia: {porcentaje_coincidencia:.2f}")
                print(f"Longitud de subsecuencia: {longitud_subseq}")

        return candidates

    def passes_filter(self) -> bool:
        """
        Determina si el alineamiento pasa los criterios del filtro.
        Se añade una comprobación para asegurarse de que no hay un codón de parada (*) entre subsecuencias pobladas.
        """
        subsequences = self.get_populated_subsequences()

        if not subsequences:
            return False

        longitud_total_subseqs = sum([len(s) for s in subsequences])
        print("Longitud total subsecs = " + str(longitud_total_subseqs))
        longitud_total_referencia = len([c for c in self.ref_sequence if c != "-"])
        print("Ref length = " + str(longitud_total_referencia))

        ratio_longitud = longitud_total_subseqs / longitud_total_referencia
        print("El ratio de longitud es: " + str(ratio_longitud))

        if longitud_total_subseqs >= self.longitud_minima_total_subseqs and ratio_longitud > self.ratio_minimo_longitud:
            self.informe_alineamiento["longitud_minima_total_subseqs_superada"] = True
            self.informe_alineamiento["ratio_minimo_longitud_superado"] = True
            self.informe_alineamiento["Pasa_filtro"] = True
            return True

        if longitud_total_subseqs < self.longitud_minima_total_subseqs:
            print("Las longitud de la suma de subsecuencias es menor al umbral establecido")
            self.informe_alineamiento["longitud_minima_total_subseqs_superada"] = False
        if ratio_longitud < self.ratio_minimo_longitud:
            print("La longitud de la suma de subsecuencias sobre la longitud de la secuencia de referencia representa un porcentaje menor al umbral establecido")
            self.informe_alineamiento["ratio_minimo_longitud_superado"] = False
        return False

# Ejemplo de uso
# >TRINITY_DN15_c0_g1_i1_Frame_R3
frame = "---------------------YTWQVLNER---------------------QDRF--FSPGQ------GGLTTSRMRCLPVFIILLLLIPFAPSVDVQTI---TKNDVTL--------------DSLRNVAT--------------------KPLQRLLN-T----------------RC---------C------------------------IKVHPC----------------------------------------CHNG*NETK*-----LEKRPLQTVPGCEIW------KADCSFRTCSW-----------------------------------------------"
# >Im_M_11|imperialis|M|49148.395122
refer = "---------------------------------------------------------------------------MYCLPVFIILLLLIPSAPSVDVQPI---TKNDVIL--------------DSLRNVAT--------------------KPLQRLLN-T----------------RC---------C------------------------IKFHPC----------------------------------------CHNG------------------------------------------------------------------------------------------"








test = Alignment_Test(frame, refer)
test.passes_filter()
