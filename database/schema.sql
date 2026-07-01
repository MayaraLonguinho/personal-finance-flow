
USE personal_finance_flow;

CREATE TABLE usuarios (
id INT AUTO_INCREMENT PRIMARY KEY,
nome VARCHAR(255) NOT NULL,
email VARCHAR(255) NOT NULL UNIQUE,
telefone VARCHAR(20),
senha_hash VARCHAR(255) NOT NULL,
criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transacoes (
id INT AUTO_INCREMENT PRIMARY KEY,
usuario_id INT NOT NULL,
data_transacao DATE NOT NULL,
descricao VARCHAR(255) NOT NULL,
categoria VARCHAR(100),
tipo ENUM('entrada','saida','investimento') NOT NULL,
valor DECIMAL(12,2) NOT NULL,
conta VARCHAR(100),
instituicao VARCHAR(100),
status ENUM('confirmado','pendente','cancelado') DEFAULT 'pendente',
criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categorias (
id INT AUTO_INCREMENT PRIMARY KEY,
usuario_id INT NOT NULL,
nome VARCHAR(100) NOT NULL,
palavras_chave TEXT,
cor VARCHAR(20),
criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
UNIQUE (usuario_id,nome)
);

CREATE TABLE metas (
id INT AUTO_INCREMENT PRIMARY KEY,
usuario_id INT NOT NULL,
titulo VARCHAR(255) NOT NULL,
valor_meta DECIMAL(12,2) NOT NULL,
valor_atual DECIMAL(12,2) DEFAULT 0.00,
data_limite DATE,
status ENUM('ativa','concluida','cancelada') DEFAULT 'ativa',
criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE investimentos (
id INT AUTO_INCREMENT PRIMARY KEY,
usuario_id INT NOT NULL,
nome VARCHAR(150) NOT NULL,
tipo VARCHAR(80) NOT NULL,
instituicao VARCHAR(120),
valor_aplicado DECIMAL(12,2) NOT NULL,
valor_atual DECIMAL(12,2) NOT NULL,
rentabilidade_percentual DECIMAL(8,2) DEFAULT 0.00,
data_aplicacao DATE NOT NULL,
data_vencimento DATE,
status ENUM('ativo','resgatado','cancelado') DEFAULT 'ativo',
criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE configuracoes_usuario (
id INT AUTO_INCREMENT PRIMARY KEY,
usuario_id INT NOT NULL UNIQUE,
nome VARCHAR(150),
tema VARCHAR(50) DEFAULT 'theme-pink',
moeda VARCHAR(10) DEFAULT 'BRL',
formato_data VARCHAR(20) DEFAULT 'DD/MM/YYYY',
qtd_transacoes_recentes INT DEFAULT 5,
confirmar_exclusao TINYINT(1) DEFAULT 1,
cards_visiveis TEXT,
criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

SHOW TABLES;

DESCRIBE usuarios;
DESCRIBE transacoes;
DESCRIBE categorias;
DESCRIBE metas;
DESCRIBE investimentos;
DESCRIBE configuracoes_usuario;

-- Lista todos os usuários cadastrados no sistema.
SELECT * FROM usuarios;

-- Lista todas as transações cadastradas.
SELECT * FROM transacoes;

-- Lista todas as categorias cadastradas por usuário.
SELECT * FROM categorias;

-- Lista todas as metas financeiras cadastradas.
SELECT * FROM metas;

-- Lista todos os investimentos cadastrados.
SELECT * FROM investimentos;

-- Lista todas as configurações salvas para os usuários.
SELECT * FROM configuracoes_usuario;

-- Mostra os tipos de transação existentes no banco.
SELECT DISTINCT tipo FROM transacoes;

-- Mostra os status existentes nas transações.
SELECT DISTINCT status FROM transacoes;

-- Exibe os principais dados dos investimentos.
SELECT
id,
usuario_id,
nome,
tipo,
instituicao,
valor_aplicado,
valor_atual,
rentabilidade_percentual,
status
FROM investimentos;

-- Exibe os principais dados das metas.
SELECT
id,
usuario_id,
titulo,
valor_meta,
valor_atual,
data_limite,
status
FROM metas;

-- Exibe as categorias organizadas por usuário e nome.
SELECT
id,
usuario_id,
nome,
palavras_chave,
cor
FROM categorias
ORDER BY usuario_id,nome;

-- Exibe as transações da mais recente para a mais antiga.
SELECT
id,
usuario_id,
data_transacao,
descricao,
categoria,
tipo,
valor,
conta,
instituicao,
status
FROM transacoes
ORDER BY data_transacao DESC;

-- Mostra a quantidade de transações cadastradas por usuário.
SELECT
usuario_id,
COUNT(*) AS quantidade_transacoes
FROM transacoes
GROUP BY usuario_id;

-- Mostra o total de entradas, saídas e investimentos por usuário.
SELECT
usuario_id,
tipo,
SUM(valor) AS valor_total
FROM transacoes
GROUP BY usuario_id,tipo;

-- Mostra quais categorias pertencem a cada usuário.
SELECT
u.nome AS usuario,
c.nome AS categoria
FROM usuarios u
INNER JOIN categorias c
ON c.usuario_id = u.id
ORDER BY u.nome,c.nome;

-- Mostra as metas relacionadas aos usuários.
SELECT
u.nome AS usuario,
m.titulo,
m.valor_meta,
m.valor_atual,
m.status
FROM usuarios u
INNER JOIN metas m
ON m.usuario_id = u.id
ORDER BY u.nome,m.titulo;

-- Mostra os investimentos relacionados aos usuários.
SELECT
u.nome AS usuario,
i.nome AS investimento,
i.tipo,
i.valor_aplicado,
i.valor_atual,
i.status
FROM usuarios u
INNER JOIN investimentos i
ON i.usuario_id = u.id
ORDER BY u.nome,i.nome;