import sys

def txt_to_fasta(input_txt, output_fasta):
    with open(input_txt, 'r') as infile, open(output_fasta, 'w') as outfile:
        for line in infile:
            line = line.strip()
            if line:
                parts = line.split()
                seq_id = parts[0]
                sequence = ''.join(parts[1:]).replace('-', '')
                outfile.write(f'>{seq_id}\n{sequence}\n')

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python txtToFasta.py <archivo_txt>")
        sys.exit(1)

    input_txt = sys.argv[1]
    output_fasta = "secuencias.fasta"

    txt_to_fasta(input_txt, output_fasta)
    print(f"Archivo {output_fasta} creado exitosamente")
