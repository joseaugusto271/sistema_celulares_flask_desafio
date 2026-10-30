-- assistencia_db.sql | MySQL 8+ | Uso: mysql -u root -p < assistencia_db.sql
DROP DATABASE IF EXISTS assistencia_db;
CREATE DATABASE assistencia_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE assistencia_db;

CREATE TABLE usuarios (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  login VARCHAR(50) NOT NULL UNIQUE,
  senha_hash CHAR(60) NOT NULL,            -- bcrypt
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clientes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(120) NOT NULL,
  cpf_hash CHAR(60) NOT NULL,              -- CPF criptografado com bcrypt (LGPD)
  telefone VARCHAR(20),
  email VARCHAR(120),
  endereco VARCHAR(200),
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE aparelhos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  cliente_id INT NOT NULL,
  imei CHAR(15) NOT NULL UNIQUE,           -- 15 dígitos
  marca VARCHAR(50) NOT NULL,
  modelo VARCHAR(50) NOT NULL,
  cor VARCHAR(30),
  defeito VARCHAR(255) NOT NULL,           -- defeito relatado pelo cliente
  CONSTRAINT fk_aparelho_cliente FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE servicos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  descricao VARCHAR(100) NOT NULL,
  valor DECIMAL(10,2) NOT NULL
);

CREATE TABLE agendamentos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  aparelho_id INT NOT NULL,
  servico_id INT NOT NULL,
  data_agendamento DATETIME NOT NULL,
  status ENUM('AGENDADO','EM_ANDAMENTO','CONCLUIDO','CANCELADO') NOT NULL DEFAULT 'AGENDADO',
  observacao VARCHAR(255),
  CONSTRAINT fk_ag_aparelho FOREIGN KEY (aparelho_id) REFERENCES aparelhos(id),
  CONSTRAINT fk_ag_servico FOREIGN KEY (servico_id) REFERENCES servicos(id)
);

-- Senhas de teste: admin/admin123 | carlos/carlos123 | ana/ana12345
INSERT INTO usuarios (nome, login, senha_hash) VALUES
('Administrador','admin','$2b$10$qizaoAEHzt5Hz/vRqXSL.uYENkSH9GpokflvL.8V1mn3QEBTyXZiO'),
('Carlos Técnico','carlos','$2b$10$r32LnLIp2cB54XivPH1Nau70ftffbmF3BPyPm8.VZIBkgD4MR.KTK'),
('Ana Atendente','ana','$2b$10$UWZ0bg.GPd50uIKOhkyUqu3.n4ceo3X8ZX.P1S.wQlNfqh88D6mTO');

-- CPFs de teste (válidos): 529.982.247-25 | 111.444.777-35 | 390.533.447-05
INSERT INTO clientes (nome, cpf_hash, telefone, email, endereco) VALUES
('João da Silva','$2b$10$KhQB9kIqUe31KTL6YcE3ouJPBhHvYgzEdile2lXILS36A55FGFk7W','(11) 98888-1111','joao@email.com','Rua das Flores, 100 - São Paulo/SP'),
('Maria Oliveira','$2b$10$bsggD78dGRaHNDAG42jEwu7aPq/utYq/OIk1bqaDFPECHp2yoTthG','(11) 97777-2222','maria@email.com','Av. Paulista, 2000 - São Paulo/SP'),
('Pedro Santos','$2b$10$hceDyXaqS2nBr69H/FWUZuwqw3sBhxfin.Zzi4tVisZ4NWCNZVC3K','(11) 96666-3333','pedro@email.com','Rua Augusta, 350 - São Paulo/SP');

INSERT INTO aparelhos (cliente_id, imei, marca, modelo, cor, defeito) VALUES
(1,'356938035643809','Samsung','Galaxy A54','Preto','Tela trincada após queda'),
(2,'490154203237518','Apple','iPhone 12','Branco','Bateria descarrega rápido'),
(3,'353918101234567','Motorola','Moto G84','Azul','Não carrega, conector com mau contato');

INSERT INTO servicos (descricao, valor) VALUES
('Troca de tela',450.00),
('Troca de bateria',220.00),
('Reparo do conector de carga',150.00);

INSERT INTO agendamentos (aparelho_id, servico_id, data_agendamento, status, observacao) VALUES
(1,1,'2026-11-03 09:00:00','AGENDADO','Cliente prefere atendimento pela manhã'),
(2,2,'2026-11-01 14:30:00','AGENDADO','Fazer backup antes do reparo'),
(3,3,'2026-11-05 10:00:00','AGENDADO',NULL);
