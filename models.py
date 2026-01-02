from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from typing import Optional, List
from database import Base

# Association table for Many-to-Many relationship between Ayat and Concept
ayat_concept_association = Table(
    "ayat_concept",
    Base.metadata,
    Column("ayat_id", Integer, ForeignKey("ayat.id"), primary_key=True),
    Column("concept_id", Integer, ForeignKey("concept.id"), primary_key=True),
    # Optional: Column("relationship_type", String) # e.g. "direct", "thematic"
)

class Ayat(Base):
    __tablename__ = "ayat"

    id = Column(Integer, primary_key=True, index=True)
    surah_number = Column(Integer, index=True)
    ayat_number = Column(Integer, index=True)
    arabic_text = Column(Text, nullable=False)
    translation_1 = Column(Text, nullable=True) # First translation
    translation_2 = Column(Text, nullable=True) # Second translation
    
    # Relationships
    concepts = relationship("Concept", secondary=ayat_concept_association, back_populates="ayats")
    reflections = relationship("Reflection", back_populates="ayat")

    def __repr__(self):
        return f"<Ayat {self.surah_number}:{self.ayat_number}>"

class Concept(Base):
    __tablename__ = "concept"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    definition = Column(Text, nullable=True) # Optional definition
    
    # Relationships
    ayats = relationship("Ayat", secondary=ayat_concept_association, back_populates="concepts")

    def __repr__(self):
        return f"<Concept {self.name}>"

class Reflection(Base):
    __tablename__ = "reflection"

    id = Column(Integer, primary_key=True, index=True)
    ayat_id = Column(Integer, ForeignKey("ayat.id"), nullable=False)
    text_content = Column(Text, nullable=False) # The personal note
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    ayat = relationship("Ayat", back_populates="reflections")

    def __repr__(self):
        return f"<Reflection for Ayat {self.ayat_id}>"
