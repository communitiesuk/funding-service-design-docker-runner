from app.db import db
from app.db.models.round import Round


def add_round(round: Round) -> Round:
    db.session.add(round)
    db.session.commit()
    return round


def get_round_by_id(id: str) -> Round:
    query = db.session.query(Round).where(Round.round_id == id)
    return query.one_or_none()
