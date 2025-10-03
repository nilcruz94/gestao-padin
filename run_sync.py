# run_sync.py
import os
import sys
import traceback

print("➡️  Python:", sys.version)
print("➡️  CWD   :", os.getcwd())

# 1) Tenta importar direto de um app.py monolítico
try:
    from app import app, db, User, Agendamento, TRE, sync_tre_user
    print("✅ Import direto de app.py OK.")
except Exception as e:
    print("❌ Falha ao importar direto de app.py:", e)
    traceback.print_exc()
    # 2) Fallback: caso seu projeto fosse em formato pacote (app/__init__.py)
    try:
        from app import create_app, db  # type: ignore
        from app.models import User, Agendamento, TRE  # type: ignore
        from app.utils import sync_tre_user  # type: ignore
        app = create_app()  # type: ignore
        print("✅ Import via factory OK.")
    except Exception as e2:
        print("\n❌ Não consegui importar sua app de jeito nenhum.")
        print("   Dicas:")
        print("   - Confirme que ESTE arquivo (run_sync.py) está na MESMA pasta do seu app.py")
        print("   - Rode:  python -c \"import app; print('ok')\"  e veja se importa")
        print("   - Evite ter uma pasta chamada 'app/' e um arquivo 'app.py' ao mesmo tempo (conflito de nomes).")
        print("   - Se seu app for um pacote (app/__init__.py), ajuste os imports conforme seu layout.")
        print("\nStacktrace:")
        traceback.print_exc()
        sys.exit(1)

# ---------- Aqui começa a sincronização ----------
def run():
    with app.app_context():
        usuarios = User.query.order_by(User.nome.asc()).all()
        total_users = len(usuarios)
        print(f"\n🔄 Iniciando sincronização de {total_users} usuário(s)...\n")

        ok = 0
        fail = 0

        for i, u in enumerate(usuarios, start=1):
            try:
                total, usadas, rest = sync_tre_user(u.id)
                print(f"[{i}/{total_users}] {u.id:>4} | {u.nome} -> Total={total} | Usufruídas={usadas} | Restantes={rest}")
                ok += 1
            except Exception as e:
                print(f"[{i}/{total_users}] ❌ ERRO no usuário id={u.id} ({u.nome}): {e}")
                traceback.print_exc()
                fail += 1

        print(f"\n✅ Concluído. Sucessos: {ok} | Falhas: {fail}")

if __name__ == "__main__":
    run()
