import os
import sys
import re

def rename_fasta_files(directory):
    # Expresión regular para identificar el patrón deseado en el nombre del archivo
    pattern = re.compile(r'seq_\d+\.')

    # Recorrer el directorio y sus subdirectorios
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".fasta"):
                # Buscar el patrón en el nombre del archivo
                match = pattern.search(filename)
                if match:
                    new_name = match.group() + "mafft.fasta"
                    old_filepath = os.path.join(dirpath, filename)
                    new_filepath = os.path.join(dirpath, new_name)

                    # Renombrar el archivo
                    os.rename(old_filepath, new_filepath)
                    print(f"Archivo '{filename}' en '{dirpath}' renombrado a '{new_name}'.")

                else:
                    print(f"El archivo {filename} en '{dirpath}' no cumple con el patrón, saltándolo...")
            else:
                print(f"El archivo {filename} en '{dirpath}' no es un archivo .fasta, saltándolo...")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python3 rename.py /path/to/directory")
        sys.exit(1)

    dir_path = sys.argv[1]
    rename_fasta_files(dir_path)
