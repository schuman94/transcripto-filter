import os
import sys

def clean_fasta(input_file, output_file):
    """Función para eliminar guiones de las secuencias en un archivo FASTA."""
    with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
        for line in fin:
            if line.startswith('>'):
                fout.write(line)  # Escribe la línea del identificador como está
            else:
                fout.write(line.replace('-', ''))  # Elimina guiones de las secuencias

def process_directory(input_dir):
    """Procesa todos los archivos FASTA en el directorio proporcionado."""
    output_dir = os.path.join(input_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)  # Crea el directorio 'output' si no existe

    for filename in os.listdir(input_dir):
        if filename.endswith('.fasta'):  # Asegúrate de que es un archivo FASTA
            new_name = filename.replace('.mafft', '')  # Elimina '.mafft' del nombre
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(output_dir, new_name)
            clean_fasta(input_file, output_file)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Uso: python script.py <directorio>")
    else:
        input_dir = sys.argv[1]
        process_directory(input_dir)
