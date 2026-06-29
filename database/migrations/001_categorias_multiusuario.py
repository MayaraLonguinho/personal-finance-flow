#!/usr/bin/env python3
"""
Migration 001: Correção do modelo multiusuário das categorias

Este script:
1. Verifica conflitos no banco de dados
2. Aplica as alterações no schema
3. Permite rollback

Conflitos que impedem a execução:
- Categorias com usuario_id IS NULL
- Categorias ligadas a usuários inexistentes
- Duplicações de (usuario_id, nome)
"""

import sys
from src.load import obter_engine
from sqlalchemy import text


def verificar_conflitos(conn):
    """Verifica se existem conflitos que impedem a migration"""
    conflitos = []

    # 1. Verificar categorias com usuario_id IS NULL
    result = conn.execute(text("SELECT COUNT(*) FROM categorias WHERE usuario_id IS NULL"))
    count = result.scalar()
    if count > 0:
        conflitos.append(f"Existem {count} categorias sem usuário associado (usuario_id IS NULL)")

    # 2. Verificar categorias ligadas a usuários inexistentes
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM categorias c
        LEFT JOIN usuarios u ON u.id = c.usuario_id
        WHERE u.id IS NULL AND c.usuario_id IS NOT NULL
    """))
    count = result.scalar()
    if count > 0:
        conflitos.append(f"Existem {count} categorias ligadas a usuários inexistentes")

    # 3. Verificar duplicações de (usuario_id, nome)
    result = conn.execute(text("""
        SELECT usuario_id, nome, COUNT(*) as qtd
        FROM categorias
        GROUP BY usuario_id, nome
        HAVING COUNT(*) > 1
    """))
    duplicatas = result.fetchall()
    if duplicatas:
        msg = f"Existem {len(duplicatas)} duplicações de nome por usuário:"
        for dup in duplicatas:
            msg += f"\n  - usuario_id={dup[0]}, nome='{dup[1]}' (x{dup[2]})"
        conflitos.append(msg)

    return conflitos


def obter_nome_constraint_unique_nome(conn):
    """Obtém o nome da constraint UNIQUE na coluna nome"""
    result = conn.execute(text("""
        SELECT CONSTRAINT_NAME
        FROM information_schema.TABLE_CONSTRAINTS
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'categorias'
          AND CONSTRAINT_TYPE = 'UNIQUE'
    """))
    constraints = result.fetchall()
    
    # Encontrar a constraint que envolve apenas a coluna 'nome'
    for (constraint_name,) in constraints:
        result_cols = conn.execute(text("""
            SELECT COLUMN_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = 'categorias'
              AND CONSTRAINT_NAME = :constraint_name
            ORDER BY ORDINAL_POSITION
        """), {'constraint_name': constraint_name})
        cols = [row[0] for row in result_cols]
        if cols == ['nome']:
            return constraint_name
    
    return None


def aplicar_migration():
    """Aplica a migration"""
    engine = obter_engine()
    
    with engine.begin() as conn:
        # 1. Verificar conflitos
        print("🔍 Verificando conflitos...")
        conflitos = verificar_conflitos(conn)
        if conflitos:
            print("\n❌ Conflitos encontrados! A migration não pode ser executada:")
            for c in conflitos:
                print(f"  - {c}")
            print("\nResolva os conflitos manualmente antes de continuar.")
            return False

        print("✅ Nenhum conflito encontrado.")

        # 2. Obter nome da constraint UNIQUE de nome
        print("\n📋 Buscando constraint UNIQUE da coluna 'nome'...")
        constraint_name = obter_nome_constraint_unique_nome(conn)
        if not constraint_name:
            print("⚠️ Constraint UNIQUE na coluna 'nome' não encontrada. Pulando remoção.")
        else:
            print(f"✅ Encontrada constraint: {constraint_name}")
            conn.execute(text(f"ALTER TABLE categorias DROP INDEX {constraint_name}"))
            print("✅ Constraint UNIQUE global removida.")

        # 3. Alterar usuario_id para NOT NULL
        print("\n🔧 Alterando usuario_id para NOT NULL...")
        conn.execute(text("ALTER TABLE categorias MODIFY COLUMN usuario_id INT NOT NULL"))
        print("✅ usuario_id definido como NOT NULL.")

        # 4. Adicionar Foreign Key para usuarios(id)
        print("\n🔗 Adicionando Foreign Key...")
        conn.execute(text("""
            ALTER TABLE categorias
            ADD CONSTRAINT fk_categorias_usuario
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        """))
        print("✅ Foreign Key adicionada.")

        # 5. Adicionar UNIQUE (usuario_id, nome)
        print("\n🔒 Adicionando constraint UNIQUE composta...")
        conn.execute(text("""
            ALTER TABLE categorias
            ADD CONSTRAINT uk_categorias_usuario_nome
            UNIQUE (usuario_id, nome)
        """))
        print("✅ Constraint UNIQUE composta adicionada.")

        print("\n🎉 Migration aplicada com sucesso!")
        return True


def rollback():
    """Desfaz a migration"""
    engine = obter_engine()
    
    with engine.begin() as conn:
        print("🔄 Iniciando rollback...")

        # 1. Remover constraint UNIQUE composta
        try:
            conn.execute(text("ALTER TABLE categorias DROP INDEX uk_categorias_usuario_nome"))
            print("✅ Constraint UNIQUE composta removida.")
        except Exception as e:
            print(f"⚠️ Não foi possível remover constraint UNIQUE composta: {e}")

        # 2. Remover Foreign Key
        try:
            conn.execute(text("ALTER TABLE categorias DROP FOREIGN KEY fk_categorias_usuario"))
            print("✅ Foreign Key removida.")
        except Exception as e:
            print(f"⚠️ Não foi possível remover Foreign Key: {e}")

        # 3. Alterar usuario_id para NULL
        try:
            conn.execute(text("ALTER TABLE categorias MODIFY COLUMN usuario_id INT NULL"))
            print("✅ usuario_id definido como NULL.")
        except Exception as e:
            print(f"⚠️ Não foi possível alterar usuario_id para NULL: {e}")

        # 4. Recriar constraint UNIQUE global em nome
        try:
            conn.execute(text("""
                ALTER TABLE categorias
                ADD CONSTRAINT uk_categorias_nome
                UNIQUE (nome)
            """))
            print("✅ Constraint UNIQUE global recriada.")
        except Exception as e:
            print(f"⚠️ Não foi possível recriar constraint UNIQUE global: {e}")

        print("\n✅ Rollback concluído!")


def main():
    if len(sys.argv) == 1:
        print("Uso:")
        print("  python database/migrations/001_categorias_multiusuario.py migrate  # Aplicar migration")
        print("  python database/migrations/001_categorias_multiusuario.py rollback # Desfazer migration")
        sys.exit(1)
    
    comando = sys.argv[1].lower()
    if comando == "migrate":
        sucesso = aplicar_migration()
        sys.exit(0 if sucesso else 1)
    elif comando == "rollback":
        rollback()
        sys.exit(0)
    else:
        print(f"Comando inválido: {comando}")
        sys.exit(1)


if __name__ == "__main__":
    main()
