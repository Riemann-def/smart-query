
-- Tabla de Usuarios
CREATE TABLE IF NOT EXISTS Usuarios(
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    fecha_registro DATE NOT NULL
);

-- Tabla de Locales
CREATE TABLE IF NOT EXISTS Locales (
    id_local SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    direccion VARCHAR(150),
    capacidad INT NOT NULL,
    telefono VARCHAR(15),
    email VARCHAR(100)
);

-- Tabla de Eventos
CREATE TABLE IF NOT EXISTS Eventos (
    id_evento SERIAL PRIMARY KEY,
    id_local INT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha DATE NOT NULL,
    hora TIME NOT NULL,
    FOREIGN KEY (id_local) REFERENCES Locales(id_local) ON DELETE CASCADE
);

-- Tabla de Entradas
CREATE TABLE IF NOT EXISTS Entradas (
    id_entrada SERIAL PRIMARY KEY,
    id_evento INT,
    id_usuario INT,
    precio DECIMAL(10,2) NOT NULL,
    fecha_compra DATE NOT NULL,
    FOREIGN KEY (id_evento) REFERENCES Eventos(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);

-- Tabla de Artistas
CREATE TABLE IF NOT EXISTS Artistas (
    id_artista SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    genero VARCHAR(50),
    pais_origen VARCHAR(50)
);

-- Tabla de Eventos_Artistas
CREATE TABLE IF NOT EXISTS Eventos_Artistas (
    id_evento INT,
    id_artista INT,
    PRIMARY KEY (id_evento, id_artista),
    FOREIGN KEY (id_evento) REFERENCES Eventos(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_artista) REFERENCES Artistas(id_artista) ON DELETE CASCADE
);

-- Tabla de Opiniones
CREATE TABLE IF NOT EXISTS Opiniones (
    id_opinion SERIAL PRIMARY KEY,
    id_evento INT,
    id_usuario INT,
    puntuacion INT NOT NULL CHECK (puntuacion BETWEEN 1 AND 5),
    comentario TEXT,
    fecha DATE NOT NULL,
    FOREIGN KEY (id_evento) REFERENCES Eventos(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);

-- Tabla de Categorías
CREATE TABLE IF NOT EXISTS Categorias (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- Tabla de Eventos_Categorias
CREATE TABLE IF NOT EXISTS Eventos_Categorias (
    id_evento INT,
    id_categoria INT,
    PRIMARY KEY (id_evento, id_categoria),
    FOREIGN KEY (id_evento) REFERENCES Eventos(id_evento) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES Categorias(id_categoria) ON DELETE CASCADE
);

-- Insertar datos de prueba en la tabla Usuarios
INSERT INTO Usuarios (nombre, email, fecha_registro) VALUES
('Juan Perez', 'juan.perez@example.com', '2023-01-01'),
('Ana Lopez', 'ana.lopez@example.com', '2023-02-15'),
('Carlos Gomez', 'carlos.gomez@example.com', '2023-03-10'),
('María Martínez', 'maria.martinez@example.com', '2023-01-20'),
('Luis Rodríguez', 'luis.rodriguez@example.com', '2023-02-25'),
('Elena Fernández', 'elena.fernandez@example.com', '2023-03-30'),
('José Sánchez', 'jose.sanchez@example.com', '2023-04-05'),
('Laura González', 'laura.gonzalez@example.com', '2023-04-15'),
('Miguel Torres', 'miguel.torres@example.com', '2023-05-20'),
('Lucía Jiménez', 'lucia.jimenez@example.com', '2023-06-01');

-- Insertar datos de prueba en la tabla Locales
INSERT INTO Locales (nombre, direccion, capacidad, telefono, email) VALUES
('Club Nocturno XYZ', 'Calle Falsa 123', 500, '555-1234', 'contacto@clubxyz.com'),
('Bar La Noche', 'Avenida Siempre Viva 742', 300, '555-5678', 'info@barnoche.com'),
('Sala de Conciertos Rock', 'Calle de la Música 45', 600, '555-4321', 'contacto@salaconciertosrock.com'),
('Pub El Rincón', 'Plaza Central 8', 200, '555-8765', 'info@pubelrincon.com'),
('Discoteca Luz y Sonido', 'Avenida del Baile 34', 700, '555-6543', 'contacto@discotecaluzsonido.com');

-- Insertar datos de prueba en la tabla Eventos
INSERT INTO Eventos (id_local, nombre, descripcion, fecha, hora) VALUES
(1, 'Fiesta Electrónica', 'Una noche con los mejores DJs de música electrónica.', '2023-06-25', '22:00:00'),
(2, 'Concierto de Rock', 'Las mejores bandas de rock en vivo.', '2023-07-01', '20:00:00'),
(3, 'Noche de Jazz', 'Disfruta del mejor jazz con artistas invitados.', '2023-07-10', '19:00:00'),
(4, 'Karaoke', 'Ven a cantar tus canciones favoritas.', '2023-07-15', '21:00:00'),
(5, 'Fiesta de Disfraces', 'Una noche de diversión y disfraces.', '2023-07-20', '23:00:00'),
(1, 'Noche de Salsa', 'Baila salsa con los mejores ritmos latinos.', '2023-07-25', '22:00:00'),
(2, 'Concierto de Pop', 'Los éxitos más sonados del pop en vivo.', '2023-08-01', '20:00:00'),
(3, 'Festival de Blues', 'Un día completo dedicado al blues.', '2023-08-05', '18:00:00'),
(4, 'Noche de Comedia', 'Ríete a carcajadas con los mejores comediantes.', '2023-08-10', '21:00:00'),
(5, 'Fiesta Retro', 'Revive los mejores momentos de las décadas pasadas.', '2023-08-15', '22:00:00');

-- Insertar datos de prueba en la tabla Artistas
INSERT INTO Artistas (nombre, genero, pais_origen) VALUES
('DJ Tiesto', 'Electrónica', 'Países Bajos'),
('Banda Los Rockeros', 'Rock', 'España'),
('Sarah Brown', 'Jazz', 'Estados Unidos'),
('Carlos Santana', 'Salsa', 'México'),
('The Retro Band', 'Pop', 'Reino Unido'),
('Blues Brothers', 'Blues', 'Estados Unidos'),
('Comedia y Risas', 'Comedia', 'España'),
('DJ Vintage', 'Retro', 'Francia');

-- Insertar datos de prueba en la tabla Eventos_Artistas
INSERT INTO Eventos_Artistas (id_evento, id_artista) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 7),
(5, 4),
(6, 4),
(7, 5),
(8, 6),
(9, 7),
(10, 8);

-- Insertar datos de prueba en la tabla Categorias
INSERT INTO Categorias (nombre) VALUES
('Concierto'),
('Fiesta'),
('Festival'),
('Comedia'),
('Karaoke'),
('Jazz'),
('Salsa'),
('Retro');

-- Insertar datos de prueba en la tabla Eventos_Categorias
INSERT INTO Eventos_Categorias (id_evento, id_categoria) VALUES
(1, 2),
(2, 1),
(3, 6),
(4, 5),
(5, 2),
(6, 7),
(7, 1),
(8, 3),
(9, 4),
(10, 8);

-- Insertar datos de prueba en la tabla Entradas
INSERT INTO Entradas (id_evento, id_usuario, precio, fecha_compra) VALUES
(1, 1, 50.00, '2023-06-01'),
(2, 2, 30.00, '2023-06-15'),
(3, 3, 40.00, '2023-06-20'),
(4, 4, 20.00, '2023-06-25'),
(5, 5, 35.00, '2023-06-30'),
(6, 6, 45.00, '2023-07-05'),
(7, 7, 25.00, '2023-07-10'),
(8, 8, 60.00, '2023-07-15'),
(9, 9, 15.00, '2023-07-20'),
(10, 10, 55.00, '2023-07-25');

-- Insertar datos de prueba en la tabla Opiniones
INSERT INTO Opiniones (id_evento, id_usuario, puntuacion, comentario, fecha) VALUES
(1, 1, 5, '¡Fue una experiencia increíble!', '2023-06-26'),
(2, 2, 4, 'Muy buen concierto, aunque faltó mejor sonido.', '2023-07-02'),
(3, 3, 5, 'El mejor concierto de jazz que he visto.', '2023-07-11'),
(4, 4, 3, 'Divertido, pero poca variedad de canciones.', '2023-07-16'),
(5, 5, 4, 'Buena fiesta, me encantaron los disfraces.', '2023-07-21'),
(6, 6, 5, 'La mejor noche de salsa de mi vida.', '2023-07-26'),
(7, 7, 4, 'Gran concierto de pop, muy entretenido.', '2023-08-02'),
(8, 8, 5, 'El festival de blues estuvo fenomenal.', '2023-08-06'),
(9, 9, 3, 'Algunos comediantes buenos, otros no tanto.', '2023-08-11'),
(10, 10, 4, 'La fiesta retro fue un viaje en el tiempo.', '2023-08-16');
