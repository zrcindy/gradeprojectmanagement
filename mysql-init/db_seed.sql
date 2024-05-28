CREATE DATABASE database_production;
USE database_production;
GRANT ALL PRIVILEGES ON database_production.* TO 'userdba'@'%';

CREATE TABLE Facultades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facultad VARCHAR(255)
);

CREATE TABLE Programas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    programa VARCHAR(255),
    facultad_id INT NOT NULL,
    FOREIGN KEY (facultad_id) REFERENCES Facultades(id)
);

CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('Estudiante', 'Evaluador') NOT NULL
);

CREATE TABLE Estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    nombre VARCHAR(100) NOT NULL,
    dni VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    programa_id INT NOT NULL,
    FOREIGN KEY (programa_id) REFERENCES Programas(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Evaluadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    nombre VARCHAR(100) NOT NULL,
    dni VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    facultad_id INT NOT NULL,
    FOREIGN KEY (facultad_id) REFERENCES Facultades(id),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Propuestas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_path VARCHAR(255),
    nombre VARCHAR(255),
    descripcion VARCHAR(1000),
    calificacion VARCHAR(2),
    feedback VARCHAR(1000),
    evaluador_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (evaluador_id) REFERENCES Evaluadores(id)
);

CREATE TABLE Proyectos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_path VARCHAR(255),
    nombre VARCHAR(255),
    descripcion VARCHAR(1000),
    calificacion VARCHAR(2),
    feedback VARCHAR(1000),
    evaluador_id INT,
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (evaluador_id) REFERENCES Evaluadores(id)
);

INSERT INTO Facultades (facultad) VALUES ('Ingenieria y Ciencias ambientales');
INSERT INTO Facultades (facultad) VALUES ('Ciencias Economicas');

INSERT INTO Programas (programa, facultad_id) VALUES ('Ingenieria Informatica', 1);
INSERT INTO Programas (programa, facultad_id) VALUES ('Contaduria Publica', 2);
INSERT INTO Programas (programa, facultad_id) VALUES ('Administracion de Empresas', 2);

INSERT INTO Users (username, password, role) VALUES ('admin', 'admin', 'Evaluador');
INSERT INTO Evaluadores (user_id, nombre, dni, email, facultad_id) VALUES (1, 'Admin', '11111', 'admin@localhost.com', 1);