import uuid
from dataclasses import dataclass

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean

from app.db import db
from app.db.models import Criteria
from app.db.models import Section

BaseModel: DefaultMeta = db.Model


@dataclass
class Round(BaseModel):
    __table_args__ = (UniqueConstraint("fund_id", "short_name"),)
    round_id = Column(
        "round_id",
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    fund_id = Column(
        "fund_id",
        UUID(as_uuid=True),
        ForeignKey("fund.fund_id"),
        nullable=False,
    )
    title_json = Column("title_json", JSON(none_as_null=True), nullable=False, unique=False)
    short_name = Column("short_name", db.String(), nullable=False, unique=False)
    opens = Column("opens", DateTime())
    deadline = Column("deadline", DateTime())
    assessment_start = Column("assessment_start", DateTime())
    reminder_date = Column("reminder_date", DateTime())
    assessment_deadline = Column("assessment_deadline", DateTime())
    prospectus_link = Column("prospectus", db.String(), nullable=False, unique=False)
    privacy_notice_link = Column("privacy_notice", db.String(), nullable=False, unique=False)
    audit_info = Column("audit_info", JSON(none_as_null=True))
    is_template = Column("is_template", Boolean, default=False, nullable=False)
    sections: Mapped[list["Section"]] = relationship("Section")
    criteria: Mapped[list["Criteria"]] = relationship("Criteria")
    # several other fields to add
