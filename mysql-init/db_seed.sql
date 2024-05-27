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
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Proyectos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_path VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

INSERT INTO Facultades (facultad) VALUES ('Ingeniería y Ciencias ambientales');
INSERT INTO Facultades (facultad) VALUES ('Ciencias Económicas');

INSERT INTO Programas (programa, facultad_id) VALUES ('Ingeniería Informática', 1);
INSERT INTO Programas (programa, facultad_id) VALUES ('Contaduría Pública', 2);
INSERT INTO Programas (programa, facultad_id) VALUES ('Administración de Empresas', 2);