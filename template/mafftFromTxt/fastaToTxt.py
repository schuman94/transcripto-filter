import sys

def fasta_to_txt(input_fasta, output_txt):
    with open(input_fasta, 'r') as infile, open(output_txt, 'w') as outfile:
        max_id_length = 0
        sequences = []

        # Leer el archivo fasta y encontrar el identificador más largo
        sequence = ""
        for line in infile:
            if line.startswith('>'):
                if sequence:
                    sequences.append((seq_id, sequence))
                seq_id = line[1:].strip()
                if len(seq_id) > max_id_length:
                    max_id_length = len(seq_id)
                sequence = ""
            else:
                sequence += line.strip()
        if sequence:
            sequences.append((seq_id, sequence))

        # Calcular la posición inicial de la secuencia
        sequence_start_position = max_id_length + 10

        # Escribir el archivo txt con las secuencias alineadas
        for seq_id, sequence in sequences:
            spaces_needed = sequence_start_position - len(seq_id)
            outfile.write(seq_id + ' ' * spaces_needed + sequence + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python fastaToTxt.py <archivo_fasta>")
        sys.exit(1)

    input_fasta = sys.argv[1]
    output_txt = "secuencias_converted.txt"

    fasta_to_txt(input_fasta, output_txt)
    print(f"Archivo {output_txt} creado exitosamente")
