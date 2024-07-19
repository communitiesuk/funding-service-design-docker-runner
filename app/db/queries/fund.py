from sqlalchemy import select

from app.db import db
from app.db.models.fund import Fund


def add_fund(fund: Fund) -> Fund:
    db.session.add(fund)
    db.session.commit()
    return fund


def get_all_funds() -> list:
    stmt = select(Fund).order_by(Fund.short_name)
    return db.session.scalars(stmt).all()


def get_fund_by_id(id: str) -> Fund:
    return db.session.get(Fund, id)
