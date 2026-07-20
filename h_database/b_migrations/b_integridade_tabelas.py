#!/usr/bin/env python3
"""
Migration 002: Integridade das tabelas e índices

Este script:
1. Verifica conflitos nas tabelas (transacoes, metas, investimentos, configuracoes_usuario)
2. Adiciona FOREIGN KEYs para usuarios(id)
3. Altera usuario_id para NOT NULL onde necessário
4. Adiciona índices em usuario_id para performance
"""

import sys
from c_generate_rpa.d_load import obter_engine
from sqlalchemy import text


def verificar_conflitos(conn):
    """Verifica conflitos que impedem a migration"""
    conflitos = []

    # Verificar metas com usuario_id NULL
    result = conn.execute(text("SELECT COUNT(*) FROM metas WHERE usuario_id IS NULL"))
    count = result.scalar()
    if count > 0:
        conflitos.append(f"Existem {count} metas sem usuário associado (usuario_id IS NULL)")

    # Verificar metas ligadas a usuários inexistentes
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM metas m
        LEFT JOIN usuarios u ON u.id = m.usuario_id
        WHERE u.id IS NULL AND m.usuario_id IS NOT NULL
    """))
    count = result.scalar()
    if count > 0:
        conflitos.append(f"Existem {count} metas ligadas a usuários inexistentes")

    # Verificar investimentos com usuario_id NULL
    result = conn.execute(text("SELECT COUNT(*) FROM investimentos WHERE usuario_id IS NULL"))
    count = result.scalar()
    if count > 0:
        conflitos.append(f"Existem {count} investimentos sem usuário associado (usuario_id IS NULL)")

    # Verificar investimentos ligados a usuários inexistentes
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM investimentos i
        LEFT JOIN usuarios u ON u.id = i.usuario_id
        WHERE u.id IS NULL AND i.usuario_id IS NOT NULL
    """))
    count = result.scalar()
    if count > 0:
        conflitos.append(f"Existem {count} investimentos ligados a usuários inexistentes")

    # Verificar transacoes ligadas a usuários inexistentes
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM transacoes t
        LEFT JOIN usuarios u ON u.id = t.usuario_id
        WHERE u.id IS NULL AND t.usuario_id IS NOT NULL
    """))
    count = result.scalar()
    if count > 0:
        conflitos.append(f"Existem {count} transações ligadas a usuários inexistentes")

    # Verificar configuracoes_usuario ligadas a usuários inexistentes
    result = conn.execute(text("""
        SELECT COUNT(*)
        FROM configuracoes_usuario c
        LEFT JOIN usuarios u ON u.id = c.usuario_id
        WHERE u.id IS NULL AND c.usuario_id IS NOT NULL
    """))
    count = result.scalar()
    if count > 0:
        conflitos.append(f"Existem {count} configurações ligadas a usuários inexistentes")

    return conflitos


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

        # 2. Ajustar tabela transacoes
        print("\n🔧 Ajustando tabela transacoes...")
        # Adicionar FOREIGN KEY
        conn.execute(text("""
            ALTER TABLE transacoes
            ADD CONSTRAINT fk_transacoes_usuario
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        """))
        # Adicionar índice em usuario_id
        conn.execute(text("CREATE INDEX idx_transacoes_usuario_id ON transacoes(usuario_id)"))
        # Adicionar índice em data_transacao (usado para ordenação)
        conn.execute(text("CREATE INDEX idx_transacoes_data_transacao ON transacoes(data_transacao DESC)"))
        print("✅ Tabela transacoes ajustada.")

        # 3. Ajustar tabela metas
        print("\n🔧 Ajustando tabela metas...")
        # Alterar usuario_id para NOT NULL
        conn.execute(text("ALTER TABLE metas MODIFY COLUMN usuario_id INT NOT NULL"))
        # Adicionar FOREIGN KEY
        conn.execute(text("""
            ALTER TABLE metas
            ADD CONSTRAINT fk_metas_usuario
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        """))
        # Adicionar índice em usuario_id
        conn.execute(text("CREATE INDEX idx_metas_usuario_id ON metas(usuario_id)"))
        print("✅ Tabela metas ajustada.")

        # 4. Ajustar tabela investimentos
        print("\n🔧 Ajustando tabela investimentos...")
        # Alterar usuario_id para NOT NULL
        conn.execute(text("ALTER TABLE investimentos MODIFY COLUMN usuario_id INT NOT NULL"))
        # Adicionar FOREIGN KEY
        conn.execute(text("""
            ALTER TABLE investimentos
            ADD CONSTRAINT fk_investimentos_usuario
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        """))
        # Adicionar índice em usuario_id
        conn.execute(text("CREATE INDEX idx_investimentos_usuario_id ON investimentos(usuario_id)"))
        # Adicionar índice em data_aplicacao (usado para ordenação)
        conn.execute(text("CREATE INDEX idx_investimentos_data_aplicacao ON investimentos(data_aplicacao DESC)"))
        print("✅ Tabela investimentos ajustada.")

        # 5. Ajustar tabela configuracoes_usuario
        print("\n🔧 Ajustando tabela configuracoes_usuario...")
        # Adicionar FOREIGN KEY
        conn.execute(text("""
            ALTER TABLE configuracoes_usuario
            ADD CONSTRAINT fk_configuracoes_usuario
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        """))
        print("✅ Tabela configuracoes_usuario ajustada.")

        print("\n🎉 Migration aplicada com sucesso!")
        return True


def rollback():
    """Desfaz a migration"""
    engine = obter_engine()

    with engine.begin() as conn:
        print("🔄 Iniciando rollback...")

        # 1. Desfazer tabela configuracoes_usuario
        try:
            conn.execute(text("ALTER TABLE configuracoes_usuario DROP FOREIGN KEY fk_configuracoes_usuario"))
            print("✅ FOREIGN KEY de configuracoes_usuario removida.")
        except Exception as e:
            print(f"⚠️ Não foi possível remover FOREIGN KEY de configuracoes_usuario: {e}")

        # 2. Desfazer tabela investimentos
        try:
            conn.execute(text("ALTER TABLE investimentos DROP FOREIGN KEY fk_investimentos_usuario"))
            conn.execute(text("DROP INDEX idx_investimentos_usuario_id ON investimentos"))
            conn.execute(text("DROP INDEX idx_investimentos_data_aplicacao ON investimentos"))
            conn.execute(text("ALTER TABLE investimentos MODIFY COLUMN usuario_id INT NULL"))
            print("✅ Tabela investimentos revertida.")
        except Exception as e:
            print(f"⚠️ Não foi possível reverter tabela investimentos: {e}")

        # 3. Desfazer tabela metas
        try:
            conn.execute(text("ALTER TABLE metas DROP FOREIGN KEY fk_metas_usuario"))
            conn.execute(text("DROP INDEX idx_metas_usuario_id ON metas"))
            conn.execute(text("ALTER TABLE metas MODIFY COLUMN usuario_id INT NULL"))
            print("✅ Tabela metas revertida.")
        except Exception as e:
            print(f"⚠️ Não foi possível reverter tabela metas: {e}")

        # 4. Desfazer tabela transacoes
        try:
            conn.execute(text("ALTER TABLE transacoes DROP FOREIGN KEY fk_transacoes_usuario"))
            conn.execute(text("DROP INDEX idx_transacoes_usuario_id ON transacoes"))
            conn.execute(text("DROP INDEX idx_transacoes_data_transacao ON transacoes"))
            print("✅ Tabela transacoes revertida.")
        except Exception as e:
            print(f"⚠️ Não foi possível reverter tabela transacoes: {e}")

        print("\n✅ Rollback concluído!")


def main():
    if len(sys.argv) == 1:
        print("Uso:")
        print("  python h_database/b_migrations/b_integridade_tabelas.py migrate  # Aplicar migration")
        print("  python h_database/b_migrations/b_integridade_tabelas.py rollback # Desfazer migration")
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
