from typing import List

class Alignment:
    def __init__(self, frame_id: str, frame_sequence: str, ref_id: str, ref_sequence: str, params: dict):
        # Inicialización de las variables con los datos de las secuencias y los parámetros ajustables
        self.frame_id = frame_id
        self.frame_sequence = frame_sequence
        self.ref_id = ref_id
        self.ref_sequence = ref_sequence
        self.alignment_vector = list(self._create_alignment_vector())

        # Asignación de parámetros ajustables desde el diccionario 'params'
        self.porcentaje_minimo_coincidencia = params['porcentaje_minimo_coincidencia']
        self.longitud_minima_subseq = params['longitud_minima_subseq']
        self.porcentaje_minimo_coincidencia_estricto = params['porcentaje_minimo_coincidencia_estricto']
        self.longitud_minima_subseq_estrica = params['longitud_minima_subseq_estrica']
        self.future_elements = params['future_elements']
        self.longitud_minima_total_subseqs = params['longitud_minima_total_subseqs']
        self.ratio_minimo_longitud = params['ratio_minimo_longitud']

        # Inicialización del informe de alineamiento
        self.informe_alineamiento = {
            "Frame_ID": self.frame_id,
            "Ref_ID": self.ref_id,
            "Pasa_filtro": False,
            "Hay_segmento_de_subsecuencias_validas": False,
            "longitud_minima_total_subseqs_superada": False,
            "ratio_minimo_longitud_superado": False,
            "Stop_codon_en_mitad_de_dos_segmentos_subsecuencias_validas": False,
            "Vector_alineamiento": self.get_alignment_string()
        }

    def _create_alignment_vector(self) -> List[str]:
        """
        Crea un vector de alineación comparando las secuencias del marco y de referencia.
        Los valores del vector son: "1" para coincidencias, "0" para no coincidencias, "*" para codones de parada en el marco.
        Ignora los gaps.
        """
        vector = []
        for f, r in zip(self.frame_sequence, self.ref_sequence):
            if f == "-" and r == "-":
                continue
            elif f == "-" and r == "*":
                continue
            elif f == r:
                vector.append("1")
            elif f == "*":
                vector.append("*")
            else:
                vector.append("0")
        return vector

    def _split_on_stops(self, alignment_list):
        """
        Divide el vector de alineación en segmentos, separando por codones de parada.
        """
        segment = []
        for char in alignment_list:
            if char == "*":
                if segment:
                    yield segment
                    segment = []
            else:
                segment.append(char)
        if segment:
            yield segment


    def get_populated_subsequences(self) -> List[List[str]]:
        """
        Identifica y devuelve las subsecuencias que cumplen con los criterios de alineamiento especificados.
        """
        # Inicializamos una lista para almacenar las subsecuencias que cumplen los criterios
        candidate_list = []

        alignment_segments = [list(segment) for segment in self._split_on_stops(self.alignment_vector) if segment]


        for segment in alignment_segments:
                candidates_for_segment = self.checked_candidates(segment)
                if len(candidates_for_segment) > 0:
                    candidate_list.append(candidates_for_segment)

        # Si no hay subsecuencias válidas, devolvemos una lista vacia
        if len(candidate_list) == 0:
            #print("No hay segmento con subsecuencias válidas)")
            self.informe_alineamiento["Hay_segmento_de_subsecuencias_validas"] = False
            return []
        # Si tenemos un segmento válido, devolvemos la lista de subsecuencias dentro del segmento
        if len(candidate_list) == 1:
            #print("Tenemos un segmento de subsecuencias válidas:")
            #print(candidate_list[0])
            self.informe_alineamiento["Hay_segmento_de_subsecuencias_validas"] = True
            self.informe_alineamiento["Stop_codon_en_mitad_de_dos_segmentos_subsecuencias_validas"] = False
            return candidate_list[0]
        # En caso contrario, si tenemos más de un segmento valido,
        # es decir, más de un candidato, significa que el alineamiento está mal porque implica que hay stop codons por medio
        # Por lo tanto, devolvemos lista vacía
        else:
            #print("Tenemos más de un segmento de subsecuencias, por lo tanto hay stop codon de por medio:")
            #print(candidate_list)
            self.informe_alineamiento["Stop_codon_en_mitad_de_dos_segmentos_subsecuencias_validas"] = True
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
        for i, char in enumerate(segment):
            #print("vamos a analizar el char: " + char)
            # Si encontramos un uno, o un cero y los elementos futuros permiten extender la subsecuencia
            if char == "1" or (char == "0" and check_future_elements(i)):
                # Añadimos el caracter a la subsecuencia actual
                current_subseq.append(char)
                #print("Se ha añadido un char:")
                #print(current_subseq)
            else:
                # Eliminamos los ceros al inicio y final de la subsecuencia actual
                current_subseq = self.trim_zeros(current_subseq) #Este paso podriamos analizar si hacerlo ahora o despues de la siguiente condicion
                # Verificamos si la subsecuencia actual cumple los criterios para ser considerada
                if len(current_subseq) >= self.longitud_minima_subseq and current_subseq.count("1") >= len(current_subseq) * self.porcentaje_minimo_coincidencia:
                   candidates.append(current_subseq)
                   #print("La current subsec se ha añadido...")
                   #print(current_subseq)
                   #print("a la lista de candidatos:")
                   #print(candidates)
                elif len(current_subseq) >= self.longitud_minima_subseq_estrica and current_subseq.count("1") >= len(current_subseq) * self.porcentaje_minimo_coincidencia_estricto:
                   candidates.append(current_subseq)

                # Limpiamos la subsecuencia actual para empezar una nueva
                current_subseq = []

        # Si todavía tenemos una subsecuencia actual después de iterar a través de todo el vector de alineación
        if current_subseq:
            # Eliminamos los ceros al inicio y final de la subsecuencia actual
            current_subseq = self.trim_zeros(current_subseq)
            #print("Seguimos teniendo Current subsec:")
            #print(current_subseq)
            # Verificamos si la subsecuencia actual cumple los criterios para ser considerada
            if len(current_subseq) >= self.longitud_minima_subseq and current_subseq.count("1") >= len(current_subseq) * self.porcentaje_minimo_coincidencia:
                candidates.append(current_subseq)
                #print("la current subseq se ha añadido a la lista de candidatos porque ha pasado el filtro:")
                #print(candidates)

        return candidates

    def passes_filter(self) -> bool:
        """
        Determina si el alineamiento pasa los criterios del filtro.
        Se añade una comprobación para asegurarse de que no hay un codón de parada (*) entre subsecuencias pobladas.
        """
        subsequences = self.get_populated_subsequences()

        if not subsequences:
            #print("No hay subsecuencias que analizar en passes_filter")
            return False
        #else:
            #print("tenemos subsecuencias para analizar dentro de pass_filter:")
            #print(subsequences)

        longitud_total_subseqs = sum([len(s) for s in subsequences])
        #print("Total length = " + str(longitud_total_subseqs))
        longitud_total_referencia = len([c for c in self.ref_sequence if c != "-"])
        #print("Ref length = " + str(longitud_total_referencia))



        ratio_longitud = longitud_total_subseqs / longitud_total_referencia
        #print("El ratio de longitud es: " + str(ratio_longitud))

        if longitud_total_subseqs >= self.longitud_minima_total_subseqs and ratio_longitud > self.ratio_minimo_longitud:
            #print(f"{self.frame_id} alinea con {self.ref_id}")
            #if longitud_total_subseqs >= self.longitud_minima_total_subseqs:
                #print("Total length = " + str(longitud_total_subseqs))
                #print("Las longitud de la suma de subsecuencias es mayor o igual al umbral establecido")
            #if ratio_longitud > self.ratio_minimo_longitud:
                #print("Longitud de la secuencia de referencia = " + str(longitud_total_referencia))
                #print("El ratio de longitud es: " + str(ratio_longitud))
                #print("La longitud de la suma de subsecuencias sobre la longitud de la secuencia de referencia representa un porcentaje mayor o igual al umbral establecido")

            self.informe_alineamiento["longitud_minima_total_subseqs_superada"] = True
            self.informe_alineamiento["ratio_minimo_longitud_superado"] = True
            self.informe_alineamiento["Pasa_filtro"] = True

            return True

        if longitud_total_subseqs < self.longitud_minima_total_subseqs:
            #print("Las longitud de la suma de subsecuencias es menor al umbral establecido")
            self.informe_alineamiento["longitud_minima_total_subseqs_superada"] = False
        if ratio_longitud < self.ratio_minimo_longitud:
            #print("La longitud de la suma de subsecuencias sobre la longitud de la secuencia de referencia representa un porcentaje menor al umbral establecido")
            self.informe_alineamiento["ratio_minimo_longitud_superado"] = False
        return False

    def get_alignment_string(self) -> str:
        """
        Retorna el vector de alineación como una cadena.
        """
        return "".join(self.alignment_vector)

    # Función para eliminar ceros al inicio y al final de la subsecuencia
    def trim_zeros(self, subseq):
        # Eliminamos los ceros al final de la subsecuencia
        while subseq and subseq[-1] == "0":
            subseq.pop()
        # Eliminamos los ceros al inicio de la subsecuencia
        while subseq and subseq[0] == "0":
            subseq.pop(0)
        # Devolvemos la subsecuencia sin ceros al inicio y final
        return subseq
