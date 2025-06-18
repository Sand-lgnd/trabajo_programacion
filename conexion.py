import mysql.connector
from typing import List, Tuple, Any, Optional, Union

def get_db_connection() -> Optional[mysql.connector.MySQLConnection]:
    """Establishes and returns a database connection.

    Attempts to connect to the MySQL database using predefined credentials
    and connection details.

    :return: A MySQLConnection object if the connection is successful,
             otherwise None.
    :rtype: Optional[mysql.connector.MySQLConnection]
    """
    try:
        connection = mysql.connector.connect(
            host="localhost",  # O dirección IP del servidor
            user="root",
            password="Pata2021.",
            database="BD_proyecto"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Database connection failed: {err}")
        return None

def execute_query(query_string: str, params: Optional[tuple] = None) -> Optional[List[Tuple[Any, ...]]]:
    """Executes a SQL query and returns the results.

    This function handles obtaining a database connection, creating a cursor,
    executing the provided SQL query (with optional parameters to prevent
    SQL injection), fetching all results, and then closing the cursor and
    connection. Errors during connection or execution are caught, and a
    message is printed.

    :param query_string: The SQL query string to be executed.
    :type query_string: str
    :param params: A tuple of parameters to be substituted into the query_string.
                   Defaults to None if no parameters are needed.
    :type params: Optional[tuple]
    :return: A list of tuples, where each tuple represents a row from the
             query results. Returns None if a database connection error or
             query execution error occurs.
    :rtype: Optional[List[Tuple[Any, ...]]]
    """
    connection = None
    try:
        connection = get_db_connection()
        if connection is None:
            # get_db_connection already printed an error, so just return None
            return None

        cursor = connection.cursor()
        cursor.execute(query_string, params)
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        # Consider security implications of printing query_string in a real app
        print(f"Error executing query: {err}\nQuery: {query_string}\nParams: {params}")
        return None
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("✅ Connection closed.")

def get_product_details(product_id: str) -> Optional[Tuple[Any, ...]]:
    """Retrieves product details for a given product_id.

    Constructs and executes a SQL query to select all information for a
    specific product from the 'producto' table.

    :param product_id: The unique identifier of the product.
    :type product_id: str
    :return: A tuple representing the product's details if found,
             otherwise None (if product not found or an error occurs).
    :rtype: Optional[Tuple[Any, ...]]
    """
    query = "SELECT * FROM producto WHERE id_producto = %s"
    results = execute_query(query, (product_id,))
    # Return None if results is None (error) or empty (not found)
    if results and len(results) > 0:
        return results[0]
    return None

def get_current_stock(product_id: str) -> int:
    """Calculates the net stock for a given product_id from movimiento_kardex.

    The query sums the 'cantidad' from 'movimiento_kardex', treating 'ENTRADA'
    movements as positive and 'SALIDA' movements as negative, filtered by
    the 'id_producto'.

    :param product_id: The unique identifier of the product.
    :type product_id: str
    :return: The calculated net stock as an integer. Returns 0 if the
             product is not found, has no movements, or if an error occurs
             during query execution.
    :rtype: int
    """
    query = """
    SELECT SUM(CASE tipo_movimiento
                  WHEN 'ENTRADA' THEN cantidad
                  WHEN 'SALIDA' THEN -cantidad
                  ELSE 0
               END) as stock_actual
    FROM movimiento_kardex
    WHERE id_producto = %s;
    """
    results = execute_query(query, (product_id,))
    # If query fails (None) or product has no movements (empty list or (None,)), return 0
    if results and results[0] and results[0][0] is not None:
        return int(results[0][0])
    # Handles execute_query returning None or empty results for the product
    return 0

def get_product_expirations(days_ahead: int) -> List[Tuple[Any, ...]]:
    """Finds products expiring within a given number of days from the current date.

    Constructs a SQL query to select products from the 'lote' table whose
    'fecha_vencimiento' (expiration date) is between the current date and
    the current date plus 'days_ahead'.

    :param days_ahead: The number of days from the current date to check for
                       expiring products.
    :type days_ahead: int
    :return: A list of tuples, where each tuple contains details of an
             expiring lot (id_lote, id_producto, fecha_vencimiento, cantidad).
             Returns an empty list if no products are expiring within the
             specified timeframe or if an error occurs.
    :rtype: List[Tuple[Any, ...]]
    """
    query = """
    SELECT id_lote, id_producto, fecha_vencimiento, cantidad
    FROM lote
    WHERE fecha_vencimiento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY);
    """
    results = execute_query(query, (days_ahead,))
    if results is None: # Error in execute_query
        return [] # Return empty list as per requirement
    return results # Return the list of results (can be empty if no matching data)

def get_products_in_environment(environment_id: str) -> List[Tuple[Any, ...]]:
    """Lists distinct products that have been in a specific environment.

    This version executes a simplified query to find all distinct product IDs
    that have at least one entry in the 'movimiento_kardex' table associated
    with the given 'id_entorno'.
    A more complex query (commented out in the function body) would be needed
    to determine products *currently* in the environment based on their last
    movement.

    :param environment_id: The unique identifier of the environment.
    :type environment_id: str
    :return: A list of tuples, where each tuple contains a distinct 'id_producto'.
             Returns an empty list if no products are found for the environment
             or if an error occurs.
    :rtype: List[Tuple[Any, ...]]
    """
    # This is a simplified version. A more complex query (commented out in the
    # function body) would be needed to find only products *currently* in the
    # environment based on the last movement.
    query = """
    SELECT DISTINCT id_producto
    FROM movimiento_kardex
    WHERE id_entorno = %s;
    """
    # To get more details like last state:
    # query = """
    # SELECT mk.id_producto, mk.estado_post_movimiento
    # FROM movimiento_kardex mk
    # INNER JOIN (
    #     SELECT id_producto, MAX(num_movimiento) as max_mov
    #     FROM movimiento_kardex
    #     WHERE id_entorno = %s
    #     GROUP BY id_producto
    # ) as latest_mov ON mk.id_producto = latest_mov.id_producto AND mk.num_movimiento = latest_mov.max_mov
    # WHERE mk.id_entorno = %s;
    # """
    results = execute_query(query, (environment_id,))
    if results is None: # Error in execute_query
        return [] # Return empty list as per requirement
    return results # Return the list of results (can be empty if no matching data)

if __name__ == "__main__":
    # print("Attempting to execute query...")
    # # Example usage:
    # query = "SELECT * FROM producto;"
    # results = execute_query(query)

    # if results:
    #     print("Query results:")
    #     for row in results:
    #         print(row)
    # else:
    #     print("No results obtained or an error occurred.")

    # --- Example calls for new functions ---
    # print("\n--- Testing get_product_details ---")
    # product_details = get_product_details(1) # Assuming product_id 1 exists
    # if product_details:
    #     print(f"Details for product 1: {product_details}")
    # else:
    #     print("Product 1 not found.")

    # print("\n--- Testing get_current_stock ---")
    # stock_product_1 = get_current_stock(1) # Assuming product_id 1 exists
    # print(f"Current stock for product 1: {stock_product_1}")

    # print("\n--- Testing get_product_expirations ---")
    # # Find products expiring in the next 30 days
    # expiring_soon = get_product_expirations(30)
    # if expiring_soon:
    #     print(f"Products expiring in the next 30 days: {expiring_soon}")
    # else:
    #     print("No products expiring soon or error.")

    # print("\n--- Testing get_products_in_environment ---")
    # # Find products in environment 101
    # products_in_env = get_products_in_environment(101) # Assuming environment_id 101 exists
    # if products_in_env:
    #     print(f"Products in environment 101: {products_in_env}")
    # else:
    #     print("No products found in environment 101 or error.")
    # pass # Keep the script runnable but without direct output for now

    print("--- Starting example function calls ---")

    # --- Test get_product_details ---
    print("\n" + "-" * 20)
    print("Testing get_product_details...")
    product_id_to_test = 'DS0001' # Example Product ID
    product_id_to_test = 'DS0001' # Example Product ID
    product_details = get_product_details(product_id_to_test)
    if product_details is not None: # Check for None explicitly due to new error handling
        # Assuming the producto table has columns like:
        # id_producto, nombre_producto, descripcion, id_categoria, precio_unitario, unidad_medida
        # Adjust indices based on your actual table structure
        print(f"Details for product {product_id_to_test}:")
        # Check for sufficient length, as product_details is a tuple
        if len(product_details) >= 6:
            print(f"  Product ID: {product_details[0]}")
            print(f"  Name: {product_details[1]}")
            print(f"  Description: {product_details[2]}")
            print(f"  Category ID: {product_details[3]}")
            print(f"  Unit Price: {product_details[4]}")
            print(f"  Unit of Measure: {product_details[5]}")
            # Add more fields if your table has them
        else:
            print(f"  Raw details: {product_details} (Note: Not enough fields for detailed breakdown or unexpected structure)")
    else:
        # This message covers product not found OR an error during the query (e.g., DB connection)
        print(f"Product {product_id_to_test} not found or an error occurred while retrieving details.")
    print("-" * 20)

    # --- Test get_current_stock ---
    print("\n" + "-" * 20)
    print("Testing get_current_stock...")
    stock_product_id = 'TR0002' # Example Product ID
    # get_current_stock is designed to return 0 in case of error or no stock.
    # So, direct printing is fine. Error messages would have been printed by execute_query or get_db_connection.
    current_stock = get_current_stock(stock_product_id)
    print(f"Current stock for product {stock_product_id}: {current_stock}")
    print("-" * 20)

    # --- Test get_product_expirations ---
    print("\n" + "-" * 20)
    days_to_check = 365
    print(f"Testing get_product_expirations (next {days_to_check} days)...")
    expiring_products = get_product_expirations(days_to_check)
    # get_product_expirations returns [] on error or no data
    if expiring_products is not None and len(expiring_products) > 0:
        print(f"Products expiring within {days_to_check} days:")
        # Assuming columns: id_lote, id_producto, fecha_vencimiento, cantidad
        for lot in expiring_products:
            if len(lot) >= 4: # Check if enough elements exist
                print(f"  Lot ID: {lot[0]}, Product ID: {lot[1]}, Expires: {lot[2]}, Quantity: {lot[3]}")
            else:
                print(f"  Raw lot data: {lot} (Note: Not enough fields for detailed breakdown or unexpected structure)")
    elif expiring_products == []: # Explicitly check for empty list (no data or error handled by returning [])
        print(f"No products found expiring in the next {days_to_check} days (or an error occurred during retrieval).")
    # No 'else' needed here as [] covers both "no data" and "error" scenarios from the function.
    # Error messages from execute_query/get_db_connection would have already printed for connection/query issues.
    print("-" * 20)

    # --- Test get_products_in_environment ---
    print("\n" + "-" * 20)
    environment_id_to_check = 'ENT-A1' # Example Environment ID
    print(f"Testing get_products_in_environment ({environment_id_to_check})...")
    products_in_env = get_products_in_environment(environment_id_to_check)
    # get_products_in_environment returns [] on error or no data
    if products_in_env is not None and len(products_in_env) > 0:
        print(f"Products in environment {environment_id_to_check}:")
        # Assuming result is a list of tuples, each with one product ID
        for prod_tuple in products_in_env:
            print(f"  Product ID: {prod_tuple[0]}")
    elif products_in_env == []: # Explicitly check for empty list (no data or error handled by returning [])
        print(f"No products found in environment {environment_id_to_check} (or an error occurred during retrieval).")
    # No 'else' needed here.
    print("-" * 20)

    print("\n--- All example function calls completed ---")
