import tkinter as tk
from tkinter import messagebox
import pyperclip

def generate_command():
    r1 = entry_r1.get()
    r2 = entry_r2.get()
    db1 = entry_db1.get()
    trinity = entry_trinity.get()
    db2 = entry_db2.get()
    db3 = entry_db3.get()
    fastqc = var_fastqc.get()
    busco = var_busco.get()
    trinity_mode = var_trinity_mode.get()
    superfamily_analysis = var_superfamily_analysis.get()

    # Validar campos obligatorios
    if trinity_mode:
        if not trinity or not db1:
            if not superfamily_analysis:
                messagebox.showerror("Error", "Debe rellenar los campos 'trinity' y 'db1'.")
            else:
                messagebox.showerror("Error", "Debe rellenar los campos 'trinity', 'db1', 'db2' y 'db3'.")
            return
    else:
        if not r1 or not r2 or not db1:
            if not superfamily_analysis:
                messagebox.showerror("Error", "Debe rellenar los campos 'r1', 'r2' y 'db1'.")
            else:
                messagebox.showerror("Error", "Debe rellenar los campos 'r1', 'r2', 'db1', 'db2' y 'db3'.")
            return

    if superfamily_analysis:
        if not db2 or not db3:
            messagebox.showerror("Error", "Debe rellenar los campos 'db2' y 'db3' para el análisis de superfamilias.")
            return

    command = "sbatch autolauncher.sh"

    if r1 and not trinity_mode:
        command += f" --r1 {r1}"
    if r2 and not trinity_mode:
        command += f" --r2 {r2}"
    if db1:
        command += f" --db1 {db1}"
    if trinity and trinity_mode:
        command += f" --trinity {trinity}"
    if db2 and superfamily_analysis:
        command += f" --db2 {db2}"
    if db3 and superfamily_analysis:
        command += f" --db3 {db3}"
    if not fastqc:
        command += " --fastqc false"
    if not busco:
        command += " --busco false"

    pyperclip.copy(command)
    messagebox.showinfo("Éxito", "El comando ha sido copiado al portapapeles.")

def toggle_trinity_mode():
    trinity_mode = var_trinity_mode.get()
    if trinity_mode:
        entry_r1.config(state='disabled')
        entry_r2.config(state='disabled')
        entry_trinity.config(state='normal')
    else:
        entry_r1.config(state='normal')
        entry_r2.config(state='normal')
        entry_trinity.config(state='disabled')

def toggle_superfamily_analysis():
    superfamily_analysis = var_superfamily_analysis.get()
    if superfamily_analysis:
        entry_db2.config(state='normal')
        entry_db3.config(state='normal')
    else:
        entry_db2.config(state='disabled')
        entry_db3.config(state='disabled')

app = tk.Tk()
app.title("Generador de comandos para Transcripto-filter")

tk.Label(app, text="Ruta del read1 (r1):").grid(row=0, column=0, sticky=tk.W)
entry_r1 = tk.Entry(app, width=100)
entry_r1.grid(row=0, column=1)

tk.Label(app, text="Ruta del read2 (r2):").grid(row=1, column=0, sticky=tk.W)
entry_r2 = tk.Entry(app, width=100)
entry_r2.grid(row=1, column=1)

tk.Label(app, text="Ruta de la base de datos general (db1):").grid(row=2, column=0, sticky=tk.W)
entry_db1 = tk.Entry(app, width=100)
entry_db1.grid(row=2, column=1)

tk.Label(app, text="Ruta del fichero fasta ensamblado con Trinity (trinity):").grid(row=3, column=0, sticky=tk.W)
entry_trinity = tk.Entry(app, width=100)
entry_trinity.grid(row=3, column=1)

tk.Label(app, text="Ruta de la base de datos de péptidos señal (db2):").grid(row=4, column=0, sticky=tk.W)
entry_db2 = tk.Entry(app, width=100)
entry_db2.grid(row=4, column=1)

tk.Label(app, text="Ruta de la base de datos de superfamilias (db3):").grid(row=5, column=0, sticky=tk.W)
entry_db3 = tk.Entry(app, width=100)
entry_db3.grid(row=5, column=1)

var_fastqc = tk.BooleanVar(value=True)
tk.Checkbutton(app, text="Ejecutar FASTQC", variable=var_fastqc).grid(row=6, sticky=tk.W, columnspan=2)

var_busco = tk.BooleanVar(value=True)
tk.Checkbutton(app, text="Ejecutar BUSCO", variable=var_busco).grid(row=7, sticky=tk.W, columnspan=2)

var_superfamily_analysis = tk.BooleanVar(value=True)
tk.Checkbutton(app, text="Incluir el análisis de superfamilias", variable=var_superfamily_analysis, command=toggle_superfamily_analysis).grid(row=8, sticky=tk.W, columnspan=2)

var_trinity_mode = tk.BooleanVar()
tk.Checkbutton(app, text="Usar fichero fasta previamente ensamblado con Trinity", variable=var_trinity_mode, command=toggle_trinity_mode).grid(row=9, sticky=tk.W, columnspan=2)

tk.Button(app, text="Generar comando", command=generate_command).grid(row=10, columnspan=2)

toggle_trinity_mode()  # Inicializa el estado correcto de los campos
toggle_superfamily_analysis()  # Inicializa el estado correcto de los campos

app.mainloop()
