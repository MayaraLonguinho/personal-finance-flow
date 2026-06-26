-- Uso do banco de dados
USE personal_finance_flow;

-- Tabela de transações
CREATE TABLE IF NOT EXISTS transacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    data_transacao DATE NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    categoria VARCHAR(100),
    tipo ENUM('entrada', 'saida', 'investimento') NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    conta VARCHAR(100),
    instituicao VARCHAR(100),
    status ENUM('confirmado', 'pendente', 'cancelado') DEFAULT 'pendente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de metas
CREATE TABLE IF NOT EXISTS metas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    valor_meta DECIMAL(10, 2) NOT NULL,
    valor_atual DECIMAL(10, 2) DEFAULT 0.00,
    data_limite DATE,
    status ENUM('ativa', 'concluida', 'cancelada') DEFAULT 'ativa',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabela de categorias
CREATE TABLE IF NOT EXISTS categorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    palavras_chave TEXT,
    cor VARCHAR(20),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- tabela de investimentos
CREATE TABLE IF NOT EXISTS investimentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(150) NOT NULL,
    tipo VARCHAR(80) NOT NULL,
    instituicao VARCHAR(120),
    valor_aplicado DECIMAL(12,2) NOT NULL,
    valor_atual DECIMAL(12,2) NOT NULL,
    rentabilidade_percentual DECIMAL(8,2) DEFAULT 0,
    data_aplicacao DATE NOT NULL,
    data_vencimento DATE NULL,
    status ENUM('ativo', 'resgatado', 'cancelado') NOT NULL DEFAULT 'ativo',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
