import mysql.connector
import getpass
import bcrypt

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root', 
    'password': '1234', 
    'database': 'inventario_dispos' 
}

def create_tables():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Tabla usuarios
        cursor.execute("""
        CREATE TABLE usuarios (
            id INT AUTO_INCREMENT PRIMARY KEY,
            alias VARCHAR(50) UNIQUE NOT NULL,
            rol ENUM('usuario','encargado') NOT NULL,
            password_hash VARCHAR(255) NULL -- NULL para usuarios que no tienen contraseña
        ) ENGINE=InnoDB;
        """)

        # Tabla categorias
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(50) UNIQUE NOT NULL,
            stock_minimo INT DEFAULT 0
        ) ENGINE=InnoDB;
        """)

        # Tabla proyectos
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS proyectos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) UNIQUE NOT NULL,
            descripcion TEXT
        ) ENGINE=InnoDB;
        """)

        # Tabla componentes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS componentes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            referencia VARCHAR(50) UNIQUE NOT NULL,
            descripcion TEXT,
            ubicacion VARCHAR(100),
            stock INT NOT NULL DEFAULT 0,
            categoria_id INT NOT NULL,
            proyecto_id INT,
            rango_frecuencia VARCHAR(50),
            potencia_max VARCHAR(50),
            tipo_conector VARCHAR(50),
            protocolo_soporte VARCHAR(50),
            version_firmware VARCHAR(50),
            fecha_calibracion DATE,
            FOREIGN KEY (categoria_id) REFERENCES categorias(id) ON DELETE RESTRICT ON UPDATE CASCADE,
            FOREIGN KEY (proyecto_id) REFERENCES proyectos(id) ON DELETE SET NULL ON UPDATE CASCADE
        ) ENGINE=InnoDB;
        """)

        # Tabla compatibilidad_componentes
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS compatibilidad_componentes (
            id INT AUTO_INCREMENT PRIMARY KEY, 
            componente_origen_id INT NOT NULL,
            componente_compatible_id INT NOT NULL,
            tipo_compatibilidad VARCHAR(100) NOT NULL,
            notas TEXT,
            UNIQUE (componente_origen_id, componente_compatible_id),
            FOREIGN KEY (componente_origen_id) REFERENCES componentes(id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (componente_compatible_id) REFERENCES componentes(id) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB;
        """)

        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error al conectar o crear tablas: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada.")

def seed_initial_data():
    print("\nInsertando datos de prueba")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM usuarios WHERE alias = 'alonso' LIMIT 1;")
        if not cursor.fetchone():
            admin_pass = getpass.getpass("Ingrese la contraseña para el usuario 'alonso': ")
            hashed_password = bcrypt.hashpw(admin_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            cursor.execute(
                "INSERT INTO usuarios (alias, rol, password_hash) VALUES (%s, %s, %s)",
                ('alonso', 'encargado', hashed_password)
            )
            conn.commit()
            print("Usuario 'alonso' creado.")
        else:
            print("Usuario 'alonso' ya existe.")

        cursor.execute("SELECT id FROM usuarios WHERE alias = 'andre' LIMIT 1;")
        if not cursor.fetchone():
            print("Creando usuario 'andre' ")
            cursor.execute(
                "INSERT INTO usuarios (alias, rol, password_hash) VALUES (%s, %s, %s)",
                ('andre', 'usuario', None)
            )
            conn.commit()
            print("Usuario 'andre' creado.")
        else:
            print("Usuario 'andre' ya existe.")

        categorias = [
            ('Antenas', 10), ('Transceptores', 5), ('Cables Coaxiales', 20),
            ('Conectores RF', 50), ('Filtros', 5), ('Amplificadores', 3)
        ]
        for nombre, stock_minimo in categorias:
            cursor.execute("SELECT id FROM categorias WHERE nombre = %s", (nombre,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO categorias (nombre, stock_minimo) VALUES (%s, %s)", (nombre, stock_minimo))
                # print(f"Categoría '{nombre}' insertada.") # Desactivado para menos ruido
        conn.commit()

        proyectos = [
            ('Proyecto Alfa', 'Instalación de red 5G en el centro'),
            ('Proyecto Beta', 'Actualización de infraestructura rural')
        ]
        for nombre, desc in proyectos:
            cursor.execute("SELECT id FROM proyectos WHERE nombre = %s", (nombre,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO proyectos (nombre, descripcion) VALUES (%s, %s)",
                               (nombre, desc))
        conn.commit()

        cursor.execute("SELECT id, nombre FROM categorias WHERE nombre = 'Antenas';")
        antenas_id = cursor.fetchone()[0] if cursor.rowcount else None
        cursor.execute("SELECT id, nombre FROM categorias WHERE nombre = 'Transceptores';")
        transceptores_id = cursor.fetchone()[0] if cursor.rowcount else None
        cursor.execute("SELECT id, nombre FROM categorias WHERE nombre = 'Cables Coaxiales';")
        cables_id = cursor.fetchone()[0] if cursor.rowcount else None

        cursor.execute("SELECT id, nombre FROM proyectos WHERE nombre = 'Proyecto Alfa';")
        proyecto_alfa_id = cursor.fetchone()[0] if cursor.rowcount else None


        componentes = [
            ('Antena Direccional 5G', 'ANT-5G-DIR-001', 'Antena de alta ganancia para 5G', 'Almacén A', 15, antenas_id, proyecto_alfa_id, '3.5-3.8 GHz', '100W', 'N-Type', 'NR', '1.0.0', '2025-01-01'),
            ('Transceptor RF 2.4GHz', 'TRX-2.4G-002', 'Transceptor para enlaces de corta distancia', 'Almacén B', 8, transceptores_id, None, '2.4-2.5 GHz', '50W', 'SMA', 'WiFi', '2.1.0', '2025-02-15'),
            ('Cable Coaxial LMR400', 'CAB-LMR400-100', 'Cable de baja pérdida de 100 metros', 'Almacén C', 30, cables_id, None, 'DC-6 GHz', '200W', 'N/A', 'N/A', None, None),
        ]

        for comp_data in componentes:
            nombre_comp = comp_data[0]
            cursor.execute("SELECT id FROM componentes WHERE nombre = %s", (nombre_comp,))
            if not cursor.fetchone():
                try:
                    cursor.execute("""
                        INSERT INTO componentes (
                            nombre, referencia, descripcion, ubicacion, stock,
                            categoria_id, proyecto_id, rango_frecuencia, potencia_max,
                            tipo_conector, protocolo_soporte, version_firmware, fecha_calibracion
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, comp_data)
                except mysql.connector.Error as e:
                    print(f"Error al insertar componente '{nombre_comp}': {e}")
        conn.commit()

        componentes_ref_map = {}
        cursor.execute("SELECT id, referencia FROM componentes")
        for row in cursor.fetchall():
            componentes_ref_map[row[1]] = row[0]

        compatibilidad_data = [
            ('ANT-5G-DIR-001', 'TRX-2.4G-002', 'Conexión RF', 'Se necesita adaptador de impedancia.'),
            ('TRX-2.4G-002', 'CAB-LMR400-100', 'Conector', 'Requiere conectores SMA Macho-Hembra.')
        ]

        for origen_ref, compatible_ref, tipo, notas in compatibilidad_data:
            origen_id = componentes_ref_map.get(origen_ref)
            compatible_id = componentes_ref_map.get(compatible_ref)
            if origen_id and compatible_id:
                cursor.execute("""
                    INSERT IGNORE INTO compatibilidad_componentes
                    (componente_origen_id, componente_compatible_id, tipo_compatibilidad, notas)
                    VALUES (%s, %s, %s, %s)
                """, (origen_id, compatible_id, tipo, notas))
        conn.commit()

    except mysql.connector.Error as err:
        print(f"Error al insertar datos: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Conexión a la base de datos cerrada.")


if __name__ == "__main__":
    create_tables()
    seed_initial_data()
    print("\nProceso de configuracion de la base de datos acabado.")