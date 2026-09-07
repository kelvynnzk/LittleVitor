ALTER TABLE usuarios
  ADD COLUMN email_verificado TINYINT(1) NOT NULL DEFAULT 0,
  ADD COLUMN token_verificacao VARCHAR(64) NULL;
