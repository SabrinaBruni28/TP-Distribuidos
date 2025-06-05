BEGIN TRANSACTION;
DROP TABLE IF EXISTS "usuario";
CREATE TABLE IF NOT EXISTS "usuario" (
	"id_usuario"	INTEGER NOT NULL,
	"cpf_usuario"	TEXT NOT NULL UNIQUE,
	"nome_usuario"	TEXT NOT NULL,
	"email_usuario"	TEXT NOT NULL UNIQUE,
	"senha_usuario"	TEXT NOT NULL,
	PRIMARY KEY("id_usuario" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "endereco";
CREATE TABLE IF NOT EXISTS "endereco" (
	"id_endereco"	INTEGER NOT NULL,
	"id_usuario"	INTEGER,
	"rua_endereco"	TEXT NOT NULL,
	"numero_endereco"	INTEGER NOT NULL,
	"bairro_endereco"	TEXT NOT NULL,
	"cidade_endereco"	TEXT NOT NULL,
	"estado_endereco"	TEXT NOT NULL,
	"complemento_endereco"	TEXT,
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario"),
	PRIMARY KEY("id_endereco")
);
DROP TABLE IF EXISTS "anuncio";
CREATE TABLE IF NOT EXISTS "anuncio" (
	"id_anuncio"	INTEGER NOT NULL,
	"id_produto"	INTEGER NOT NULL,
	"preco_anuncio"	NUMERIC NOT NULL,
	"quantidade_produto"	INTEGER NOT NULL,
	"chave_pix"	TEXT NOT NULL,
	"pausado"	INTEGER NOT NULL,
	PRIMARY KEY("id_anuncio" AUTOINCREMENT),
	FOREIGN KEY("id_produto") REFERENCES "produto"("id_produto")
);
DROP TABLE IF EXISTS "pedido";
CREATE TABLE IF NOT EXISTS "pedido" (
	"id_pedido"	INTEGER NOT NULL,
	"id_anuncio"	INTEGER NOT NULL,
	"id_endereco"	INTEGER NOT NULL,
	"quantidade_pedido"	INTEGER NOT NULL,
	"data_pedido"	INTEGER NOT NULL,
	"confirmacao_pedido"	INTEGER NOT NULL DEFAULT 0,
	FOREIGN KEY("id_endereco") REFERENCES "endereco"("id_endereco"),
	FOREIGN KEY("id_anuncio") REFERENCES "anuncio"("id_anuncio"),
	PRIMARY KEY("id_pedido" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "produto";
CREATE TABLE IF NOT EXISTS "produto" (
	"id_produto"	INTEGER NOT NULL,
	"id_loja"	INTEGER,
	"nome_produto"	TEXT NOT NULL,
	"descricao_produto"	TEXT,
	PRIMARY KEY("id_produto" AUTOINCREMENT),
	FOREIGN KEY("id_loja") REFERENCES "loja"("id_loja")
);
DROP TABLE IF EXISTS "imagem_produto";
CREATE TABLE IF NOT EXISTS "imagem_produto" (
	"id_imagem_produto"	INTEGER NOT NULL,
	"id_produto"	INTEGER NOT NULL,
	PRIMARY KEY("id_imagem_produto" AUTOINCREMENT),
	FOREIGN KEY("id_produto") REFERENCES "produto"("id_produto")
);
DROP TABLE IF EXISTS "loja";
CREATE TABLE IF NOT EXISTS "loja" (
	"id_loja"	INTEGER NOT NULL,
	"id_usuario"	INTEGER NOT NULL,
	"nome_loja"	TEXT NOT NULL,
	PRIMARY KEY("id_loja" AUTOINCREMENT),
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario")
);
DROP TRIGGER IF EXISTS "on_criar_pedido";
CREATE TRIGGER on_criar_pedido
AFTER INSERT ON pedido
FOR EACH ROW
BEGIN
    -- 1. Subtrair a quantidade do anúncio
    UPDATE anuncio
    SET quantidade_produto = quantidade_produto - NEW.quantidade_pedido
    WHERE id_anuncio = NEW.id_anuncio;

    -- 2. Pausar o anúncio se a quantidade chegar a 0 ou menos
    UPDATE anuncio
    SET pausado = 1
    WHERE id_anuncio = NEW.id_anuncio
      AND quantidade_produto <= 0;
END;
DROP TRIGGER IF EXISTS "on_apagar_pedido";
CREATE TRIGGER on_apagar_pedido
AFTER DELETE ON pedido
FOR EACH ROW
BEGIN
    -- 1. Subtrair a quantidade do anúncio
    UPDATE anuncio
    SET quantidade_produto = quantidade_produto + OLD.quantidade_pedido
    WHERE id_anuncio = OLD.id_anuncio;

    -- 2. Pausar o anúncio se a quantidade chegar a 0 ou menos
    UPDATE anuncio
    SET pausado = 0
    WHERE id_anuncio = OLD.id_anuncio
      AND quantidade_produto > 0;
END;
COMMIT;
