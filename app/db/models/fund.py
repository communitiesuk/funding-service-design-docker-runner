import uuid
from dataclasses import dataclass
from typing import List

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean

from app.db import db

from .round import Round

BaseModel: DefaultMeta = db.Model


@dataclass
class Fund(BaseModel):
    fund_id = Column(
        "fund_id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    name_json = Column("name_json", JSON(none_as_null=True), nullable=False, unique=False)
    title_json = Column("title_json", JSON(none_as_null=True), nullable=False, unique=False)
    short_name = Column("short_name", db.String(), nullable=False, unique=True)
    description_json = Column("description_json", JSON(none_as_null=True), nullable=False, unique=False)
    rounds: Mapped[List["Round"]] = relationship("Round")
    welsh_available = Column("welsh_available", Boolean, default=False, nullable=False)
    is_template = Column("is_template", Boolean, default=False, nullable=False)
    audit_info = Column("audit_info", JSON(none_as_null=True))
