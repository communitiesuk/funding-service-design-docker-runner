from app.db import db
from app.db.models.fund import Fund


def add_fund(fund: Fund) -> Fund:
    db.session.add(fund)
    db.session.commit()
    return fund


def get_all_funds() -> list:
    query = db.session.query(Fund).order_by(Fund.short_name)
    return query.all()


def get_fund_by_id(id: str) -> Fund:
    query = db.session.query(Fund).where(Fund.fund_id == id)
    return query.one_or_none()
