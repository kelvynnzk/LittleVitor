CREATE TABLE tipos_ingresso (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evento_id INT NOT NULL,
    nome VARCHAR(100) NOT NULL,
    preco DECIMAL(10,2) NOT NULL,
    quantidade_total INT NOT NULL,
    quantidade_vendida INT NOT NULL DEFAULT 0,
    FOREIGN KEY (evento_id) REFERENCES eventos(id) ON DELETE CASCADE
);

CREATE TABLE compras (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_ingresso_id INT NOT NULL,
    usuario_id INT NOT NULL,
    quantidade INT NOT NULL,
    valor_total DECIMAL(10,2) NOT NULL,
    nome_titular VARCHAR(150) NOT NULL,
    email_titular VARCHAR(150) NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_ingresso_id) REFERENCES tipos_ingresso(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);
