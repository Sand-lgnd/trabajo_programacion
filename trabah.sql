CREATE DATABASE BD_proyecto
use BD_proyecto;
CREATE TABLE entorno_almacenamiento (
    id_entorno VARCHAR(10) PRIMARY KEY not null,
    nombre VARCHAR(100),
    ubicacion_fisica VARCHAR(100),
    temperatura_min DECIMAL(5,2),
    temperatura_max DECIMAL(5,2),
    humedad_min DECIMAL(5,2),
    humedad_max DECIMAL(5,2),
    ventilacion VARCHAR(5)
);
CREATE TABLE producto (
    id_producto varchar(8) PRIMARY KEY not null,
    descripcion VARCHAR(100),
    tipo ENUM('SIM', 'DISPOSITIVO') ,
    modelo VARCHAR(50),
    operador VARCHAR(50),
    numero_serie VARCHAR(100),
    iccid VARCHAR(25),
    direccion_mac VARCHAR(50),
    tecnologia VARCHAR(50),
    propiedad ENUM('ALQUILADO', 'EN ALMACEN', 'VENDIDO'),
    estado ENUM('NUEVO', 'ACTIVO', 'USADO', 'REACONDICIONADO', 'DAÑADO'),
    ruta VARCHAR(200),
	nombre VARCHAR(260)
);
CREATE TABLE lote (
    id_lote VARCHAR(50) NOT NULL,  -- Código de lote del proveedor
    id_producto VARCHAR(8) NOT NULL,
    fecha_vencimiento DATE,
    fecha_ingreso DATE,
    PRIMARY KEY (id_lote, id_producto),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);
use BD_proyecto
CREATE TABLE movimiento_kardex (
    num_movimiento varchar(8) PRIMARY KEY not null,
    fecha DATE,
    tipo_movimiento ENUM('ENTRADA', 'SALIDA', 'DEVOLUCION', 'MANTENIMIENTO') ,
    id_producto VARCHAR(8) NOT NULL,
    cantidad INT ,
    id_entorno VARCHAR(12) NOT NULL REFERENCES entorno_almacenamiento(id_entorno) ,
    estado_post_movimiento ENUM('NUEVO', 'ACTIVO', 'USADO', 'REACONDICIONADO', 'DAÑADO'),
    id_lote VARCHAR(50) NOT NULL,
    FOREIGN KEY (id_lote, id_producto) REFERENCES lote(id_lote, id_producto),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
);

use BD_proyecto
INSERT INTO producto (id_producto, nombre, tipo, modelo, operador, numero_serie, iccid, direccion_mac, tecnologia, propiedad, estado) VALUES
('TR0001', 'SIM Entel', 'SIM', NULL, 'Entel', NULL, '8957123456789012345', NULL, NULL, 'VENDIDO', 'NUEVO'),
('TR0002','SIM Movistar', 'SIM', NULL, 'Movistar', NULL, '8957456123789456123', NULL, NULL, 'EN ALMACEN', 'NUEVO'),
('TR0003','SIM Claro', 'SIM', NULL, 'Claro', NULL, '8957987612345678901', NULL, NULL, 'VENDIDO', 'NUEVO'),
('TR0004','SIM Bitel', 'SIM', NULL, 'Bitel', NULL, '8957456987654321234', NULL, NULL, 'ALQUILADO', 'NUEVO'),
('DS0001','Router Huawei HG8245H', 'DISPOSITIVO', 'HG8245H', NULL, 'SN12345678A', NULL, 'AA:BB:CC:DD:EE:01', 'FTTH', 'EN ALMACEN', 'NUEVO'),
('DS0002','ONT ZTE F660', 'DISPOSITIVO', 'F660', NULL, 'SN98765432Z', NULL, 'AA:BB:CC:DD:EE:02', 'FTTH', 'ALQUILADO', 'NUEVO'),
('DS0003','Módem Claro 4G', 'DISPOSITIVO', 'E8372h-320', 'Claro', 'SN56789XY', NULL, 'AA:BB:CC:DD:EE:03', '4G LTE', 'VENDIDO', 'NUEVO'),
('DS0004','Router TP-Link Archer C6', 'DISPOSITIVO', 'Archer C6', NULL, 'SNTP123456', NULL, 'AC:DE:48:00:11:22', 'WiFi 5', 'EN ALMACEN', 'NUEVO'),
('DS0005','ONT Huawei EchoLife', 'DISPOSITIVO', 'HG8010H', NULL, 'SNHG8010H01', NULL, 'A1:B2:C3:D4:E5:F6', 'FTTH', 'ALQUILADO', 'NUEVO'),
('DS0006','Módem Movistar LTE', 'DISPOSITIVO', 'B310s-518', 'Movistar', 'SNB310S001', NULL, 'DC:FE:23:45:67:89', '4G LTE', 'VENDIDO', 'NUEVO');

use BD_proyecto;
INSERT INTO entorno_almacenamiento (id_entorno, nombre, ubicacion_fisica, temperatura_min, temperatura_max, humedad_min, humedad_max, ventilacion) VALUES
('ENT-A2', 'Almacén regulado inferior', 'Primer piso', 18.00, 27.00, 40.00, 60.00, 'SI'),
('ENT-A3', 'Almacén regulado superior', 'Segundo piso', 20.00, 25.00, 35.00, 55.00, 'SI'),
('ENT-A1', 'Reparaciones', 'Sótano', null, null, null, null, 'NO');

use BD_proyecto;
INSERT INTO lote (id_lote, id_producto, fecha_vencimiento, fecha_ingreso)
VALUES 
('L20250201A3F', 'DS0001', '2025-12-15', '2025-02-01'),
('L202501109CE', 'DS0006', '2025-09-21', '2025-01-10'),
('L20250105E19', 'TR0002', '2025-12-21', '2025-01-05'),
('L202502127BD', 'DS0002', '2025-11-20', '2025-02-12'),
('L2025062127A', 'TR0004', '2026-04-21', '2025-06-21');

use BD_proyecto;
INSERT INTO movimiento_kardex (num_movimiento, fecha, tipo_movimiento, id_producto, cantidad, id_entorno, estado_post_movimiento, id_lote) VALUES
('N0000001', '2025-02-01', 'ENTRADA', 'DS0001', 50, 'ENT-A1', 'NUEVO', 'L20250201A3F'),
('N0000002', '2025-01-10', 'ENTRADA', 'DS0006', 30, 'ENT-A3', 'DAÑADO', 'L202501109CE'),
('N0000003', '2025-01-05', 'SALIDA', 'TR0002', 200 , 'ENT-A1', 'NUEVO', 'L20250105E19'),
('N0000004', '2025-02-12', 'SALIDA', 'DS0002', 20, 'ENT-A2', 'NUEVO', 'L202502127BD'),
('N0000005', '2025-06-21', 'ENTRADA', 'TR0004', 500, 'ENT-A1', 'NUEVO', 'L2025062127A');

use BD_proyecto;
SELECT * FROM movimiento_kardex;

use BD_proyecto;
select * from lote;

use BD_proyecto;
select * from producto;

use BD_proyecto;
select * from entorno_almacenamiento



