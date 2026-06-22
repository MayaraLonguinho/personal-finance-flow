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
