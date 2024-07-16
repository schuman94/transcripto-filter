import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox

def convertir_a_ruta_larga(ruta):
    # Convertimos la ruta a formato extendido si estamos en Windows
    if os.name == 'nt':
        ruta = os.path.abspath(ruta)
        if not ruta.startswith('\\\\?\\'):
            ruta = '\\\\?\\' + ruta
    return ruta

def browse_input_directory(entry):
    dirname = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, dirname)

def browse_output_file(entry):
    filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx;*.xls")])
    entry.delete(0, tk.END)
    entry.insert(0, filename)

def execute_conversion(input_dir_entry, output_file_entry, prefix_entry):
    input_dir = convertir_a_ruta_larga(input_dir_entry.get())
    output_file = convertir_a_ruta_larga(output_file_entry.get())
    prefix = prefix_entry.get()

    if not input_dir or not output_file:
        messagebox.showerror("Error", "Por favor, seleccione una carpeta de entrada y un archivo de salida.")
        return

    try:
        writer = pd.ExcelWriter(output_file, engine='xlsxwriter')
        for filename in os.listdir(input_dir):
            if filename.endswith('.csv'):
                sheet_name = os.path.splitext(filename)[0][:31]  # Limitar nombre de la hoja a 31 caracteres
                csv_file = os.path.join(input_dir, filename)
                df = pd.read_csv(csv_file)
                if 'id' in df.columns:
                    df_filtered = df[df['id'].str.startswith(prefix, na=False)]
                    df_filtered.to_excel(writer, sheet_name=sheet_name, index=False)
                else:
                    messagebox.showwarning("Advertencia", f"El archivo {filename} no contiene una columna 'id' y será omitido.")
        writer.save()

        messagebox.showinfo("Éxito", f"Archivo Excel generado exitosamente en {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Ocurrió un error: {str(e)}")

def main():
    root = tk.Tk()
    root.title("CSV to Excel Converter with Filter")

    # Etiquetas y entradas
    tk.Label(root, text="Carpeta de entrada").grid(row=0, column=0, sticky=tk.W)
    input_dir_entry = tk.Entry(root, width=50)
    input_dir_entry.grid(row=0, column=1)
    tk.Button(root, text="Browse", command=lambda: browse_input_directory(input_dir_entry)).grid(row=0, column=2)

    tk.Label(root, text="Archivo de salida (Excel)").grid(row=1, column=0, sticky=tk.W)
    output_file_entry = tk.Entry(root, width=50)
    output_file_entry.grid(row=1, column=1)
    tk.Button(root, text="Guardar como", command=lambda: browse_output_file(output_file_entry)).grid(row=1, column=2)

    tk.Label(root, text="Prefijo para filtrar 'id'").grid(row=2, column=0, sticky=tk.W)
    prefix_entry = tk.Entry(root, width=50)
    prefix_entry.grid(row=2, column=1)
    prefix_entry.insert(0, "TRINITY")

    # Botón de ejecución
    tk.Button(root, text="Convertir", command=lambda: execute_conversion(input_dir_entry, output_file_entry, prefix_entry)).grid(row=3, column=0, columnspan=3)

    # Mantener la ventana abierta
    root.mainloop()

if __name__ == '__main__':
    main()
