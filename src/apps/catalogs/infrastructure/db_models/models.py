from typing import Dict

from sqlalchemy import String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Integer

from src.shared.infrastructure.base import Base, ChangedAtMixin, CreatedAtMixin


class SQLAlchemyCitizenshipCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_citizenship"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    country_code: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        unique=True,
        comment="Citizenship country code (ISO)",
    )
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Citizenship default name"
    )
    lang: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="Citizenship default language"
    )

    name_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Citizenship's name additional locales",
    )


class SQLAlchemyNationalitiesCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_nationalities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Nationality default name"
    )
    lang: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="Nationality default language"
    )

    name_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Nationality's name additional locales",
    )


class SQLAlchemyPatientContextAttributesCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_patient_context_attributes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="Patient context attribute default name"
    )
    lang: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="Patient context attribute default language"
    )

    name_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Patient context attribute's name additional locales",
    )


class SQLAlchemyFinancingSourcesCatalog(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_financing_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Financing source default name",
        unique=True,
    )
    code: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="Financing source code", unique=True
    )
    lang: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="Financing source default language"
    )

    name_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Financing source's name additional locales",
    )


class SQLAlchemyMedicalOrganizationsCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_medical_organizations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    code: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Medical organization internal code",
        unique=True,
    )
    name: Mapped[str] = mapped_column(
        String(256),
        nullable=False,
        comment="Medical organization default name",
        unique=True,
    )
    address: Mapped[str] = mapped_column(
        String(256), nullable=False, comment="Medical organization default address"
    )
    lang: Mapped[str] = mapped_column(
        String(5), nullable=False, comment="Medical organization default language"
    )

    name_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Medical organization's name additional locales",
    )
    address_locales: Mapped[Dict[str, str]] = mapped_column(
        JSONB,
        nullable=True,
        comment="Medical organization's address additional locales",
    )
