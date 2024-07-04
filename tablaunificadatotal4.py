import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def contar_tipos_peticion(file_path, id_col, type_col, module_col, output_path_base):
    # Cargar el archivo CSV
    data = pd.read_csv(file_path)
    
    # Contabilizar el número de veces que cada identificador tiene cada tipo de petición
    conteo_tipos_peticion = data.groupby([id_col, type_col]).size().reset_index(name='Conteo')

    # Pivotar los datos para tener type_col como columnas y id_col como filas
    pivot_table = conteo_tipos_peticion.pivot(index=id_col, columns=type_col, values='Conteo').fillna(0)

    # Calcular la sumatoria total de cada identificador
    pivot_table['Total clics'] = pivot_table.sum(axis=1)

    # Calcular la cantidad de fechas únicas por identificador y módulo
    unique_dates = data.groupby([id_col, module_col])['Fecha'].nunique().reset_index(name='Fechas_Diferentes')
    pivot_table = pd.merge(pivot_table, unique_dates, on=id_col, how='left').fillna(0)

    # Resetear el índice para convertir id_col de nuevo en una columna
    pivot_table.reset_index(inplace=True)

    # Guardar la tabla pivotada en un archivo Excel
    output_file_pivot_path = f'{output_path_base}_unificado.xlsx'
    pivot_table.to_excel(output_file_pivot_path, index=False, engine='openpyxl')

    return pivot_table, output_file_pivot_path

def open_file():
    file_path = filedialog.askopenfilename(title="Abrir archivo CSV", filetypes=[("CSV files", "*.csv")])
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

def save_file():
    output_path = filedialog.asksaveasfilename(title="Guardar archivo Excel", defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
    if output_path:
        entry_output_path.delete(0, tk.END)
        entry_output_path.insert(0, output_path)

def process_files():
    file_path = entry_file_path.get()
    output_path_base = entry_output_path.get()
    
    if not file_path or not output_path_base:
        messagebox.showerror("Error", "Por favor, selecciona ambos archivos.")
        return

    try:
        id_col = entry_id_col.get()
        type_col = entry_type_col.get()
        module_col = entry_module_col.get()
        
        pivot_table, output_file_pivot_path = contar_tipos_peticion(file_path, id_col, type_col, module_col, output_path_base)
        messagebox.showinfo("Éxito", f"Archivo guardado:\n{output_file_pivot_path}")
        
        # Actualizar la lista desplegable con las nuevas columnas
        columns = pivot_table.columns.tolist()
        column_selector['values'] = columns

        # Guardar la tabla pivotada en una variable global para su posterior uso
        global global_pivot_table
        global_pivot_table = pivot_table

    except Exception as e:
        messagebox.showerror("Error", str(e))

def show_column():
    selected_column = column_selector.get()
    selected_id = entry_id_selector.get()
    
    if selected_column and selected_id:
        try:
            selected_id = int(selected_id)
            filtered_row = global_pivot_table[global_pivot_table[entry_id_col.get()] == selected_id]

            if not filtered_row.empty:
                result = filtered_row[selected_column].values[0]
            else:
                result = "No"

            # Mostrar el resultado en un mensaje
            if selected_column == 'Fechas_Diferentes':
                messagebox.showinfo("Resultado", f"El identificador '{selected_id}' tiene {result} fechas diferentes en el módulo seleccionado.")
            else:
                messagebox.showinfo("Resultado", f"El identificador '{selected_id}' tiene valores superiores a 0 en la columna '{selected_column}': {result}")
                
        except ValueError:
            messagebox.showerror("Error", "El identificador debe ser un número.")
        except KeyError:
            messagebox.showerror("Error", f"El identificador '{selected_id}' no se encuentra en los datos.")
    else:
        messagebox.showerror("Error", "Por favor, selecciona una columna y un identificador.")

# Configuración de la interfaz gráfica
root = tk.Tk()
root.title("Contador de Tipos de Petición")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="Ruta del archivo CSV:").grid(row=0, column=0, sticky=tk.W)
entry_file_path = tk.Entry(frame, width=50)
entry_file_path.grid(row=0, column=1, padx=5, pady=5)
tk.Button(frame, text="Abrir", command=open_file).grid(row=0, column=2, padx=5, pady=5)

tk.Label(frame, text="Ruta para guardar el archivo Excel:").grid(row=1, column=0, sticky=tk.W)
entry_output_path = tk.Entry(frame, width=50)
entry_output_path.grid(row=1, column=1, padx=5, pady=5)
tk.Button(frame, text="Guardar", command=save_file).grid(row=1, column=2, padx=5, pady=5)

tk.Label(frame, text="Nombre de la columna del identificador:").grid(row=2, column=0, sticky=tk.W)
entry_id_col = tk.Entry(frame)
entry_id_col.grid(row=2, column=1, padx=5, pady=5)
entry_id_col.insert(0, "Identificador")  # Valor por defecto

tk.Label(frame, text="Nombre de la columna del tipo de petición:").grid(row=3, column=0, sticky=tk.W)
entry_type_col = tk.Entry(frame)
entry_type_col.grid(row=3, column=1, padx=5, pady=5)
entry_type_col.insert(0, "TipoPeticion")  # Valor por defecto

tk.Label(frame, text="Nombre de la columna del módulo:").grid(row=4, column=0, sticky=tk.W)
entry_module_col = tk.Entry(frame)
entry_module_col.grid(row=4, column=1, padx=5, pady=5)
entry_module_col.insert(0, "Modulo")  # Valor por defecto

tk.Button(frame, text="Procesar", command=process_files, bg="green", fg="white").grid(row=5, column=0, columnspan=3, pady=10)

tk.Label(frame, text="Número del identificador:").grid(row=6, column=0, sticky=tk.W)
entry_id_selector = tk.Entry(frame)
entry_id_selector.grid(row=6, column=1, padx=5, pady=5)

# Añadir lista desplegable para seleccionar columna
tk.Label(frame, text="Selecciona una columna para mostrar:").grid(row=7, column=0, sticky=tk.W)
column_selector = ttk.Combobox(frame, state="readonly")
column_selector.grid(row=7, column=1, padx=5, pady=5)
tk.Button(frame, text="Mostrar", command=show_column).grid(row=7, column=2, padx=5, pady=5)

root.mainloop()
