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
