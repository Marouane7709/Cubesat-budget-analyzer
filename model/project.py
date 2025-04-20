from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from .database import Base

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Link Budget Parameters
    frequency = Column(Float)
    transmit_power = Column(Float)
    transmit_antenna_gain = Column(Float)
    receive_antenna_gain = Column(Float)
    distance = Column(Float)
    system_noise_temp = Column(Float)
    propagation_model = Column(String(50))
    link_margin = Column(Float)
    
    # Data Budget Parameters
    data_rate = Column(Float)
    storage_capacity = Column(Float)
    mission_duration = Column(Float)
    downlink_opportunities = Column(JSON)  # Store as JSON array of time windows
    
    # Results and Analysis
    link_budget_results = Column(JSON)  # Store detailed calculation results
    data_budget_results = Column(JSON)  # Store data analysis results
    
    def to_dict(self):
        """Convert project to dictionary for JSON export."""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'frequency': self.frequency,
            'transmit_power': self.transmit_power,
            'transmit_antenna_gain': self.transmit_antenna_gain,
            'receive_antenna_gain': self.receive_antenna_gain,
            'distance': self.distance,
            'system_noise_temp': self.system_noise_temp,
            'propagation_model': self.propagation_model,
            'link_margin': self.link_margin,
            'data_rate': self.data_rate,
            'storage_capacity': self.storage_capacity,
            'mission_duration': self.mission_duration,
            'downlink_opportunities': self.downlink_opportunities,
            'link_budget_results': self.link_budget_results,
            'data_budget_results': self.data_budget_results
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create project from dictionary (for JSON import)."""
        # Remove timestamps if present
        data.pop('created_at', None)
        data.pop('updated_at', None)
        return cls(**data) 