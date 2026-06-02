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


-- Criação do trigger que define automaticamente o vencedor da partida
DELIMITER $$

CREATE TRIGGER trg_definir_vencedor
BEFORE INSERT ON partidas
FOR EACH ROW
BEGIN
    IF NEW.quantidade_gols_selecao_1 > NEW.quantidade_gols_selecao_2 THEN
        SET NEW.vencedor = NEW.id_selecao_1;
    ELSEIF NEW.quantidade_gols_selecao_2 > NEW.quantidade_gols_selecao_1 THEN
        SET NEW.vencedor = NEW.id_selecao_2;
    ELSE
        SET NEW.vencedor = NULL; -- Indica empate
    END IF;
END$$

DELIMITER ;





-- Inserção
INSERT INTO estadios (nome_estadio, cidade, pais, capacidade) VALUES 
('MetLife Stadium', 'Nova Jersey', 'Estados Unidos', 82500),
('Estádio Azteca', 'Cidade do México', 'México', 87523),
('SoFi Stadium', 'Los Angeles', 'Estados Unidos', 70240),
('BMO Field', 'Toronto', 'Canadá', 30000);


INSERT INTO selecoes (nome_selecao, continente, tecnico, titulos) VALUES 
('Brasil', 'América do Sul', 'Dorival Júnior', 5),
('França', 'Europa', 'Didier Deschamps', 2),
('Argentina', 'América do Sul', 'Lionel Scaloni', 3),
('Estados Unidos', 'América do Norte', 'Gregg Berhalter', 0);


INSERT INTO jogadores (nome_jogador, posicao, numero_camisa, data_nascimento, id_selecao) VALUES 
('Vinícius Júnior', 'Atacante', 7, '2000-07-12', 1),
('Endrick', 'Atacante', 9, '2006-07-21', 1),
('Kylian Mbappé', 'Atacante', 10, '1998-12-20', 2),
('Eduardo Camavinga', 'Meio-campo', 6, '2002-11-10', 2),
('Lionel Messi', 'Atacante', 10, '1987-06-24', 3),
('Christian Pulisic', 'Atacante', 10, '1998-09-18', 4);


INSERT INTO partidas (data_partida, id_estadio, id_selecao_1, id_selecao_2, quantidade_gols_selecao_1, quantidade_gols_selecao_2, vencedor) VALUES 
('2026-06-15', 3, 1, 4, 3, 1, 1),
('2026-06-18', 1, 2, 3, 2, 2, NULL), -- Empate no MetLife Stadium
('2026-06-22', 2, 1, 3, 2, 1, 1);    