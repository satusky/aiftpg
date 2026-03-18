from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    submissions = relationship("Submission", back_populates="team")


class Variable(Base):
    __tablename__ = "variables"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ground_truths = relationship("GroundTruth", back_populates="variable")
    submissions = relationship("Submission", back_populates="variable")


class GroundTruth(Base):
    __tablename__ = "ground_truths"

    id = Column(Integer, primary_key=True)
    variable_id = Column(String, ForeignKey("variables.id"), nullable=False)
    document_id = Column(Text, nullable=False)
    value = Column(Text, nullable=True)

    variable = relationship("Variable", back_populates="ground_truths")

    __table_args__ = (
        UniqueConstraint("variable_id", "document_id", name="uq_gt_var_doc"),
    )


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    variable_id = Column(String, ForeignKey("variables.id"), nullable=False)
    extracted_values = Column(JSON, nullable=False)
    extra_fields = Column(JSON, nullable=True)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1 = Column(Float, nullable=True)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    team = relationship("Team", back_populates="submissions")
    variable = relationship("Variable", back_populates="submissions")

    __table_args__ = (
        Index("ix_submission_team_var_f1", "team_id", "variable_id", f1.desc()),
    )
