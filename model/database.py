from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from PyQt6.QtCore import QTimer
from .base import Base

# Database configuration
DB_PATH = 'cubesat_budget.db'
ENGINE = create_engine(f'sqlite:///{DB_PATH}', echo=True)
Session = sessionmaker(bind=ENGINE)
session = Session()

# Auto-save timer
auto_save_timer = QTimer()

class LinkBudget(Base):
    __tablename__ = 'link_budgets'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    frequency = Column(Float)
    tx_power = Column(Float)
    tx_antenna_gain = Column(Float)
    rx_antenna_gain = Column(Float)
    path_loss = Column(Float)
    propagation_model = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="link_budgets")

class DataBudget(Base):
    __tablename__ = 'data_budgets'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    data_generated = Column(Float)
    downlink_capacity = Column(Float)
    storage_capacity = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="data_budgets")

def init_db():
    """Initialize the database, creating all tables."""
    # Import here to avoid circular import
    from .project import Project
    Base.metadata.create_all(ENGINE)

def auto_save():
    try:
        session.commit()
    except Exception as e:
        print(f"Auto-save failed: {e}")
        session.rollback()

# Connect auto-save timer
auto_save_timer.timeout.connect(auto_save)

# Create tables when module is imported
init_db() 