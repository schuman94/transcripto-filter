import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, StringVar, Entry, Button, Label, Tk
from Bio import SeqIO
import pandas as pd

def convertir_a_ruta_larga(ruta):
    # Convertimos la ruta a formato extendido si estamos en Windows
    if os.name == 'nt':
        ruta = os.path.abspath(ruta)
        if not ruta.startswith('\\\\?\\'):
            ruta = '\\\\?\\' + ruta
    return ruta

def select_fasta_file():
    filename = filedialog.askopenfilename(filetypes=[("FASTA files", "*.fasta")])
    fasta_file.set(filename)

def select_txt_file():
    filename = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    txt_file.set(filename)

def select_output_file():
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    output_file.set(filename)

def execute():
    fasta_file_path = convertir_a_ruta_larga(fasta_file.get())
    txt_file_path = convertir_a_ruta_larga(txt_file.get())
    output_file_path = convertir_a_ruta_larga(output_file.get())

    if not fasta_file_path or not txt_file_path or not output_file_path:
        messagebox.showerror("Error", "Please select the input files and output file.")
        return

    try:
        # Leer el archivo TXT y construir un diccionario para búsqueda rápida
        superfamilia = ""
        id_to_superfamily = {}

        with open(txt_file_path, 'r') as txt_handle:
            for line in txt_handle:
                if line.startswith("[Superfamily "):
                    superfamilia = re.search(r'\[Superfamily (.*?)\]', line).group(1)
                match = re.match(r'(.+?Frame_[RF]\d)', line)
                if match:
                    identifier = match.group(1)
                    id_to_superfamily[identifier] = superfamilia

        # Verificación de datos del archivo TXT
        if not id_to_superfamily:
            messagebox.showerror("Error", "No se encontraron identificadores en el archivo TXT.")
            return

        # Leer el archivo FASTA y extraer la información necesaria
        found_records = []
        not_found_records = []
        for record in SeqIO.parse(fasta_file_path, "fasta"):
            # Extracción del identificador con el formato correcto
            match = re.match(r'(.+?Frame_[RF]\d)', record.id)
            if match:
                full_identifier = match.group(1)
                # Recortar el identificador para la búsqueda en el TXT
                search_identifier = re.sub(r'^.*(TRINITY.*Frame_[RF]\d)', r'\1', full_identifier)
                if search_identifier in id_to_superfamily:
                    found_records.append((full_identifier, id_to_superfamily[search_identifier]))
                else:
                    not_found_records.append((full_identifier, ""))

        # Verificación de datos del archivo FASTA
        if not found_records and not_found_records:
            messagebox.showerror("Error", "No se encontraron coincidencias entre los identificadores del archivo FASTA y el archivo TXT.")
            return

        # Escribir el archivo Excel de salida, primero los encontrados y luego los no encontrados
        records = found_records + not_found_records
        df = pd.DataFrame(records, columns=["Identifier", "Superfamily"])
        df.to_excel(output_file_path, index=False)

        messagebox.showinfo("Finalizado", f"Proceso completado correctamente. Se procesaron {len(records)} secuencias.")
    except Exception as e:
        messagebox.showerror("Error", f"Ha ocurrido un error: {str(e)}")

root = Tk()
root.title("ID-Superfamily")

fasta_file = StringVar()
txt_file = StringVar()
output_file = StringVar()

Label(root, text="FASTA file").grid(row=0, column=0)
Entry(root, textvariable=fasta_file).grid(row=0, column=1)
Button(root, text="Examinar", command=select_fasta_file).grid(row=0, column=2)

Label(root, text="TXT file").grid(row=1, column=0)
Entry(root, textvariable=txt_file).grid(row=1, column=1)
Button(root, text="Examinar", command=select_txt_file).grid(row=1, column=2)

Label(root, text="Output Excel file").grid(row=2, column=0)
Entry(root, textvariable=output_file).grid(row=2, column=1)
Button(root, text="Examinar", command=select_output_file).grid(row=2, column=2)

Button(root, text="Ejecutar", command=execute).grid(row=3, column=0, columnspan=3)

root.mainloop()
