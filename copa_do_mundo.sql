CREATE DATABASE copa_do_mundo;
USE copa_do_mundo;

-- Criação das tabelas sem dependência
CREATE TABLE estadios (
    id_estadio INT PRIMARY KEY AUTO_INCREMENT,
    nome_estadio VARCHAR(80),
    cidade VARCHAR(50),
    pais VARCHAR(50),
    capacidade INT
);

CREATE TABLE selecoes (
    id_selecao INT PRIMARY KEY AUTO_INCREMENT,
    nome_selecao VARCHAR(50),
    continente VARCHAR(30),
    tecnico VARCHAR(50),
    titulos INT
);

-- Criação das tabelas com chaves estrangeiras
CREATE TABLE jogadores (
    id_jogador INT PRIMARY KEY AUTO_INCREMENT,
    nome_jogador VARCHAR(60),
    posicao VARCHAR(30),
    numero_camisa INT,
    data_nascimento DATE,
    id_selecao INT,
    FOREIGN KEY (id_selecao) REFERENCES selecoes(id_selecao)
);

CREATE TABLE partidas (
    id_partida INT PRIMARY KEY AUTO_INCREMENT,
    data_partida DATE,
    id_estadio INT,
    id_selecao_1 INT,
    id_selecao_2 INT,
    quantidade_gols_selecao_1 INT,
    quantidade_gols_selecao_2 INT,
    vencedor INT,
    FOREIGN KEY (id_estadio) REFERENCES estadios(id_estadio),
    FOREIGN KEY (id_selecao_1) REFERENCES selecoes(id_selecao),
    FOREIGN KEY (id_selecao_2) REFERENCES selecoes(id_selecao),
    FOREIGN KEY (vencedor) REFERENCES selecoes(id_selecao)
);
