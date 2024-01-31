import argparse

def eliminar_secuencias_repetidas_y_gene(archivo_entrada, archivo_salida):
    secuencias_unicas = set()
    with open(archivo_entrada, 'r') as entrada, open(archivo_salida, 'w') as salida:
        guardar_secuencia = True
        for linea in entrada:
            if linea.startswith('>'):
                identificador = linea.strip()
                if identificador in secuencias_unicas or identificador.startswith('>gene:'):
                    guardar_secuencia = False
                else:
                    secuencias_unicas.add(identificador)
                    guardar_secuencia = True
                    salida.write(linea)
            else:
                if guardar_secuencia:
                    salida.write(linea)

def main():
    parser = argparse.ArgumentParser(description='Elimina secuencias repetidas y secuencias que comienzan con ">gene:" en archivos FASTA.')
    parser.add_argument('archivo_entrada', type=str, help='Archivo FASTA de entrada')
    parser.add_argument('archivo_salida', type=str, help='Archivo FASTA de salida')
    args = parser.parse_args()

    eliminar_secuencias_repetidas_y_gene(args.archivo_entrada, args.archivo_salida)

if __name__ == "__main__":
    main()
