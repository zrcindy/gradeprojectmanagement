CREATE DATABASE database_production;
USE database_production;
GRANT ALL PRIVILEGES ON database_production.* TO 'userdba'@'%';

CREATE TABLE propuestas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    filename VARCHAR(100) NOT NULL
);