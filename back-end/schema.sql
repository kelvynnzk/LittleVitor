-- ============================================================
-- SCHEMA COMPLETO DO BANCO — LittleVitor
-- ============================================================
-- Esse arquivo cria as 4 tabelas do zero, já com todas as colunas
-- que o projeto usa hoje (login, verificação de e-mail, perfil,
-- eventos, ingressos e pagamentos reais via Mercado Pago).
--
-- Como usar (quem estiver clonando o projeto pela primeira vez):
--   1. Crie um banco vazio no seu MySQL/XAMPP (ex: "teste", o mesmo
--      nome que já está configurado em back-end/test_conect.py).
--   2. Rode esse arquivo inteiro nele — pelo phpMyAdmin ("Importar"),
--      ou por linha de comando:
--         mysql -u root teste < schema.sql
--   3. Pronto — as 4 tabelas já ficam criadas com a estrutura atual.
--
-- Os arquivos schema_compras.sql, schema_verificacao_email.sql,
-- schema_pagamentos.sql, schema_perfil.sql, schema_redefinir_senha.sql
-- e schema_imagem_evento.sql continuam no projeto só como histórico de
-- como o banco foi evoluindo (eram rodados um a um, com ALTER
-- TABLE, conforme cada funcionalidade nova era criada) — quem está
-- começando do zero não precisa rodar nenhum deles, só este arquivo.
-- ============================================================

CREATE TABLE usuarios (
  id INT NOT NULL AUTO_INCREMENT,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL,
  senha_hash VARCHAR(255) NOT NULL,
  criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  email_verificado TINYINT(1) NOT NULL DEFAULT 0,
  token_verificacao VARCHAR(64) DEFAULT NULL,
  telefone VARCHAR(20) DEFAULT NULL,
  cidade VARCHAR(100) DEFAULT NULL,
  token_redefinicao_senha VARCHAR(64) DEFAULT NULL,
  token_redefinicao_expira DATETIME DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE eventos (
  id INT NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(150) NOT NULL,
  categoria VARCHAR(50) DEFAULT NULL,
  descricao TEXT DEFAULT NULL,
  data DATE NOT NULL,
  horario TIME DEFAULT NULL,
  local VARCHAR(150) DEFAULT NULL,
  cidade VARCHAR(100) DEFAULT NULL,
  usuario_id INT NOT NULL,
  criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  imagem VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (id),
  KEY usuario_id (usuario_id),
  CONSTRAINT eventos_ibfk_1 FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE tipos_ingresso (
  id INT NOT NULL AUTO_INCREMENT,
  evento_id INT NOT NULL,
  nome VARCHAR(100) NOT NULL,
  preco DECIMAL(10,2) NOT NULL,
  quantidade_total INT NOT NULL,
  quantidade_vendida INT NOT NULL DEFAULT 0,
  PRIMARY KEY (id),
  KEY evento_id (evento_id),
  CONSTRAINT tipos_ingresso_ibfk_1 FOREIGN KEY (evento_id) REFERENCES eventos (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE compras (
  id INT NOT NULL AUTO_INCREMENT,
  tipo_ingresso_id INT NOT NULL,
  usuario_id INT NOT NULL,
  quantidade INT NOT NULL,
  valor_total DECIMAL(10,2) NOT NULL,
  nome_titular VARCHAR(150) NOT NULL,
  email_titular VARCHAR(150) NOT NULL,
  criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  mp_payment_id VARCHAR(50) DEFAULT NULL,
  forma_pagamento VARCHAR(20) DEFAULT NULL,
  PRIMARY KEY (id),
  UNIQUE KEY mp_payment_id (mp_payment_id),
  KEY tipo_ingresso_id (tipo_ingresso_id),
  KEY usuario_id (usuario_id),
  CONSTRAINT compras_ibfk_1 FOREIGN KEY (tipo_ingresso_id) REFERENCES tipos_ingresso (id),
  CONSTRAINT compras_ibfk_2 FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
