import json
import tkinter as tk
from tkinter import filedialog, ttk


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

        self.treeview_frame = tk.Frame(self.main_root)
        self.treeview_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.treeview_frame, selectmode="browse")
        self.tree.pack(pady=10, fill=tk.BOTH, expand=True)

        self.message_label = tk.Label(self.main_root, text="", fg="red")
        self.message_label.pack(pady=10)

        self.style = ttk.Style()
        self.style.configure("Treeview", font=('Comic Sans MS', 10), foreground="white", background="#2D2A2E")
        self.style.configure("Treeview.Heading", font=('Arial', 12, 'bold'), foreground="blue", background="lightgray")
        self.style.configure("Treeview.Item", foreground="blue", background="white")
        self.style.map("Treeview", background=[('selected', 'lightblue')])

        self.style.configure("key", foreground="blue", font=('Comic Sans MS', 10, 'bold'))
        self.style.configure("value", foreground="blue", font=('Comic Sans MS', 20, 'bold'))

    def load_file(self):
        """Read and load JSON file"""
        if file_path := filedialog.askopenfilename(filetypes=[("Archivos JSON", "*.json")]):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    json_data = json.load(file)

                for item in self.tree.get_children():
                    self.tree.delete(item)

                self.display_json(json_data)
                self.message_label.config(text="JSON cargado exitosamente.", fg="green")

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

if __name__ == "__main__":
    root = tk.Tk()
    app = JsonValidatorApp(root)
    root.mainloop()
