CREATE DATABASE database_production;
USE database_production;
GRANT ALL PRIVILEGES ON database_production.* TO 'userdba'@'%';

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
    programa VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

CREATE TABLE Evaluadores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    nombre VARCHAR(100) NOT NULL,
    dni VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    especialidad VARCHAR(100),
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