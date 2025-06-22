CREATE DATABASE BD_proyecto_2;
use BD_proyecto_2;
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
use BD_proyecto_2;
CREATE TABLE producto (
    id_producto varchar(8) PRIMARY KEY not null,
    descripcion VARCHAR(100),
    tipo ENUM('SIM', 'DISPOSITIVO') ,
    modelo VARCHAR(50),
    operador ENUM('ENTEL', 'MOVISTAR', 'CLARO', 'BITEL'),
    numero_serie VARCHAR(100),
    iccid VARCHAR(25),
    direccion_mac VARCHAR(50),
    tecnologia VARCHAR(50),
    propiedad ENUM('ALQUILADO', 'EN ALMACEN', 'VENDIDO'),
    estado ENUM('NUEVO', 'ACTIVO', 'USADO', 'REACONDICIONADO', 'DAÑADO'),
    ruta VARCHAR(200),
	nombre VARCHAR(260)
);
use BD_proyecto_2;
CREATE TABLE lote (
    id_lote VARCHAR(12) PRIMARY KEY NOT NULL,
    id_producto VARCHAR(8) not null,
    fecha_ingreso DATE,
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto) 
);
use BD_proyecto_2;
CREATE TABLE movimiento_kardex (
    num_movimiento varchar(8) PRIMARY KEY not null,
    fecha DATE,
    tipo_movimiento ENUM('ENTRADA', 'SALIDA', 'DEVOLUCION', 'MANTENIMIENTO') ,
    id_producto VARCHAR(8) NOT NULL,
    id_lote varchar(12) not null, 
    cantidad INT ,
    id_entorno VARCHAR(12)  NOT NULL ,
    estado_post_movimiento ENUM('NUEVO', 'ACTIVO', 'USADO', 'REACONDICIONADO', 'DAÑADO'),
    FOREIGN KEY (id_producto) REFERENCES producto(id_producto),
    FOREIGN KEY (id_entorno) REFERENCES entorno_almacenamiento(id_entorno),
    FOREIGN KEY (id_lote) REFERENCES lote(id_lote)
);

use BD_proyecto_2;
INSERT INTO producto (id_producto, nombre, tipo, modelo, operador, numero_serie, iccid, direccion_mac, tecnologia, propiedad, estado) VALUES
('TR0001', 'SIM Entel', 'SIM', NULL, 'ENTEL', NULL, '8957123456789012345', NULL, NULL, 'VENDIDO', 'NUEVO'),
('TR0002','SIM Movistar', 'SIM', NULL, 'MOVISTAR', NULL, '8957456123789456123', NULL, NULL, 'EN ALMACEN', 'NUEVO'),
('TR0003','SIM Claro', 'SIM', NULL, 'CLARO', NULL, '8957987612345678901', NULL, NULL, 'VENDIDO', 'NUEVO'),
('TR0004','SIM Bitel', 'SIM', NULL, 'BITEL', NULL, '8957456987654321234', NULL, NULL, 'ALQUILADO', 'NUEVO'),
('DS0001','Router Huawei HG8245H', 'DISPOSITIVO', 'HG8245H', NULL, 'SN12345678A', NULL, 'AA:BB:CC:DD:EE:01', 'FTTH', 'EN ALMACEN', 'NUEVO'),
('DS0002','ONT ZTE F660', 'DISPOSITIVO', 'F660', NULL, 'SN98765432Z', NULL, 'AA:BB:CC:DD:EE:02', 'FTTH', 'ALQUILADO', 'NUEVO'),
('DS0003','Módem Claro 4G', 'DISPOSITIVO', 'E8372h-320', 'CLARO', 'SN56789XY', NULL, 'AA:BB:CC:DD:EE:03', '4G LTE', 'VENDIDO', 'NUEVO'),
('DS0004','Router TP-Link Archer C6', 'DISPOSITIVO', 'Archer C6', NULL, 'SNTP123456', NULL, 'AC:DE:48:00:11:22', 'WiFi 5', 'EN ALMACEN', 'NUEVO'),
('DS0005','ONT Huawei EchoLife', 'DISPOSITIVO', 'HG8010H', NULL, 'SNHG8010H01', NULL, 'A1:B2:C3:D4:E5:F6', 'FTTH', 'ALQUILADO', 'NUEVO'),
('DS0006','Módem Movistar LTE', 'DISPOSITIVO', 'B310s-518', 'MOVISTAR', 'SNB310S001', NULL, 'DC:FE:23:45:67:89', '4G LTE', 'VENDIDO', 'NUEVO');

use BD_proyecto_2;
INSERT INTO entorno_almacenamiento (id_entorno, nombre, ubicacion_fisica, temperatura_min, temperatura_max, humedad_min, humedad_max, ventilacion) VALUES
('ENT-A2', 'Almacén regulado inferior', 'Primer piso', 18.00, 27.00, 40.00, 60.00, 'SI'),
('ENT-A3', 'Almacén regulado superior', 'Segundo piso', 20.00, 25.00, 35.00, 55.00, 'SI'),
('ENT-A1', 'Reparaciones', 'Sótano', null, null, null, null, 'NO');

use BD_proyecto_2;
INSERT INTO lote (id_lote, id_producto, fecha_ingreso)
VALUES 
('L20250201A3F', 'DS0001', '2025-06-09'),
('L202502127BD', 'DS0002', '2025-06-09'),
('L20250604B1C', 'DS0003', '2025-06-09'),
('L20250605B1D', 'DS0004', '2025-06-10'),
('L20250606B1E', 'DS0005', '2025-06-10'),
('L20250607B1F', 'DS0006', '2025-06-10'),
('L20250610B1I', 'DS0001', '2025-06-10'),
('L20250611B1J', 'DS0002', '2025-06-11'),
('L202501109CE', 'DS0006', '2025-06-11'),
('L20250601B1A', 'TR0001', '2025-06-11'),
('L20250105E19', 'TR0002', '2025-06-12'),
('L20250603B1B', 'TR0003', '2025-06-12'),
('L2025062127A', 'TR0004', '2025-06-12'),
('L20250608B1G', 'TR0001', '2025-06-12'),
('L20250609B1H', 'TR0002', '2025-06-12');

use BD_proyecto_2;
INSERT INTO movimiento_kardex (num_movimiento, fecha, tipo_movimiento, id_producto, cantidad, id_entorno, estado_post_movimiento, id_lote) VALUES
('1', '2025-06-09', 'ENTRADA', 'DS0001', 50, 'ENT-A1', 'NUEVO', 'L20250201A3F'),
('2', '2025-06-11', 'ENTRADA', 'DS0006', 30, 'ENT-A1', 'NUEVO', 'L202501109CE'),
('3', '2025-06-12', 'ENTRADA', 'TR0002', 200 , 'ENT-A1', 'NUEVO', 'L20250105E19'),
('4', '2025-06-09', 'ENTRADA', 'DS0002', 20, 'ENT-A2', 'NUEVO', 'L202502127BD'),
('5', '2025-06-12', 'ENTRADA', 'TR0004', 500, 'ENT-A1', 'NUEVO', 'L2025062127A'),
('6', '2025-06-11', 'ENTRADA', 'TR0001', 100, 'ENT-A2', 'NUEVO', 'L20250601B1A'),
('7', '2025-06-12', 'ENTRADA', 'TR0003', 120, 'ENT-A2', 'NUEVO', 'L20250603B1B'),
('8', '2025-06-09', 'ENTRADA', 'DS0003', 50, 'ENT-A2', 'NUEVO', 'L20250604B1C'),
('9', '2025-06-10', 'ENTRADA', 'DS0004', 60, 'ENT-A1', 'NUEVO', 'L20250605B1D'),
('10', '2025-06-10', 'ENTRADA', 'DS0005', 45, 'ENT-A2', 'NUEVO', 'L20250606B1E'),
('11', '2025-06-10', 'ENTRADA', 'DS0006', 70, 'ENT-A1', 'NUEVO', 'L20250607B1F'),
('12', '2025-06-12', 'ENTRADA', 'TR0001', 80, 'ENT-A1', 'NUEVO', 'L20250608B1G'),
('13', '2025-06-12', 'ENTRADA', 'TR0002', 90, 'ENT-A2', 'NUEVO', 'L20250609B1H'),
('14', '2025-06-10', 'ENTRADA', 'DS0001', 55, 'ENT-A1', 'NUEVO', 'L20250610B1I'),
('15', '2025-06-11', 'ENTRADA', 'DS0002', 100, 'ENT-A1', 'NUEVO', 'L20250611B1J'),
('16', '2025-06-13', 'SALIDA', 'DS0001', 20, 'ENT-A1', 'USADO', 'L20250201A3F'),
('17', '2025-06-13', 'SALIDA', 'DS0006', 25, 'ENT-A1', 'USADO', 'L202501109CE'),
('18', '2025-06-13', 'SALIDA', 'TR0002', 150, 'ENT-A1', 'USADO', 'L20250105E19'),
('19', '2025-06-14', 'SALIDA', 'DS0002', 10, 'ENT-A2', 'USADO', 'L202502127BD'),
('20', '2025-06-14', 'SALIDA', 'TR0004', 300, 'ENT-A1', 'USADO', 'L2025062127A'),
('21', '2025-06-14', 'SALIDA', 'TR0001', 60, 'ENT-A2', 'USADO', 'L20250601B1A'),
('22', '2025-06-14', 'SALIDA', 'TR0003', 100, 'ENT-A2', 'USADO', 'L20250603B1B'),
('23', '2025-06-13', 'SALIDA', 'DS0003', 30, 'ENT-A2', 'USADO', 'L20250604B1C'),
('24', '2025-06-14', 'SALIDA', 'DS0004', 40, 'ENT-A1', 'USADO', 'L20250605B1D'),
('25', '2025-06-13', 'SALIDA', 'DS0005', 20, 'ENT-A2', 'USADO', 'L20250606B1E'),
('26', '2025-06-14', 'SALIDA', 'DS0006', 50, 'ENT-A1', 'USADO', 'L20250607B1F'),
('27', '2025-06-14', 'SALIDA', 'TR0001', 60, 'ENT-A1', 'USADO', 'L20250608B1G'),
('28', '2025-06-14', 'SALIDA', 'TR0002', 70, 'ENT-A2', 'USADO', 'L20250609B1H'),
('29', '2025-06-13', 'SALIDA', 'DS0001', 30, 'ENT-A1', 'USADO', 'L20250610B1I'),
('30', '2025-06-14', 'SALIDA', 'DS0002', 80, 'ENT-A1', 'USADO', 'L20250611B1J');


use BD_proyecto_2;
SELECT * FROM movimiento_kardex;

use BD_proyecto_2;
select * from lote;

use BD_proyecto_2;
select * from producto;

use BD_proyecto_2;
select * from entorno_almacenamiento;

use BD_proyecto_2;
show columns from lote;

USE BD_proyecto_2;
DELETE FROM lote where id_lote 