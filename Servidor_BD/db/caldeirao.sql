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
	PRIMARY KEY("id_endereco"),
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario")
);
DROP TABLE IF EXISTS "endereco_pedido";
CREATE TABLE IF NOT EXISTS "endereco_pedido" (
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
	FOREIGN KEY("id_produto") REFERENCES "produto"("id_produto"),
	PRIMARY KEY("id_anuncio" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "produto";
CREATE TABLE IF NOT EXISTS "produto" (
	"id_produto"	INTEGER NOT NULL,
	"id_loja"	INTEGER,
	"nome_produto"	TEXT NOT NULL,
	"descricao_produto"	TEXT,
	FOREIGN KEY("id_loja") REFERENCES "loja"("id_loja"),
	PRIMARY KEY("id_produto" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "produto_pedido";
CREATE TABLE IF NOT EXISTS "produto_pedido" (
	"id_produto"	INTEGER NOT NULL,
	"id_loja"	INTEGER,
	"nome_produto"	TEXT NOT NULL,
	"descricao_produto"	TEXT,
	FOREIGN KEY("id_loja") REFERENCES "loja"("id_loja"),
	PRIMARY KEY("id_produto" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "loja";
CREATE TABLE IF NOT EXISTS "loja" (
	"id_loja"	INTEGER NOT NULL,
	"id_usuario"	INTEGER NOT NULL,
	"nome_loja"	TEXT NOT NULL,
	FOREIGN KEY("id_usuario") REFERENCES "usuario"("id_usuario"),
	PRIMARY KEY("id_loja" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "pedido_andamento";
CREATE TABLE IF NOT EXISTS "pedido_andamento" (
	"id_pedido"	INTEGER NOT NULL,
	"id_anuncio"	INTEGER NOT NULL,
	"id_endereco"	INTEGER NOT NULL,
	"quantidade_pedido"	INTEGER NOT NULL,
	"data_pedido"	INTEGER NOT NULL,
	FOREIGN KEY("id_anuncio") REFERENCES "anuncio"("id_anuncio"),
	FOREIGN KEY("id_endereco") REFERENCES "endereco"("id_endereco"),
	PRIMARY KEY("id_pedido" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "pedido_confirmado";
CREATE TABLE IF NOT EXISTS "pedido_confirmado" (
	"id_pedido"	INTEGER NOT NULL,
	"id_anuncio"	INTEGER NOT NULL,
	"id_endereco"	INTEGER NOT NULL,
	"quantidade_pedido"	INTEGER NOT NULL,
	"data_pedido"	INTEGER NOT NULL,
	PRIMARY KEY("id_pedido" AUTOINCREMENT),
	FOREIGN KEY("id_anuncio") REFERENCES "anuncio_pedido"("id_anuncio"),
	FOREIGN KEY("id_endereco") REFERENCES "endereco_pedido"("id_endereco")
);
DROP TABLE IF EXISTS "imagem_pedido";
CREATE TABLE IF NOT EXISTS "imagem_pedido" (
	"id_imagem"	INTEGER NOT NULL,
	"id_produto"	INTEGER NOT NULL,
	PRIMARY KEY("id_imagem" AUTOINCREMENT),
	FOREIGN KEY("id_produto") REFERENCES "produto_pedido"("id_produto")
);
DROP TABLE IF EXISTS "imagem_produto";
CREATE TABLE IF NOT EXISTS "imagem_produto" (
	"id_imagem"	INTEGER NOT NULL,
	"id_produto"	INTEGER NOT NULL,
	FOREIGN KEY("id_produto") REFERENCES "produto"("id_produto"),
	PRIMARY KEY("id_imagem" AUTOINCREMENT)
);
DROP TABLE IF EXISTS "anuncio_pedido";
CREATE TABLE IF NOT EXISTS "anuncio_pedido" (
	"id_anuncio"	INTEGER NOT NULL,
	"id_produto"	INTEGER NOT NULL,
	"preco_anuncio"	NUMERIC NOT NULL,
	PRIMARY KEY("id_anuncio" AUTOINCREMENT),
	FOREIGN KEY("id_produto") REFERENCES "produto_pedido"("id_produto")
);
DROP TRIGGER IF EXISTS "on_update_quantidade_produto";
CREATE TRIGGER on_update_quantidade_produto
AFTER UPDATE OF quantidade_produto ON anuncio
FOR EACH ROW
BEGIN
    -- Pausar se a nova quantidade for 0 ou menor
    UPDATE anuncio
    SET pausado = 1
    WHERE id_anuncio = NEW.id_anuncio
      AND NEW.quantidade_produto <= 0;

    -- Despausar se a nova quantidade for positiva
    UPDATE anuncio
    SET pausado = 0
    WHERE id_anuncio = NEW.id_anuncio
      AND NEW.quantidade_produto > 0;
END;
COMMIT;
