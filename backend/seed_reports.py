import sys
sys.path.insert(0, '.')

from src.db import init_db
from src.models import SetterReport, CloserReport
from pony.orm import db_session
from datetime import date, datetime

init_db()

with db_session:
    # Setter report
    SetterReport(
        user_id=1,
        member_id=1,
        fecha=date(2026, 7, 4),
        conversaciones=15,
        agendas=8,
        links_enviados=10,
        conversaciones_stories=9,
        conversaciones_reels=6,
        agendas_stories=5,
        agendas_reels=3,
        agendas_ads=0,
        links_enviados_stories=6,
        links_enviados_reels=4,
        sentimiento_trafico="Buen tráfico hoy",
        avatar_tipo_agendas="Dueño de negocio",
        insights_marketing="Los reels de objeción funcionan bien",
        created_at=datetime.utcnow(),
    )

    # Closer report
    CloserReport(
        user_id=1,
        member_id=1,
        fecha=date(2026, 7, 4),
        reporte_tipo="ventas",
        llamadas_agendadas=8,
        shows=6,
        cierres=3,
        calificados=5,
        descalificados=1,
        ingreso=9000,
        shows_organico=4,
        shows_ads=2,
        cierres_organico=2,
        cierres_ads=1,
        reservas=2,
        seguimiento=2,
        facturacion=12000,
        notas="Buen día, 2 reservas de 300€",
        created_at=datetime.utcnow(),
    )

print("Seed completado.")
