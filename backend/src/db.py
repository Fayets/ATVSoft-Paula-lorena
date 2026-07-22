import time

from pony.orm import *

db = Database()
_db_bound = False


def ensure_db_bound() -> bool:
    """Enlaza Pony con Postgres cuando existe `DATABASE_URL` o variables DB_* en `.env`."""
    global _db_bound
    if _db_bound:
        return True
    from src.setup_env import load_db_bind_kwargs

    kwargs = load_db_bind_kwargs()
    if not kwargs:
        return False
    db.bind(**kwargs)
    _db_bound = True
    return True


def init_db() -> None:
    if not ensure_db_bound():
        raise RuntimeError(
            "Base de datos no configurada. Configurá DATABASE_URL o "
            "DB_PROVIDER/DB_HOST (y user/pass/name) en backend/.env."
        )

    t0 = time.time()
    print("[db] Inicializando base de datos...")

    import src.models  # noqa: F401 — registrar entidades Pony antes del mapping

    db.generate_mapping(create_tables=False, check_tables=False)

    with db_session:
        for col, tipo in [
            ("conversaciones_stories", "INTEGER NOT NULL DEFAULT 0"),
            ("conversaciones_reels", "INTEGER NOT NULL DEFAULT 0"),
            ("agendas_stories", "INTEGER NOT NULL DEFAULT 0"),
            ("agendas_reels", "INTEGER NOT NULL DEFAULT 0"),
            ("agendas_ads", "INTEGER NOT NULL DEFAULT 0"),
            ("links_enviados_stories", "INTEGER NOT NULL DEFAULT 0"),
            ("links_enviados_reels", "INTEGER NOT NULL DEFAULT 0"),
        ]:
            db.execute(f"""
                ALTER TABLE setter_report
                ADD COLUMN IF NOT EXISTS {col} {tipo}
            """)

        for col, tipo in [
            ("shows_organico", "INTEGER NOT NULL DEFAULT 0"),
            ("shows_ads", "INTEGER NOT NULL DEFAULT 0"),
            ("cierres_organico", "INTEGER NOT NULL DEFAULT 0"),
            ("cierres_ads", "INTEGER NOT NULL DEFAULT 0"),
            ("reservas", "INTEGER NOT NULL DEFAULT 0"),
            ("seguimiento", "INTEGER NOT NULL DEFAULT 0"),
            ("facturacion", "DOUBLE PRECISION NOT NULL DEFAULT 0"),
        ]:
            db.execute(f"""
                ALTER TABLE closer_report
                ADD COLUMN IF NOT EXISTS {col} {tipo}
            """)

        for col, tipo in [
            ("ingresos_rango", "VARCHAR DEFAULT ''"),
            ("email", "VARCHAR DEFAULT ''"),
            ("objetivo", "VARCHAR DEFAULT ''"),
            ("situacion_actual", "TEXT DEFAULT ''"),
            ("reto_actual", "TEXT DEFAULT ''"),
        ]:
            db.execute(f"""
                ALTER TABLE lead
                ADD COLUMN IF NOT EXISTS {col} {tipo}
            """)

        db.execute("""
            ALTER TABLE app_sync_settings
            ADD COLUMN IF NOT EXISTS calendly_interval_minutes INTEGER NOT NULL DEFAULT 360
        """)

    db.create_tables(check_tables=True)

    print(f"[db] Base de datos lista ({time.time() - t0:.1f}s)")
