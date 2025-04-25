from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
import numpy as np
from datetime import datetime, timedelta

@dataclass
class DataBudgetResult:
    data_generated: float  # MB/day
    downlink_capacity: float  # MB/day
    storage_required: float  # MB
    storage_available: float  # MB
    backlog: float  # MB
    days_until_full: Optional[float]
    recommendations: List[str]

class DataBudgetCalculator:
    def __init__(self):
        self.MB_TO_BITS = 8 * 1024 * 1024  # Conversion factor
    
    def calculate(self,
                 data_rate: float,  # bits/second
                 duty_cycle: float,  # percentage (0-100)
                 downlink_rate: float,  # bits/second
                 downlink_duration: float,  # hours/day
                 storage_capacity: float,  # MB
                 current_storage: float = 0  # MB
                 ) -> DataBudgetResult:
        """
        Calculate data budget parameters.
        
        Args:
            data_rate: Data generation rate in bits/second
            duty_cycle: Percentage of time generating data (0-100)
            downlink_rate: Downlink data rate in bits/second
            downlink_duration: Hours of downlink per day
            storage_capacity: Total storage capacity in MB
            current_storage: Current used storage in MB
            
        Returns:
            DataBudgetResult containing all calculated parameters and recommendations
        """
        # Calculate daily data generation
        seconds_per_day = 24 * 3600
        data_generated = (data_rate * duty_cycle/100 * seconds_per_day) / self.MB_TO_BITS
        
        # Calculate daily downlink capacity
        downlink_capacity = (downlink_rate * downlink_duration * 3600) / self.MB_TO_BITS
        
        # Calculate storage requirements
        storage_required = current_storage + data_generated
        storage_available = storage_capacity - storage_required
        
        # Calculate backlog
        backlog = max(0, data_generated - downlink_capacity)
        
        # Calculate days until storage is full
        if data_generated > downlink_capacity:
            daily_accumulation = data_generated - downlink_capacity
            days_until_full = storage_available / daily_accumulation
        else:
            days_until_full = None
        
        # Generate recommendations
        recommendations = []
        if backlog > 0:
            recommendations.append(
                f"Warning: Daily data generation ({data_generated:.1f} MB) exceeds "
                f"downlink capacity ({downlink_capacity:.1f} MB)"
            )
        
        if storage_available < 0:
            recommendations.append(
                f"Critical: Storage capacity ({storage_capacity:.1f} MB) exceeded"
            )
        elif storage_available < storage_capacity * 0.1:
            recommendations.append(
                f"Warning: Less than 10% storage remaining ({storage_available:.1f} MB)"
            )
        
        if days_until_full is not None and days_until_full < 30:
            recommendations.append(
                f"Warning: Storage will be full in {days_until_full:.1f} days"
            )
        
        return DataBudgetResult(
            data_generated=data_generated,
            downlink_capacity=downlink_capacity,
            storage_required=storage_required,
            storage_available=storage_available,
            backlog=backlog,
            days_until_full=days_until_full,
            recommendations=recommendations
        )

    def calculate_data_budget(self, params: Dict[str, Any]) -> DataBudgetResult:
        """Calculate complete data budget based on input parameters."""
        recommendations = []
        
        # Extract parameters
        data_rate_mbps = params['data_rate']  # Mbps
        storage_capacity_mb = params['storage_capacity']  # MB
        mission_duration_hours = params['mission_duration']  # hours
        downlink_opportunities = params['downlink_opportunities']  # list of windows
        
        # Converting to bytes
        data_rate_bps = data_rate_mbps * 1e6
        storage_capacity_bytes = storage_capacity_mb * self.MB_TO_BITS
        
        # Calculate total data generated in bytes
        mission_duration_seconds = mission_duration_hours * 3600
        total_data_generated = data_rate_bps * mission_duration_seconds / self.MB_TO_BITS
        
        # Calculate the downlink capacity
        total_downlink_capacity = self._calculate_downlink_capacity(
            downlink_opportunities, params)
        
        # Calculate storage requirements
        max_storage_required = self._calculate_max_storage(
            data_rate_bps, downlink_opportunities, mission_duration_hours)
        
        storage_margin = storage_capacity_bytes - max_storage_required
        is_viable = storage_margin >= 0
        
        # Generate recommendations
        if not is_viable:
            recommendations.extend([
                f"Increase storage capacity by at least {abs(storage_margin)/self.MB_TO_BITS:.1f} MB",
                "Consider reducing data generation rate during non-downlink periods",
                "Add more downlink opportunities if possible"
            ])
        elif storage_margin < storage_capacity_bytes * 0.2:
            recommendations.append(
                "Storage margin is less than 20% of capacity - consider increasing storage"
            )
        
        # Generate timeline for visualization
        timeline = self._generate_timeline(
            data_rate_bps, downlink_opportunities, mission_duration_hours)
        
        return DataBudgetResult(
            data_generated=total_data_generated,
            downlink_capacity=total_downlink_capacity,
            storage_required=max_storage_required,
            storage_available=storage_margin,
            backlog=max(0, total_data_generated - total_downlink_capacity),
            days_until_full=None if total_data_generated <= total_downlink_capacity else (storage_margin / (total_data_generated - total_downlink_capacity)),
            recommendations=recommendations,
            timeline=timeline
        )
    
    def _calculate_downlink_capacity(
        self, opportunities: List[Dict], params: Dict[str, Any]) -> float:
        """Calculate total downlink capacity across all opportunities."""
        downlink_rate_bps = params.get('downlink_rate', 1e6)  # default 1 Mbps
        total_bytes = 0
        
        for window in opportunities:
            start_time = datetime.fromisoformat(window['start'])
            end_time = datetime.fromisoformat(window['end'])
            duration_seconds = (end_time - start_time).total_seconds()
            total_bytes += downlink_rate_bps * duration_seconds / self.MB_TO_BITS
        
        return total_bytes
    
    def _calculate_max_storage(
        self, data_rate_bps: float, opportunities: List[Dict], 
        mission_duration_hours: float) -> float:
        """Calculate maximum storage required between downlinks."""
        timeline = self._generate_timeline(
            data_rate_bps, opportunities, mission_duration_hours)
        return max(point[1] for point in timeline)
    
    def _generate_timeline(
        self, data_rate_bps: float, opportunities: List[Dict],
        mission_duration_hours: float) -> List[Tuple[datetime, float]]:
        """Generate timeline of cumulative data storage."""
        timeline = []
        current_time = datetime.now()
        end_time = current_time + timedelta(hours=mission_duration_hours)
        
        # Sort opportunities by start time
        opportunities = sorted(
            opportunities, 
            key=lambda x: datetime.fromisoformat(x['start'])
        )
        
        cumulative_data = 0
        last_time = current_time
        
        for window in opportunities:
            window_start = datetime.fromisoformat(window['start'])
            window_end = datetime.fromisoformat(window['end'])
            
            # Add data accumulated until window start
            data_generated = (
                (window_start - last_time).total_seconds() * data_rate_bps / self.MB_TO_BITS
            )
            cumulative_data += data_generated
            timeline.append((window_start, cumulative_data))
            
            # Subtract downlinked data during window
            downlink_rate_bps = window.get('downlink_rate', 1e6)
            data_downlinked = (
                (window_end - window_start).total_seconds() * 
                downlink_rate_bps / self.MB_TO_BITS
            )
            cumulative_data = max(0, cumulative_data - data_downlinked)
            timeline.append((window_end, cumulative_data))
            
            last_time = window_end
        
        # Add final point
        if last_time < end_time:
            data_generated = (
                (end_time - last_time).total_seconds() * data_rate_bps / self.MB_TO_BITS
            )
            cumulative_data += data_generated
            timeline.append((end_time, cumulative_data))
        
        return timeline 