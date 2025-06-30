import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import menu_interactivo_2 as db_logic
import re # Para validación de fecha
from PIL import Image, ImageTk
from datetime import datetime # Para validación de fecha

# Constantes para nombres de columnas (para asegurar consistencia)
COLUMN_NAMES_PRODUCTO = ["ID Producto", "Descripción", "Tipo", "Modelo", "Operador",
                         "No. Serie", "ICCID", "MAC", "Tecnología", "Propiedad",
                         "Estado", "Ruta Archivo", "Nombre Archivo"]
COLUMN_NAMES_MOVIMIENTOS = ["No. Movimiento", "ID Producto", "Cantidad", "ID Lote",
                            "ID Entorno", "Estado Post Movimiento"]

class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Inventario BD")
        self.root.geometry("900x700") # Tamaño inicial

        # Aplicar un tema de ttk si está disponible para mejorar la estética
        style = ttk.Style()
        available_themes = style.theme_names()
        # print(f"Available themes: {available_themes}") # Para depuración
        style.theme_use("vista")

        # --- Frames Principales ---
        # Frame para los botones de opciones (izquierda)
        options_outer_frame = ttk.Frame(self.root, padding="10")
        options_outer_frame.pack(side=tk.LEFT, fill=tk.Y)

        options_frame = ttk.LabelFrame(options_outer_frame, text="Menú de Opciones")
        options_frame.pack(expand=True, fill=tk.BOTH)

        # Frame para el área principal (entradas y resultados) (derecha)
        main_area_frame = ttk.Frame(self.root, padding="10")
        main_area_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        # Frame para entradas de parámetros (arriba en main_area_frame)
        self.input_frame = ttk.LabelFrame(main_area_frame, text="Parámetros de Consulta")
        self.input_frame.pack(fill=tk.X, pady=(0,10))

        # Frame para resultados (abajo en main_area_frame)
        results_frame = ttk.LabelFrame(main_area_frame, text="Resultados")
        results_frame.pack(expand=True, fill=tk.BOTH)

        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, state=tk.DISABLED, height=15)
        self.results_text.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        btn_clear_results = ttk.Button(results_frame, text="Limpiar Resultados", command=self.clear_results_area)
        btn_clear_results.pack(pady=5)

        # --- Botones de Opciones ---
        opciones = [
            ("1. Detalles Producto y Stock Lote", self.show_op1_inputs),
            ("2. Stock General Producto", self.show_op2_inputs),
            ("3. Stock Producto por Lote", self.show_op3_inputs),
            ("4. Stock Lote Específico", self.show_op4_inputs),
            ("5. Productos en Entorno", self.show_op5_inputs),
            ("6. Stock Todos los Productos", self.execute_op6_direct), # Sin inputs adicionales
            ("7. Contar Dispositivos Dañados", self.execute_op7_direct), # Sin inputs
            ("8. Entradas en un Día", self.show_op8_inputs),
            ("9. Salidas en un Día", self.show_op9_inputs),
            ("10. SIMs por Operador", self.show_op10_inputs),
            ("11. Total SIMs", self.execute_op11_direct), # Sin inputs
            ("12. Mostrar imagen del producto", self.mostrar_entrada_op12)
        ]

        for texto, comando in opciones:
            btn = ttk.Button(options_frame, text=texto, command=comando, width=30)
            btn.pack(pady=3, padx=5, fill=tk.X)

        # Botón de Salir
        btn_salir = ttk.Button(options_frame, text="Salir", command=self.root.quit)
        btn_salir.pack(pady=10, padx=5, fill=tk.X, side=tk.BOTTOM)

    def _clear_input_frame(self):
        for widget in self.input_frame.winfo_children():
            widget.destroy()

    def _display_results(self, content: str):
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, content)
        self.results_text.config(state=tk.DISABLED)
    
    def _mostrar_imagen(self, ruta_image):
        image = Image.open(ruta_image)
        image = image.resize((300, 300))  # Ajustar tamaño si es necesario
        image_tk = ImageTk.PhotoImage(image)  
        
        self.results_frame.config(image=image_tk)
        self.results_frame.image = image_tk  # Mantener referencia 


    def clear_results_area(self):
        self._display_results("")

    def _handle_db_call(self, func, *args):
        self.clear_results_area() # Limpiar antes de nueva consulta
        try:
            return func(*args)
        except db_logic.DatabaseError as e:
            messagebox.showerror("Error de Base de Datos", str(e))
            self._display_results(f"Error de Base de Datos:\n{e}")
            return None
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error inesperado: {e}")
            self._display_results(f"Error Inesperado:\n{e}")
            return None

    def _validate_date_format(self, date_string: str) -> bool:
        """Valida que el string de fecha esté en formato YYYY-MM-DD."""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date_string):
            return False
        try:
            datetime.strptime(date_string, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    # --- Funciones para configurar inputs y ejecutar acciones ---

    def show_op1_inputs(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="ID Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_op1_pid = ttk.Entry(self.input_frame, width=30)
        self.entry_op1_pid.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Consultar", command=self.execute_op1).grid(row=1, column=0, columnspan=2, pady=10)

    def execute_op1(self):
        pid = self.entry_op1_pid.get()
        if not pid:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese un ID de Producto.")
            return

        detalles_producto = self._handle_db_call(db_logic.obtener_detalles_producto, pid)
        if detalles_producto:
            resultado_str = "--- Detalles del Producto ---\n"
            for i, col_name in enumerate(COLUMN_NAMES_PRODUCTO):
                if i < len(detalles_producto):
                    resultado_str += f"{col_name}: {detalles_producto[i]}\n"

            resultado_str += "\n--- Stock por Lote (asociado al producto) ---\n"
            stock_lotes = self._handle_db_call(db_logic.obtener_stock_producto_desglosado_por_lote, pid)
            if stock_lotes:
                for id_lote, stock_lote_val in stock_lotes:
                    resultado_str += f"  Lote {id_lote}: {stock_lote_val}\n"
            else:
                resultado_str += "  No hay información de stock por lote para este producto o no tiene lotes con stock."
            self._display_results(resultado_str)
        elif detalles_producto is None and self.results_text.get(1.0, tk.END).strip() == "": # Solo si no hubo error previo de BD
             self._display_results(f"Producto con ID '{pid}' no encontrado.")

    def show_op2_inputs(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="ID Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_op2_pid = ttk.Entry(self.input_frame, width=30)
        self.entry_op2_pid.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Consultar", command=self.execute_op2).grid(row=1, column=0, columnspan=2, pady=10)

    def execute_op2(self):
        pid = self.entry_op2_pid.get()
        if not pid:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese un ID de Producto.")
            return

        # Verificar si el producto existe antes de obtener stock para dar mensaje más claro
        producto_existe = self._handle_db_call(db_logic.obtener_detalles_producto, pid)
        if producto_existe is None and self.results_text.get(1.0, tk.END).strip() == "":
             self._display_results(f"Producto con ID '{pid}' no encontrado.")
             return
        elif producto_existe is None: # Error de BD ya mostrado
            return

        stock = self._handle_db_call(db_logic.obtener_stock, pid)
        if stock is not None: # Puede ser 0, lo cual es válido
            self._display_results(f"Stock general actual del producto {pid}: {stock}")
        # Si stock es None, el error ya fue manejado por _handle_db_call

    def show_op3_inputs(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="ID Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_op3_pid = ttk.Entry(self.input_frame, width=30)
        self.entry_op3_pid.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Consultar", command=self.execute_op3).grid(row=1, column=0, columnspan=2, pady=10)

    def execute_op3(self):
        pid = self.entry_op3_pid.get()
        if not pid:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese un ID de Producto.")
            return

        producto_existe = self._handle_db_call(db_logic.obtener_detalles_producto, pid)
        if producto_existe is None and self.results_text.get(1.0, tk.END).strip() == "":
             self._display_results(f"Producto con ID '{pid}' no encontrado.")
             return
        elif producto_existe is None:
            return

        stock_por_lote = self._handle_db_call(db_logic.obtener_stock_producto_desglosado_por_lote, pid)
        if stock_por_lote:
            resultado_str = f"Stock desglosado por lote para el producto {pid}:\n"
            for id_lote, stock_lote_val in stock_por_lote:
                resultado_str += f"  Lote {id_lote}: {stock_lote_val}\n"
            self._display_results(resultado_str)
        elif isinstance(stock_por_lote, list) and not stock_por_lote: # Lista vacía, no error
            self._display_results(f"El producto {pid} existe, pero no tiene lotes con stock activo registrado.")
        # Si stock_por_lote es None, el error ya fue manejado

    def show_op4_inputs(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="ID Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_op4_pid = ttk.Entry(self.input_frame, width=30)
        self.entry_op4_pid.grid(row=0, column=1, padx=5, pady=5)
        ttk.Label(self.input_frame, text="ID Lote Proveedor:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_op4_lid = ttk.Entry(self.input_frame, width=30)
        self.entry_op4_lid.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Consultar", command=self.execute_op4).grid(row=2, column=0, columnspan=2, pady=10)

    def execute_op4(self):
        pid = self.entry_op4_pid.get()
        lid = self.entry_op4_lid.get()
        if not pid or not lid:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese ID de Producto e ID de Lote.")
            return

        producto_existe = self._handle_db_call(db_logic.obtener_detalles_producto, pid)
        if producto_existe is None and self.results_text.get(1.0, tk.END).strip() == "":
             self._display_results(f"Producto con ID '{pid}' no encontrado.")
             return
        elif producto_existe is None:
            return

        stock_lote_val = self._handle_db_call(db_logic.obtener_stock_producto_lote, pid, lid)
        if stock_lote_val is not None:
            self._display_results(f"Stock del lote '{lid}' para el producto '{pid}': {stock_lote_val}")

    def show_op5_inputs(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="ID Entorno:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_op5_eid = ttk.Entry(self.input_frame, width=30)
        self.entry_op5_eid.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Consultar", command=self.execute_op5).grid(row=1, column=0, columnspan=2, pady=10)

    def execute_op5(self):
        entorno_id = self.entry_op5_eid.get()
        if not entorno_id:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese un ID de Entorno.")
            return

        productos_en_entorno = self._handle_db_call(db_logic.producto_entorno, entorno_id)
        if productos_en_entorno:
            resultado_str = f"Productos presentes en el entorno {entorno_id}:\n"
            for p_info in productos_en_entorno:
                resultado_str += f"  ID Producto: {p_info[0]}\n" # p_info es una tupla con un solo elemento
            self._display_results(resultado_str)
        elif isinstance(productos_en_entorno, list) and not productos_en_entorno:
            self._display_results(f"No se encontraron productos en el entorno {entorno_id}, el entorno no existe o no tiene movimientos.")

    def execute_op6_direct(self): # No necesita show_inputs
        self._clear_input_frame() # Limpiar por si había algo
        stock_productos = self._handle_db_call(db_logic.obtener_stock_todos_productos)
        if stock_productos:
            resultado_str = "--- STOCK DE TODOS LOS PRODUCTOS ---\n"
            for id_p, nombre_p, stock_p in stock_productos:
                resultado_str += f"ID: {id_p}, Nombre: {nombre_p}, Stock: {stock_p}\n"
            self._display_results(resultado_str)
        elif isinstance(stock_productos, list) and not stock_productos:
             self._display_results("No hay productos en la base de datos o no se pudo obtener el stock.")

    def execute_op7_direct(self): # No necesita show_inputs
        self._clear_input_frame()
        total_dañados = self._handle_db_call(db_logic.cantidad_productos_dañados)
        if total_dañados is not None:
            self._display_results(f"Total de dispositivos (tipo 'DISPOSITIVO') en estado 'DAÑADO': {total_dañados}")

    def show_op8_inputs(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_op8_fecha = ttk.Entry(self.input_frame, width=30)
        self.entry_op8_fecha.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Consultar", command=self.execute_op8).grid(row=1, column=0, columnspan=2, pady=10)

    def execute_op8(self):
        fecha = self.entry_op8_fecha.get()
        if not fecha:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una fecha.")
            return
        if not self._validate_date_format(fecha):
            messagebox.showwarning("Formato Inválido", "El formato de fecha debe ser YYYY-MM-DD.")
            return

        detalles_entradas = self._handle_db_call(db_logic.obtener_detalles_entradas_en_un_dia, fecha)
        if detalles_entradas:
            resultado_str = f"--- Detalles de Entradas en {fecha} ---\n"
            for entrada in detalles_entradas:
                for i, col_name in enumerate(COLUMN_NAMES_MOVIMIENTOS):
                    resultado_str += f"  {col_name}: {entrada[i]}\n"
                resultado_str += "-" * 20 + "\n"
            self._display_results(resultado_str)
        elif isinstance(detalles_entradas, list) and not detalles_entradas:
            self._display_results(f"No se encontraron entradas para la fecha {fecha}.")

    def show_op9_inputs(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_op9_fecha = ttk.Entry(self.input_frame, width=30)
        self.entry_op9_fecha.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Consultar", command=self.execute_op9).grid(row=1, column=0, columnspan=2, pady=10)

    def execute_op9(self):
        fecha = self.entry_op9_fecha.get()
        if not fecha:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese una fecha.")
            return
        if not self._validate_date_format(fecha):
            messagebox.showwarning("Formato Inválido", "El formato de fecha debe ser YYYY-MM-DD.")
            return

        detalles_salidas = self._handle_db_call(db_logic.obtener_detalles_salidas_en_un_dia, fecha)
        if detalles_salidas:
            resultado_str = f"--- Detalles de Salidas en {fecha} ---\n"
            for salida in detalles_salidas:
                for i, col_name in enumerate(COLUMN_NAMES_MOVIMIENTOS):
                     resultado_str += f"  {col_name}: {salida[i]}\n"
                resultado_str += "-" * 20 + "\n"
            self._display_results(resultado_str)
        elif isinstance(detalles_salidas, list) and not detalles_salidas:
            self._display_results(f"No se encontraron salidas para la fecha {fecha}.")

    def show_op10_inputs(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="Nombre Operador:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_op10_operador = ttk.Entry(self.input_frame, width=30)
        self.entry_op10_operador.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Consultar", command=self.execute_op10).grid(row=1, column=0, columnspan=2, pady=10)

    def execute_op10(self):
        operador_nombre = self.entry_op10_operador.get()
        if not operador_nombre:
            messagebox.showwarning("Entrada Inválida", "Por favor, ingrese un nombre de operador.")
            return

        num_sim_operador = self._handle_db_call(db_logic.obtener_sim_de_operador, operador_nombre)
        if num_sim_operador is not None:
            self._display_results(f"Total de SIM cards (stock) del operador '{operador_nombre}': {num_sim_operador}")

    def execute_op11_direct(self): # No necesita show_inputs
        self._clear_input_frame()
        total_sims = self._handle_db_call(db_logic.obtener_sim_total)
        if total_sims is not None:
            self._display_results(f"Total de SIM cards (tipo 'SIM') registradas en la tabla producto: {total_sims}")

    def mostrar_entrada_op12(self):
        self._clear_input_frame()
        ttk.Label(self.input_frame, text="ID Producto:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_op12 = ttk.Entry(self.input_frame, width=30)
        self.entry_op12.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(self.input_frame, text="Consultar", command=self.ejecutar_op12).grid(row=1, column=0, columnspan=2, pady=10)

    def ejecutar_op12(self):
        id_imagen = self.entry_op12.get
        if not id_imagen:

            return 
        
        ruta_imagen = self._handle_db_call(db_logic.mostrar_ruta_imagen, id_imagen) 
        if ruta_imagen is not None: 
            image = Image.open(ruta_imagen)
            image = image.resize((300, 300))
            image_tk = ImageTk.PhotoImage()  
            self.results_frame.config(image=image_tk)
            self.results_frame.image = image_tk  # Mantener referencia

if __name__ == "__main__":
    # Test de conexión inicial para feedback temprano si la BD no está accesible
    try:
        # Intentar una conexión simple para ver si la BD está arriba
        # Esto no es parte de db_logic.conexion_BD() para no acoplarlo tanto al inicio
        conn_test = db_logic.mysql.connector.connect(
            host=db_logic.DB_HOST,
            user=db_logic.DB_USER,
            password=db_logic.DB_PASSWORD,
            database=db_logic.DB_NAME,
            connection_timeout=5 # Timeout corto
        )
        conn_test.close()

        app_root = tk.Tk()
        app = InventarioApp(app_root)
        app_root.mainloop()

    except db_logic.mysql.connector.Error as err:
        # Crear una ventana raíz temporal solo para mostrar el error si la conexión inicial falla
        error_root = tk.Tk()
        error_root.withdraw() # Ocultar la ventana principal vacía
        messagebox.showerror("Error Crítico de Conexión",
                             f"No se pudo conectar a la base de datos '{db_logic.DB_NAME}' en {db_logic.DB_HOST}.\n"
                             f"Verifique que el servidor MySQL esté en ejecución y las credenciales sean correctas.\n\n"
                             f"Detalle: {err}")
        error_root.destroy()
    except Exception as e:
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("Error Inesperado al Iniciar",
                             f"Ocurrió un error inesperado al iniciar la aplicación: {e}")
        error_root.destroy()
