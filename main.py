import json
import tkinter as tk
from tkinter import ttk, filedialog

from json_validator import JsonValidator


class JsonValidatorApp:
    """Rendering application class."""
    def __init__(self, main_root):
        self.main_root = main_root
        self.sc_width = self.main_root.winfo_screenwidth()
        self.sc_height = self.main_root.winfo_screenheight()

        self.win_width = int(self.sc_width * 0.6)
        self.win_height = int(self.sc_height * 0.6)
        self.x_axis = (self.sc_width // 2) - (self.win_width // 2)
        self.y_axis = (self.sc_height // 2) - (self.win_height // 2)

        self.main_root.geometry(f"{self.win_width}x{self.win_height}+{self.x_axis}+{self.y_axis}")
        self.main_root.title("Validador JSON")
        self.load_button = tk.Button(self.main_root, text="Cargar archivo JSON", command=self.load_file)
        self.load_button.pack(pady=20)

        # Sección para mostrar los errores de validación usando Treeview
        self.error_section_frame = tk.Frame(self.main_root)
        self.error_section_frame.pack(pady=20, fill=tk.BOTH, expand=True)

        # Crear un widget Treeview para mostrar los errores
        self.error_tree = ttk.Treeview(self.error_section_frame, columns=("Tipo de Error", "Mensaje"), show="headings")
        self.error_tree.pack(pady=10, fill=tk.BOTH, expand=True)

        # Configuración de las columnas
        # self.error_tree.heading("Función", text="Función", anchor="w")
        self.error_tree.heading("Tipo de Error", text="Tipo de Error", anchor="w")
        self.error_tree.heading("Mensaje", text="Mensaje", anchor="w")

        # self.error_tree.column("Función", width=150)
        self.error_tree.column("Tipo de Error", width=150)
        self.error_tree.column("Mensaje", width=500, stretch=tk.YES)

        self.style = ttk.Style()
        self.style.configure("Treeview", font=('Comic Sans MS', 10), foreground="#FDFCFA", background="#2D2A2E") #2D2A2E f4f8ff
        self.style.configure("Treeview.Heading", font=('Arial', 12, 'bold'), foreground="red", background="lightgray")
        self.style.configure("Treeview.Item", foreground="red", background="#FDFCFA")
        self.style.map("Treeview", background=[('selected', 'lightblue')])

        # Crear el Treeview para el JSON (este es el que se usa para visualizar el JSON cargado)
        self.treeview_frame = tk.Frame(self.main_root)
        self.treeview_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.treeview_frame, selectmode="browse")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.json_data = None

    def load_file(self):
        """Read and load JSON file"""
        # Aquí usas un archivo local de ejemplo, puedes reemplazar con filedialog si prefieres
        # file_path = "/Users/carlos/Downloads/demo 1.json"
        file_path = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
        if file_path:  # Verifica que el archivo ha sido seleccionado
            try:
                # Limpiar errores anteriores
                self.clear_errors()
                for item in self.tree.get_children():
                    self.tree.delete(item)  # Limpiar el Treeview del JSON anterior

                # Leer el nuevo archivo
                with open(file_path, "r", encoding="utf-8") as file:
                    json_data = json.load(file)
                    self.json_data = json_data

                # Mostrar el nuevo JSON en el Treeview
                self.display_json(self.json_data)

                # Validar el nuevo JSON
                validator = JsonValidator(json_report=self.json_data)
                validator.set_json()
                validator.validate_json()

                # Obtener y mostrar los errores en el Treeview de errores
                print(len(validator.get_errors()))
                self.display_errors(validator.get_errors())

            except json.JSONDecodeError as e:
                self.message_label.config(text=f"Error al cargar el archivo: {e}", fg="red")

    def display_json(self, data, parent=""):
        """Display json data in tk window."""
        if isinstance(data, dict):
            for key, value in data.items():
                item_id = self.tree.insert(parent, "end", text=key, open=True)
                self.display_json(value, parent=item_id)

        elif isinstance(data, list):
            for idx, item in enumerate(data):
                item_id = self.tree.insert(parent, "end", text=f"[{idx}]", open=True)
                self.display_json(item, parent=item_id)

        else:
            self.tree.insert(parent, "end", text=str(data), open=False)

    def display_errors(self, errors):
        """Display errors in the error section."""
        # Limpiar los errores previos
        for item in self.error_tree.get_children():
            self.error_tree.delete(item)

        # Función recursiva para manejar errores anidados
        def process_error(error, parent=""):
            if isinstance(error, dict):
                # Solo mostramos el 'type_error' y 'error' que son los que quieres ver
                type_error = error.get('type_error', 'Desconocido')
                msg = error.get('error', 'Sin mensaje')
                # Insertamos solo el tipo de error y el mensaje
                self.error_tree.insert(parent, 'end', values=(type_error, msg))
            elif isinstance(error, list):
                # Si el error es una lista, recorremos cada item
                for sub_error in error:
                    process_error(sub_error, parent)
            else:
                # Si es un error simple (no diccionario ni lista), lo mostramos directamente
                self.error_tree.insert(parent, 'end', values=("Error", str(error)))

        # Procesamos la lista de errores
        for error in errors:
            process_error(error)

    def adjust_text_in_treeview(self):
        """Ajusta el texto largo en el Treeview utilizando un widget Text para el "Mensaje"""
        for item in self.error_tree.get_children():
            values = self.error_tree.item(item, "values")
            if len(values) > 2:  # Aseguramos que la fila tenga valores (Función, Tipo de Error, Mensaje)
                msg = values[2]  # Accedemos a "Mensaje"
                if len(msg) > 50:  # Si el texto es muy largo
                    # Crear un Text widget para el mensaje largo
                    text_widget = tk.Text(self.main_root, wrap=tk.WORD, height=3, width=70)
                    text_widget.insert(tk.END, msg)
                    text_widget.config(state=tk.DISABLED)
                    # Agregar el widget de texto debajo del Treeview en la interfaz
                    text_widget.pack(pady=5)
                    # Enlazamos el widget Text con el item
                    self.error_tree.item(item, values=(values[0], values[1], ""))  # Limpiamos el valor actual

    def clear_errors(self):
        """Limpiar los errores del Treeview de errores"""
        for item in self.error_tree.get_children():
            self.error_tree.delete(item)

    def get_json(self) -> dict:
        return self.json_data


if __name__ == "__main__":
    root = tk.Tk()
    app = JsonValidatorApp(root)
    app.load_file()
    root.mainloop()

# TODO
# Lineas a descomentar para cargar un archivo instantaneamente
        # file_path = "/Users/carlos/Downloads/demo 1.json"
        # app.load_file()

# Lineas a cdomentar para cargar un archivo instantaneamente
        # file_path = filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")])
