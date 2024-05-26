FROM mysql
COPY ./mysql-init/ /docker-entrypoint-initdb.d/
EXPOSE 3306