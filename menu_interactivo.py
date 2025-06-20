import mysql.connector
from typing import List, Tuple, Any, Optional

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
            print("Conexión cerrada.")

def obtener_detalles_producto(product_id: str) -> Optional[Tuple[Any, ...]]:
    query = "SELECT * FROM producto WHERE id_producto = %s"
    resultado = ejecutar_query(query, (product_id,))
    if resultado and len(resultado) > 0:
        return resultado[0] 
    return None

def obtener_stock(product_id: str) -> int:
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

def producto_entorno(id_entorno: str) -> List[Tuple[Any, ...]]:
    query = """
    SELECT DISTINCT id_producto 
    FROM movimiento_kardex 
    WHERE id_entorno = %s;
    """
    resultado = ejecutar_query(query, (id_entorno,))
    if resultado is None:
        return []
    return resultado

def cantidad_productos_dañados() -> int:
    sql_query = "SELECT COUNT(*) FROM producto WHERE tipo = 'DISPOSITIVO' AND estado = 'DAÑADO';"
    resultado = ejecutar_query(sql_query)
    if resultado and resultado[0] and resultado[0][0] is not None:
        return int(resultado[0][0])
    return 0

def entradas_en_un_dia(specific_date: str) -> int:
    sql_query = "SELECT COUNT(*) FROM movimiento_kardex WHERE tipo_movimiento = 'ENTRADA' AND fecha = %s;"
    resultado = ejecutar_query(sql_query, params=(specific_date,))
    if resultado and resultado[0] and resultado[0][0] is not None:
        return int(resultado[0][0])
    return 0

def obtener_sim_total() -> int:
    sql_query = "SELECT COUNT(*) FROM producto WHERE tipo = 'SIM';"
    resultado = ejecutar_query(sql_query)
    if resultado and resultado[0] and resultado[0][0] is not None:
        return int(resultado[0][0])
    return 0

def obtener_sim_de_operador(operator_name: str) -> int:
    sql_query = "SELECT COUNT(*) FROM producto WHERE tipo = 'SIM' AND operador = %s;"
    resultado = ejecutar_query(sql_query, params=(operator_name,))
    if resultado and resultado[0] and resultado[0][0] is not None:
        return int(resultado[0][0])
    return 0

if __name__ == "__main__":
    while True:
        print("\n--- MENÚ PRINCIPAL ---")
        print("1. Ver detalles de un producto")
        print("2. Ver stock actual de un producto")
        print("3. Ver productos en un entorno")
        print("4. Contar dispositivos dañados")
        print("5. Contar entradas en una fecha específica")
        print("6. Contar SIM cards totales")
        print("7. Contar SIM cards por operador")
        opcion = input("Seleccione una opción (1-7): ")
        if opcion == "1":
            pid = input("Ingrese ID del producto: ")
            resultado = obtener_detalles_producto(pid)
            print(resultado if resultado else "Producto no encontrado.")
        elif opcion == "2":
            pid = input("Ingrese ID del producto: ")
            stock = obtener_stock(pid)
            print(f"Stock actual: {stock}")
        elif opcion == "3":
            entorno = input("Ingrese ID del entorno: ")
            productos = producto_entorno(entorno)
            for p in productos:
                print(p[0])
        elif opcion == "4":
            total = cantidad_productos_dañados()
            print(f"Dispositivos dañados: {total}")
        elif opcion == "5":
            fecha = input("Ingrese la fecha (YYYY-MM-DD): ")
            entradas = entradas_en_un_dia(fecha)
            print(f"Entradas en {fecha}: {entradas}")
        elif opcion == "6":
            total = obtener_sim_total()
            print(f"Total de SIM cards: {total}")
        elif opcion == "7":
            operador = input("Ingrese nombre del operador: ")
            cantidad = obtener_sim_de_operador(operador)
            print(f"SIMs de {operador}: {cantidad}")
        else:
            print("Opción no válida. Intente nuevamente.")
            break
        continuar= input("¿Desea realizar más consultas? s/n: ")
        if continuar.lower()== "s":
            print("Entendido.")
        else:
            print("Gracias por usar el programa :)")
            break