CREATE DATABASE database_production;
USE database_production;
GRANT ALL PRIVILEGES ON database_production.* TO 'userdba'@'%';

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role ENUM('Estudiante', 'Evaluador') NOT NULL
);

CREATE TABLE propuestas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    filename VARCHAR(100) NOT NULL
);