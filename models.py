from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, Table, Boolean
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
)

class Ayat(Base):
    __tablename__ = "ayat"

    id = Column(Integer, primary_key=True, index=True)
    surah_number = Column(Integer, index=True)
    ayat_number = Column(Integer, index=True)
    arabic_text = Column(Text, nullable=False)
    translation_1 = Column(Text, nullable=True)  # Elmalılı
    translation_2 = Column(Text, nullable=True)  # Diyanet
    
    # New fields for scope completion
    is_mekki = Column(Boolean, nullable=True)  # True=Mekki, False=Medeni, None=Unknown
    context_type = Column(String, nullable=True)  # "vaat", "uyari", "anlatim", etc.
    
    # Relationships
    concepts = relationship("Concept", secondary=ayat_concept_association, back_populates="ayats")
    reflections = relationship("Reflection", back_populates="ayat")
    favorites = relationship("Favorite", back_populates="ayat")

    def __repr__(self):
        return f"<Ayat {self.surah_number}:{self.ayat_number}>"

class Concept(Base):
    __tablename__ = "concept"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    definition = Column(Text, nullable=True)
    
    # Relationships
    ayats = relationship("Ayat", secondary=ayat_concept_association, back_populates="concepts")

    def __repr__(self):
        return f"<Concept {self.name}>"

class Reflection(Base):
    __tablename__ = "reflection"

    id = Column(Integer, primary_key=True, index=True)
    ayat_id = Column(Integer, ForeignKey("ayat.id"), nullable=False)
    text_content = Column(Text, nullable=False)
    concept_tag = Column(String, nullable=True)  # Optional concept tag for the reflection
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    ayat = relationship("Ayat", back_populates="reflections")

    def __repr__(self):
        return f"<Reflection for Ayat {self.ayat_id}>"

class Favorite(Base):
    """User's favorite/bookmarked ayats"""
    __tablename__ = "favorite"

    id = Column(Integer, primary_key=True, index=True)
    ayat_id = Column(Integer, ForeignKey("ayat.id"), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    # Relationships
    ayat = relationship("Ayat", back_populates="favorites")

    def __repr__(self):
        return f"<Favorite Ayat {self.ayat_id}>"

class UserPreference(Base):
    """Store user preferences like last read position"""
    __tablename__ = "user_preference"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)  # e.g. "last_read_surah", "last_read_ayat"
    value = Column(String, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<UserPreference {self.key}={self.value}>"

class ReadingFlow(Base):
    """Predefined guided reading flows"""
    __tablename__ = "reading_flow"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # e.g. "Kur'an'da Allah kendini nasıl anlatır?"
    description = Column(Text, nullable=True)
    
    # Relationship to flow steps
    steps = relationship("ReadingFlowStep", back_populates="flow", order_by="ReadingFlowStep.order")

    def __repr__(self):
        return f"<ReadingFlow {self.title}>"

class ReadingFlowStep(Base):
    """Steps within a reading flow"""
    __tablename__ = "reading_flow_step"

    id = Column(Integer, primary_key=True, index=True)
    flow_id = Column(Integer, ForeignKey("reading_flow.id"), nullable=False)
    order = Column(Integer, nullable=False)  # Step order
    ayat_id = Column(Integer, ForeignKey("ayat.id"), nullable=False)
    reflection_question = Column(Text, nullable=True)  # Question to ponder
    
    # Relationships
    flow = relationship("ReadingFlow", back_populates="steps")
    ayat = relationship("Ayat")

    def __repr__(self):
        return f"<ReadingFlowStep {self.flow_id}:{self.order}>"

class NuzulSebebi(Base):
    """Occasion/reason of revelation for verses - from Al-Wahidi's Asbab al-Nuzul"""
    __tablename__ = "nuzul_sebebi"

    id = Column(Integer, primary_key=True, index=True)
    surah_number = Column(Integer, index=True, nullable=False)
    ayat_number = Column(Integer, index=True, nullable=False)
    text_en = Column(Text, nullable=True)  # English text from Al-Wahidi
    source = Column(String, default="Al-Wahidi")  # Source attribution
    
    def __repr__(self):
        return f"<NuzulSebebi {self.surah_number}:{self.ayat_number}>"

# Association table for Many-to-Many ayat cross-references
ayat_reference_association = Table(
    "ayat_reference",
    Base.metadata,
    Column("source_ayat_id", Integer, ForeignKey("ayat.id"), primary_key=True),
    Column("target_ayat_id", Integer, ForeignKey("ayat.id"), primary_key=True),
    Column("reference_type", String, nullable=True),  # "tefsir", "theme", "similar"
)

