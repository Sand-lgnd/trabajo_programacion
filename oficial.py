import mysql.connector
from typing import List, Tuple, Any, Optional
import os
from PIL import Image

def conexion_BD():
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Pata2021.",
            database="BD_proyecto"
        )
        return conexion
    except mysql.connector.Error as err:
        print(f"Conexión con la BD fallida: {err}")
        return None

def ejecutar_query(query_string: str, params: Optional[tuple] = None) -> Optional[List[Tuple[Any, ...]]]:
    conexion = None
    try:
        conexion = conexion_BD()
        if conexion is None:
            return None

        cursor = conexion.cursor()
        cursor.execute(query_string, params)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Error al ejecutar el query: {err}\nQuery: {query_string}\nParams: {params}")
        return None
    finally:
        if conexion and conexion.is_connected():
            cursor.close()
            conexion.close()

def obtener_detalles_producto(product_id: str) -> Optional[Tuple[Any, ...]]: # DEVUELVE LOS DETALLES DE UN PRODUCTO
    query = "SELECT * FROM producto WHERE id_producto = %s"
    resultado = ejecutar_query(query, (product_id,))
    if resultado and len(resultado) > 0:
        return resultado[0] 
    return None

def obtener_stock(product_id: str) -> int: #CALCULA EL STOCK EN GENERAL DE UN PRODUCTO EN ESPECIFICO
    query = """
    SELECT SUM(CASE tipo_movimiento 
                  WHEN 'ENTRADA' THEN cantidad 
                  WHEN 'SALIDA' THEN -cantidad 
                  ELSE 0 
               END) as stock_actual
    FROM movimiento_kardex 
    WHERE id_producto = %s;
    """
    resultado = ejecutar_query(query, (product_id,))
    if resultado and resultado[0] and resultado[0][0] is not None:
        return int(resultado[0][0])
    return 0

def obtener_stock_producto_lote(id_producto_especifico: str, id_lote: str, id_entorno) -> int:# Calcula el stock de un lote de un producto en especÍfico 
    query = """
    SELECT SUM(CASE tipo_movimiento
                  WHEN 'ENTRADA' THEN cantidad
                  WHEN 'SALIDA' THEN -cantidad
                  ELSE 0
               END) as stock_del_lote_producto
    FROM movimiento_kardex
    WHERE id_producto = %s AND id_lote = %s AND id_entorno =%s;
    """
    resultado = ejecutar_query(query, (id_producto_especifico, id_lote, id_entorno))
    if resultado and resultado[0] and resultado[0][0] is not None:
        return int(resultado[0][0])
    return 0

def producto_entorno(id_entorno: str) -> List[Tuple[Any, ...]]:
    query = """
    SELECT mk.id_producto, mk.estado_post_movimiento
    FROM movimiento_kardex mk
    INNER JOIN (
        SELECT id_producto, MAX(num_movimiento) as max_mov
        FROM movimiento_kardex
        WHERE id_entorno = %s
        GROUP BY id_producto
    ) as latest_mov 
    ON mk.id_producto = latest_mov.id_producto AND mk.num_movimiento = latest_mov.max_mov
    WHERE mk.id_entorno = %s;
    """
    resultado = ejecutar_query(query, (id_entorno, id_entorno))
    if resultado is None:
        return []
    return resultado

def obtener_stock_producto_desglosado_por_lote(product_id: str) -> List[Tuple[str, int]]: 
    query = """
    SELECT id_lote, SUM(CASE tipo_movimiento
                           WHEN 'ENTRADA' THEN cantidad
                           WHEN 'SALIDA' THEN -cantidad
                           ELSE 0
                        END) as stock_del_lote
    FROM movimiento_kardex
    WHERE id_producto = %s 
    GROUP BY id_lote;
    """
    resultados = ejecutar_query(query, (product_id,))
    if resultados:
        return [(str(id_lote), int(stock)) for id_lote, stock in resultados]
    return []

def cantidad_productos_dañados() -> int: 
    sql_query = "SELECT COUNT(*) FROM movimiento_kardex WHERE estado_post_movimiento = 'DAÑADO';"
    resultado = ejecutar_query(sql_query)
    if resultado and resultado[0] and resultado[0][0] is not None:
        return int(resultado[0][0])
    return 0

def obtener_sim_total(): # Esta función ahora calcula el STOCK de SIMs en total.
    sql_query = """
    SELECT SUM(CASE mk.tipo_movimiento
              WHEN 'ENTRADA' THEN mk.cantidad
              WHEN 'SALIDA' THEN -mk.cantidad
              ELSE 0
           END) AS stock_total_sim
    FROM producto p
    LEFT JOIN lote l ON p.id_producto = l.id_producto
    LEFT JOIN movimiento_kardex mk ON l.id_lote = mk.id_lote
    WHERE p.tipo = 'SIM';
    """
    resultado = ejecutar_query(sql_query)
    if resultado and resultado[0] and resultado[0][0] is not None:
        return int(resultado[0][0])
    return

def obtener_sim_de_operador(operator_name: str): # Esta función ahora calcula el STOCK de SIMs de un operador, basado en los movimientos de entrada/salida.
    sql_query = """
    SELECT SUM(CASE mk.tipo_movimiento
              WHEN 'ENTRADA' THEN mk.cantidad
              WHEN 'SALIDA' THEN -mk.cantidad
              ELSE 0
           END) AS stock_total_sim
    FROM producto p
    LEFT JOIN lote l ON p.id_producto = l.id_producto
    LEFT JOIN movimiento_kardex mk ON l.id_lote = mk.id_lote
    WHERE p.tipo = 'SIM' AND p.operador = %s;
    """
    resultado = ejecutar_query(sql_query, params=(operator_name,))
    if resultado and resultado[0] and resultado[0][0] is not None:
        return int(resultado[0][0])
    return 0 # Devuelve 0 si no hay stock o el operador no tiene SIMs con movimientos

def obtener_detalles_entradas_en_un_dia(specific_date: str) -> List[Tuple[Any, ...]]:
    query = """
    SELECT num_movimiento, id_producto, cantidad, id_lote, id_entorno, estado_post_movimiento
    FROM movimiento_kardex
    WHERE tipo_movimiento = 'ENTRADA' AND fecha = %s;
    """
    resultados = ejecutar_query(query, (specific_date,))
    if resultados:
        return resultados
    return []

def obtener_detalles_salidas_en_un_dia(specific_date: str) -> List[Tuple[Any, ...]]:
    query = """
    SELECT num_movimiento, id_producto, cantidad, id_lote, id_entorno, estado_post_movimiento
    FROM movimiento_kardex
    WHERE tipo_movimiento = 'SALIDA' AND fecha = %s;
    """
    resultados = ejecutar_query(query, (specific_date,))
    if resultados:
        return resultados
    return []

def obtener_stock_todos_productos(): #CALCULA EL STOCK EN GENERAL DE TODOS LOS PRODUCTOS
    query_productos = "SELECT id_producto, nombre FROM producto;"
    productos = ejecutar_query(query_productos)
    
    if not productos:
        return []
        
    stock_total = []
    for id_producto, nombre_producto in productos:
        stock = obtener_stock(id_producto)
        stock_total.append((id_producto, nombre_producto, stock))
        
    return stock_total

def mostrar_imagen(id_imagen):
    conexion = conexion_BD()
    cursor = conexion.cursor()

    cursor.execute("SELECT ruta FROM producto WHERE id_producto = %s", (id_imagen,))
    resultado = cursor.fetchone()

    if resultado:
        ruta_imagen = resultado[0]
        if os.path.exists(ruta_imagen):
            img = Image.open(ruta_imagen)
            img.show()
        else:
            print("⚠️  La imagen ya no existe en el disco.")
    else:
        print("⚠️  No se encontró esa imagen.")

    cursor.close()
    conexion.close()

def mostrar_ruta_imagen(id_imagen:str):
    query = "SELECT ruta FROM producto WHERE id_producto = %s"
    resultado = ejecutar_query(query, id_imagen)
    return resultado

if __name__ == "__main__":
    column_names_producto = ["ID Producto", "Descripción", "Tipo", "Modelo", "Operador", "No. Serie", "ICCID", "MAC", "Tecnología", "Propiedad", 
                             "Estado", "Ruta Archivo", "Nombre Archivo"]
    column_names_movimientos = ["No. Movimiento", "ID Producto", "Cantidad", "ID Lote", "ID Entorno", "Estado Post Movimiento"]
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Ver detalles de un producto (incluye stock por lote)")
        print("2. Ver stock general de un producto")
        print("3. Ver stock de un producto desglosado por lote")
        print("4. Ver stock de un lote específico")
        print("5. Ver productos en un entorno de almacenamiento")
        print("6. Ver stock actual de todos los productos") 
        print("7. Contar dispositivos dañados") 
        print("8. Consultar entradas en un día específico") 
        print("9. Consultar salidas de un día específico")
        print("10. Contar SIM cards por operador") 
        print("11. Contar SIM cards totales") 
        print("12. Mostrar imagen de producto")
        
        opcion_valida = False
        opcion = input("Seleccione una opción (1-12): ")

        if opcion == "1":
            opcion_valida = True
            pid = input("Ingrese ID del producto: ")
            detalles_producto = obtener_detalles_producto(pid)
            if detalles_producto:
                print("--- Detalles del Producto ---")
                for i, col_name in enumerate(column_names_producto):
                    if i < len(detalles_producto):
                         print(f"{col_name}: {detalles_producto[i]}")

                print("\n--- Stock por Lote (asociado al producto) ---")
                stock_lotes = obtener_stock_producto_desglosado_por_lote(pid)
                if stock_lotes:
                    for id_lote, stock_lote_val in stock_lotes:
                        print(f"  Lote {id_lote}: {stock_lote_val}")
                else:
                    print("  No hay información de stock por lote para este producto, o el producto no tiene lotes con stock registrado.")
            else:
                print(f"Producto con ID '{pid}' no encontrado.")

        elif opcion == "2":
            opcion_valida = True
            pid = input("Ingrese ID del producto: ")
            if obtener_detalles_producto(pid):
                stock = obtener_stock(pid)
                print(f"Stock general actual del producto {pid}: {stock}")
            else:
                print(f"Producto con ID '{pid}' no encontrado.")

        elif opcion == "3": 
            opcion_valida = True
            pid = input("Ingrese ID del producto para ver stock desglosado por lote: ")

            if obtener_detalles_producto(pid): 
                stock_por_lote = obtener_stock_producto_desglosado_por_lote(pid)
                if stock_por_lote:
                    print(f"Stock desglosado por lote para el producto {pid}:")
                    for id_lote, stock_lote_val in stock_por_lote:
                        print(f"  Lote {id_lote}: {stock_lote_val}")
                else:
                    print(f"El producto {pid} existe, pero no tiene lotes con stock activo registrado.")
            else:
                print(f"Producto con ID '{pid}' no encontrado.")

        elif opcion == "4": # Ver stock de un lote específico para un producto
            opcion_valida = True
            pid = input("Ingrese ID del producto: ") 
            lid = input("Ingrese el código de lote del proveedor: ") 
            eid = input("Ingrese el ID del entorno: ")
            if obtener_detalles_producto(pid):
                stock_lote_val = obtener_stock_producto_lote(pid, lid, eid)
                print(f"Stock del lote '{lid}' para el producto '{pid}': {stock_lote_val} en el entorno: {eid} "  )
            else:
                print("Hubo un fallo con uno de los ID ingresados")

        elif opcion == "5": 
            opcion_valida = True
            entorno_id = input("Ingrese ID del entorno de almacenamiento: ") 
            productos_en_entorno = producto_entorno(entorno_id)
            if productos_en_entorno:
                print(f"Productos presentes en el entorno {entorno_id}:")
                for p_info in productos_en_entorno: 
                    print(f"  ID Producto: {p_info[0]}") 
            else:
                print(f"No se encontraron productos en el entorno {entorno_id}, el entorno no existe, o no tiene movimientos registrados.")
        
        elif opcion == "6": 
            opcion_valida = True
            stock_productos = obtener_stock_todos_productos()
            if stock_productos:
                print("\n--- STOCK DE TODOS LOS PRODUCTOS ---")
                for id_p, nombre_p, stock_p in stock_productos:
                    print(f"ID: {id_p}, Nombre: {nombre_p}, Stock: {stock_p}")
            else:
                print("No se pudo obtener el stock de los productos.")

        elif opcion == "7": 
            opcion_valida = True
            total_dañados = cantidad_productos_dañados()
            print(f"Total de dispositivos (tipo 'DISPOSITIVO') en estado 'DAÑADO': {total_dañados}")

        elif opcion == "8": 
            opcion_valida = True
            fecha = input("Ingrese la fecha (YYYY-MM-DD) para ver detalles de entradas: ")
            detalles_entradas = obtener_detalles_entradas_en_un_dia(fecha)
            if detalles_entradas:
                print(f"\n--- Detalles de Entradas en {fecha} ---")
                for entrada in detalles_entradas:
                    for i, col_name in enumerate(column_names_movimientos): 
                        print(f"  {col_name}: {entrada[i]}")
                    print("-" * 20)
            else:
                print(f"No se encontraron entradas para la fecha {fecha}.")

        elif opcion == "9": # Antigua opción 6 - Consultar salidas de un día específico
            opcion_valida = True
            fecha = input("Ingrese la fecha (YYYY-MM-DD) para ver detalles de salidas: ")
            detalles_salidas = obtener_detalles_salidas_en_un_dia(fecha)
            if detalles_salidas:
                print(f"\n--- Detalles de Salidas en {fecha} ---")
                for salida in detalles_salidas:
                    for i, col_name in enumerate(column_names_movimientos): # Reutilizamos column_names_movimientos
                        print(f"  {col_name}: {salida[i]}")
                    print("-" * 20)
            else:
                print(f"No se encontraron salidas para la fecha {fecha}.")
            
        elif opcion == "10": # Antigua opción 7
            opcion_valida = True
            operador_nombre = input("Ingrese nombre del operador para contar sus SIM cards: ")
            num_sim_operador = obtener_sim_de_operador(operador_nombre)
            print(f"Total de SIM cards del operador '{operador_nombre}': {num_sim_operador}")

        elif opcion == "11": # Antigua opción 8
            opcion_valida = True
            total_sims = obtener_sim_total()
            print(f"Total de SIM cards (tipo 'SIM') en inventario: {total_sims}")
        
        elif opcion == "12":
            opcion_valida = True
            try:
                id_img = input("ID del prodcuto a mostrar: ")
                mostrar_imagen(id_img)
            except ValueError:
                print("❌ ID inválido.")

        else:
            print("Opción no válida. Por favor, intente nuevamente.")
        
        if opcion_valida:
            continuar_input = input("¿Desea realizar más consultas? (s para si o cualquier letra para no): ")
            if continuar_input.lower() != 's':
                print("Gracias por usar el programa :)")
                break
        # Si la opción no fue válida, el bucle continúa