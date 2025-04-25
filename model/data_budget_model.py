from dataclasses import dataclass
from typing import List, Dict

@dataclass
class DataBudgetResult:
    """Data class to hold data budget calculation results."""
    total_data_per_day: float  # in GB
    available_downlink_per_day: float  # in GB
    storage_backlog: float  # in GB
    storage_status: str
    recommendations: List[str]

class DataBudgetModel:
    """Model class for data budget calculations."""
    
    def __init__(self):
        self._parameters = {
            'payload_data_rate': 0.0,  # Mbps
            'storage_capacity': 0.0,   # GB
            'downlink_rate': 0.0,      # Mbps
            'pass_duration': 0.0,      # minutes
            'passes_per_day': 0.0      # count
        }
    
    def set_parameters(self, params: Dict[str, float]) -> None:
        """Update model parameters."""
        self._parameters.update(params)
    
    def calculate(self) -> DataBudgetResult:
        """Calculate data budget based on current parameters."""
        self._validate_inputs()
        
        # Calculate total data generated per day (GB)
        data_per_day = (self._parameters['payload_data_rate'] * 3600 * 24) / (8 * 1024)
        
        # Calculate available downlink capacity per day (GB)
        downlink_per_pass = (self._parameters['downlink_rate'] * self._parameters['pass_duration'] * 60) / (8 * 1024)
        total_downlink = downlink_per_pass * self._parameters['passes_per_day']
        
        # Calculate storage backlog
        daily_backlog = data_per_day - total_downlink
        storage_status = "Normal"
        recommendations = []
        
        if daily_backlog > 0:
            days_until_full = self._parameters['storage_capacity'] / daily_backlog
            storage_status = f"Warning: Storage will be full in {days_until_full:.1f} days"
            recommendations = self._generate_recommendations(daily_backlog, data_per_day, total_downlink)
        
        return DataBudgetResult(
            total_data_per_day=data_per_day,
            available_downlink_per_day=total_downlink,
            storage_backlog=daily_backlog,
            storage_status=storage_status,
            recommendations=recommendations
        )
    
    def _validate_inputs(self) -> None:
        """Validate input parameters."""
        if any(v < 0 for v in self._parameters.values()):
            raise ValueError("All parameters must be non-negative.")
        if self._parameters['storage_capacity'] == 0:
            raise ValueError("Storage capacity must be greater than zero.")
        if self._parameters['payload_data_rate'] == 0:
            raise ValueError("Payload data rate must be greater than zero.")
    
    def _generate_recommendations(self, backlog: float, generation: float, downlink: float) -> List[str]:
        """Generate recommendations based on calculations."""
        recommendations = ["Data budget improvements needed:"]
        
        if backlog > 0:
            if generation > downlink * 2:
                recommendations.append("• Consider reducing payload data generation rate")
            
            needed_passes = (generation * 8 * 1024) / (self._parameters['downlink_rate'] * self._parameters['pass_duration'] * 60)
            if needed_passes > self._parameters['passes_per_day']:
                recommendations.append(f"• Increase number of ground station passes (need {needed_passes:.1f} passes/day)")
            
            if self._parameters['downlink_rate'] < 10:
                recommendations.append("• Consider upgrading downlink rate capability")
            
            if self._parameters['storage_capacity'] < backlog * 7:  # Less than a week of storage
                recommendations.append("• Consider increasing onboard storage capacity")
        
        return recommendations 