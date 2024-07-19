# from __future__ import annotations

import uuid
from dataclasses import dataclass
from enum import Enum
from typing import List

from flask_sqlalchemy.model import DefaultMeta
from sqlalchemy import Column
from sqlalchemy import ForeignKey
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.orderinglist import ordering_list
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean

from app.db import db

BaseModel: DefaultMeta = db.Model


class ComponentType(Enum):
    TEXT_FIELD = "TextField"
    FREE_TEXT_FIELD = "FreeTextField"
    EMAIL_ADDRESS_FIELD = "EmailAddressField"
    UK_ADDRESS_FIELD = "UkAddressField"
    HTML = "Html"
    YES_NO_FIELD = "YesNoField"
    RADIOS_FIELD = "RadiosField"


@dataclass
class Section(BaseModel):

    round_id = Column(
        UUID(as_uuid=True),
        ForeignKey("round.round_id"),
        nullable=True,  # will be null where this is a template and not linked to a round
    )
    section_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name_in_apply_json = Column(JSON(none_as_null=True), nullable=False, unique=False)
    template_name = Column(String(), nullable=True)
    is_template = Column(Boolean, default=False, nullable=False)
    audit_info = Column(JSON(none_as_null=True))
    forms: Mapped[List["Form"]] = relationship(
        "Form", order_by="Form.section_index", collection_class=ordering_list("section_index")
    )
    index = Column(Integer())
    source_template_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"Section({self.name_in_apply_json['en']}, Forms: {self.forms})"

    def as_dict(self):
        return {col.name: self.__getattribute__(col.name) for col in inspect(self).mapper.columns}


@dataclass
class Form(BaseModel):

    section_id = Column(
        UUID(as_uuid=True),
        ForeignKey("section.section_id"),
        nullable=True,  # will be null where this is a template and not linked to a section
    )
    form_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name_in_apply_json = Column(JSON(none_as_null=True), nullable=False, unique=False)
    template_name = Column(String(), nullable=True)
    is_template = Column(Boolean, default=False, nullable=False)
    audit_info = Column(JSON(none_as_null=True))
    section_index = Column(Integer())
    pages: Mapped[List["Page"]] = relationship(
        "Page", order_by="Page.form_index", collection_class=ordering_list("form_index")
    )
    runner_publish_name = Column(db.String())
    source_template_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"Form({self.runner_publish_name} - {self.name_in_apply_json['en']}, Pages: {self.pages})"

    def as_dict(self):
        return {col.name: self.__getattribute__(col.name) for col in inspect(self).mapper.columns}


@dataclass
class Page(BaseModel):

    form_id = Column(
        UUID(as_uuid=True),
        ForeignKey("form.form_id"),
        nullable=True,  # will be null where this is a template and not linked to a form
    )
    page_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name_in_apply_json = Column(JSON(none_as_null=True), nullable=False, unique=False)
    template_name = Column(String(), nullable=True)
    is_template = Column(Boolean, default=False, nullable=False)
    audit_info = Column(JSON(none_as_null=True))
    form_index = Column(Integer())
    display_path = Column(String())
    components: Mapped[List["Component"]] = relationship(
        "Component", order_by="Component.page_index", collection_class=ordering_list("page_index")
    )
    source_template_id = Column(UUID(as_uuid=True), nullable=True)

    def __repr__(self):
        return f"Page(/{self.display_path} - {self.name_in_apply_json['en']}, Components: {self.components})"

    def as_dict(self):
        return {col.name: self.__getattribute__(col.name) for col in inspect(self).mapper.columns}


# Ensure we can only have one template with a particular display_path value
Index("ix_template_page_name", Page.display_path, unique=True, postgresql_where="Page.is_template = true")


class Lizt(BaseModel):
    list_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name = Column(String())
    type = Column(String())
    items = Column(JSON())
    is_template = Column(Boolean, default=False, nullable=False)

    def as_dict(self):
        return {col.name: self.__getattribute__(col.name) for col in inspect(self).mapper.columns}


@dataclass
class Component(BaseModel):

    component_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    page_id = Column(
        UUID(as_uuid=True),
        ForeignKey("page.page_id"),
        nullable=True,  # will be null where this is a template and not linked to a page
    )
    theme_id = Column(
        UUID(as_uuid=True),
        ForeignKey("theme.theme_id"),
        nullable=True,  # will be null where this is a template and not linked to a theme
    )
    # TODO make these 2 json so we can do welsh?
    title = Column(String())
    hint_text = Column(String(), nullable=True)
    options = Column(JSON(none_as_null=False))
    type = Column(ENUM(ComponentType))
    template_name = Column(String(), nullable=True)
    is_template = Column(Boolean, default=False, nullable=False)
    audit_info = Column(JSON(none_as_null=True))
    page_index = Column(Integer())
    theme_index = Column(Integer())
    conditions = Column(JSON(none_as_null=True))
    source_template_id = Column(UUID(as_uuid=True), nullable=True)
    runner_component_name = Column(
        String(), nullable=False
    )  # TODO add validation to make sure it's only letters, numbers and _
    list_id = Column(
        UUID(as_uuid=True),
        ForeignKey("list.list_id"),
        nullable=True,
    )
    list_id: Mapped[int | None] = mapped_column(ForeignKey("lizt.list_id"))
    lizt: Mapped[Lizt | None] = relationship()  # back_populates="used_by")

    def __repr__(self):
        return f"Component({self.title}, {self.type.value})"

    def as_dict(self):
        return {col.name: self.__getattribute__(col.name) for col in inspect(self).mapper.columns}

    @property
    def assessment_display_type(self):
        # TODO extend this to account for what's in self.options eg. if prefix==£, return 'currency'
        return {
            "numberfield": "integer",
            "textfield": "text",
            "yesnofield": "text",
            "freetextfield": "free_text",
            "checkboxesfield": "list",
            "multiinputfield": "table",
            "clientsidefileuploadfield": "s3bucketPath",
            "radiosfield": "text",
            "emailaddressfield": "text",
            "telephonenumberfield": "text",
            "ukaddressfield": "address",
        }.get(self.type.value.casefold())
