ALTER TABLE usuarios
  ADD COLUMN token_redefinicao_senha VARCHAR(64) DEFAULT NULL,
  ADD COLUMN token_redefinicao_expira DATETIME DEFAULT NULL;
