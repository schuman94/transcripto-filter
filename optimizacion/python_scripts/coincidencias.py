import os
import sys

def compare_fasta_files(auto_dir, manual_dir, original_dir, output_dir):
    print(f"Leyendo archivos desde {auto_dir}, {manual_dir} y {original_dir}...")

    # Leer nombres de archivos FASTA en los directorios
    auto_files = {f for f in os.listdir(auto_dir) if f.endswith('.fasta')}
    manual_files = {f for f in os.listdir(manual_dir) if f.endswith('.fasta')}
    original_files = {f for f in os.listdir(original_dir) if f.endswith('.fasta')}

    print(f"Encontrados {len(auto_files)} archivos FASTA en 'auto', {len(manual_files)} en 'manual', y {len(original_files)} en 'original'.")

    # Calcular verdaderos positivos, falsos positivos, falsos negativos y verdaderos negativos
    true_positives = auto_files.intersection(manual_files)
    false_positives = auto_files.difference(manual_files)
    false_negatives = manual_files.difference(auto_files)
    true_negatives = original_files.difference(auto_files.union(manual_files))

    print(f"Verdaderos Positivos: {len(true_positives)}, Falsos Positivos: {len(false_positives)}, Falsos Negativos: {len(false_negatives)}, Verdaderos Negativos: {len(true_negatives)}")

    # Crear el directorio de salida si no existe
    if not os.path.exists(output_dir):
        print(f"Creando directorio de salida {output_dir}...")
        os.makedirs(output_dir)
    else:
        print(f"Usando directorio de salida existente {output_dir}.")

    # Rutas para los archivos de salida
    tp_path = os.path.join(output_dir, 'true_positives.txt')
    fp_path = os.path.join(output_dir, 'false_positives.txt')
    fn_path = os.path.join(output_dir, 'false_negatives.txt')
    tn_path = os.path.join(output_dir, 'true_negatives.txt')
    summary_path = os.path.join(output_dir, 'summary.txt')

    # Escribir los resultados en archivos de texto
    with open(tp_path, 'w') as tp_file, \
         open(fp_path, 'w') as fp_file, \
         open(fn_path, 'w') as fn_file, \
         open(tn_path, 'w') as tn_file:
        tp_file.write('\n'.join(true_positives))
        fp_file.write('\n'.join(false_positives))
        fn_file.write('\n'.join(false_negatives))
        tn_file.write('\n'.join(true_negatives))

    # Escribir el resumen en el archivo de texto
    with open(summary_path, 'w') as summary_file:
        summary_file.write(f"TP={len(true_positives)}\n")
        summary_file.write(f"FP={len(false_positives)}\n")
        summary_file.write(f"FN={len(false_negatives)}\n")
        summary_file.write(f"TN={len(true_negatives)}\n")

    print(f"Informes generados en {output_dir}: 'true_positives.txt', 'false_positives.txt', 'false_negatives.txt', 'true_negatives.txt', 'summary.txt'")

if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Uso: python script_name.py /path/to/auto_dir /path/to/manual_dir /path/to/original_dir /path/to/output_dir")
        sys.exit(1)

    auto_directory = sys.argv[1]
    manual_directory = sys.argv[2]
    original_directory = sys.argv[3]
    output_directory = sys.argv[4]

    print("Iniciando el proceso de comparación...")
    compare_fasta_files(auto_directory, manual_directory, original_directory, output_directory)
