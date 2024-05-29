import sys

def fasta_to_single_line(input_fasta, output_fasta):
    with open(input_fasta, 'r') as infile, open(output_fasta, 'w') as outfile:
        sequence = ""
        for line in infile:
            if line.startswith('>'):
                if sequence:
                    outfile.write(sequence + '\n')
                outfile.write(line)
                sequence = ""
            else:
                sequence += line.strip()
        if sequence:
            outfile.write(sequence + '\n')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python fastaToSingleLine.py <archivo_fasta>")
        sys.exit(1)

    input_fasta = sys.argv[1]
    output_fasta = "secuencias_single_line.fasta"

    fasta_to_single_line(input_fasta, output_fasta)
    print(f"Archivo {output_fasta} creado exitosamente")
