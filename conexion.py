import mysql.connector

# Establecer conexión
conexion = mysql.connector.connect(
    host="localhost",         # O dirección IP del servidor
    user="root",
    password="Pata2021.",
    database="BD_proyecto"
)

# Crear cursor para ejecutar queries
cursor = conexion.cursor()

print("✅ Conexión establecida correctamente")

cursor.execute("SELECT * FROM producto")

# Obtener todos los resultados
resultados = cursor.fetchall()

# Imprimir resultados
for fila in resultados:
    print(fila)
