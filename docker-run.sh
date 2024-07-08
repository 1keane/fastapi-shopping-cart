#!/bin/bash

cp Dockerfile-db Dockerfile
docker build -t shopping-cart-db .
docker run -d --name shopping-cart-db -p 5432:5432 shopping-cart-db

cp Dockerfile-api Dockerfile
docker build -t fastapi-shopping-cart .
docker run -d --name fastapi-shopping-cart -p 8000:8000 --link shopping-cart-db:db fastapi-shopping-cart

rm Dockerfile
