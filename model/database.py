from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from PyQt6.QtCore import QTimer

# Create the base class for declarative models
Base = declarative_base()

# Database configuration
DB_PATH = 'cubesat_budget.db'
ENGINE = create_engine(f'sqlite:///{DB_PATH}', echo=True)
Session = sessionmaker(bind=ENGINE)
session = Session()

# Auto-save timer
auto_save_timer = QTimer()

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    link_budgets = relationship("LinkBudget", back_populates="project")
    data_budgets = relationship("DataBudget", back_populates="project")

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