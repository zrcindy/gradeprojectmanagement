# Gestión de trabajos de grado

## Descripción

Sistema de software para la gestión de trabajos de grado en la Fundación Universitaria Católica del Norte (FUCN).

## Tecnologías utilizadas

Lenguaje de programación: Python 3.9-alpine,
Base de datos: MySQL,
Entorno de desarrollo: Visual Studio Code,
Herramienta de empaquetado: Docker.
Framwework: Flask con HTLM, CSS.

## Requisitos previos

Tener Docker instalado en su sistema, PlugIn de Docker Compose y Git.

## Instalación

1. Clonar el repositorio del proyecto: git clone https://github.com/tu_usuario/gradeprojectmanagement.git
2. Acceder al directorio del proyecto: cd gradeprojectmanagement
3. Iniciar el proyecto con Docker Compose: docker-compose up -d
4. Acceder a la aplicación web: Abra su navegador web y navegue a la dirección http://localhost:5000 

## Uso

1. Registro de usuario con rol estudiantes: Los estudiantes pueden registrar un nombre de usuario, una clave, nombre completo, su identificación, correo electrónico y seleccionar su carrera y/o programa de estudio.
2. Registro de usuarios evaluadores: Los evaluadores pueden registrar un nombre de usuario, una clave, nombre completo, su identificación, correo electrónico y seleccionar la facultad a la que pertenecen.
3. El usuario con rol estudiante al momento de iniciar sesión en el portal web podrá enviar una propuesta de grado, consultar el estado de la propuesta enviada, enviar proyecto de trabajo de grado, consultar estado de su proyecto de trabajo de grado, actualizar su perfil y finalizar la sesión.
4. El usuario con rol evaluador al momento de iniciar sesión en el portal web podrá revisar las propuestas de grado de acuerdo a los programas de estudio que pertenecen a su facultad, nombre del estudiante, correo, identificación, nombre del programa, también podrá descargar archivo de la propuesta enviada. Consulta de proyectos de trabajo de grado de acuerdo a los programas de estudio que pertenecen a su facultad, nombre del estudiante, correo, identificación, nombre del programa, también podrá descargar archivo del proyecto de trabajo de grado enviado actualizar su perfil y finalizar la sesión.

