#!/bin/sh

docker run -d -p 3306:3306 -e MYSQL_USER=mysql -e MYSQL_PASSWORD=mysql mysql
