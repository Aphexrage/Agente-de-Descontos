CREATE DATABASE loja;
USE loja

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(50),
    sobrenome VARCHAR(50),
    email VARCHAR(100)
);

CREATE TABLE produtos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome_do_produto VARCHAR(100),
    categoria VARCHAR(50),
    data_compra DATE,
    preco DECIMAL(10,2),
    data_entrega DATE,
    id_cliente INT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);