from datetime import date
from typing import Dict, List
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.dialects.postgresql.json import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Date, Integer

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

    insurance_info_records: Mapped[List["SQLAlchemyInsuranceInfoCatalogue"]] = (
        relationship(
            "SQLAlchemyInsuranceInfoCatalogue",
            back_populates="financing_source",
            lazy="selectin",
            cascade="all, delete-orphan",
        )
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


class SQLAlchemyInsuranceInfoCatalogue(Base, ChangedAtMixin, CreatedAtMixin):
    __tablename__ = "cat_insurance_info"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    policy_number: Mapped[str] = mapped_column(
        String(50), nullable=True, comment="Insurance policy number"
    )
    company: Mapped[str] = mapped_column(
        String(100), nullable=True, comment="Insurance company name"
    )
    valid_from: Mapped[date] = mapped_column(
        Date, nullable=True, comment="Insurance valid from"
    )
    valid_till: Mapped[date] = mapped_column(
        Date, nullable=True, comment="Insurance valid till"
    )
    comment: Mapped[str] = mapped_column(
        String(256), nullable=True, comment="Insurance comment"
    )

    # Relations with different tables
    patient_id: Mapped[UUID] = mapped_column(
        ForeignKey("patients.id"), nullable=False, comment="Insurance ID"
    )
    patient: Mapped["SQLAlchemyPatient"] = relationship(  # noqa: F821
        "SQLAlchemyPatient",
        back_populates="insurances",
        lazy="selectin",
    )

    financing_source_id: Mapped[int] = mapped_column(
        ForeignKey("cat_financing_sources.id"),
        nullable=False,
        comment="Financing source ID",
    )
    financing_source: Mapped["SQLAlchemyFinancingSourcesCatalog"] = relationship(
        "SQLAlchemyFinancingSourcesCatalog",
        back_populates="insurance_info_records",
        lazy="selectin",
    )
