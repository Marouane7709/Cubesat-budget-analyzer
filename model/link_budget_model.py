import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass
class LinkBudgetResult:
    """Data class to hold link budget calculation results."""
    received_power: float
    noise_power: float
    carrier_to_noise: float
    bit_error_rate: float
    link_margin: float
    status: str
    recommendations: List[str]

class LinkBudgetModel:
    """Model class for link budget calculations."""
    
    def __init__(self):
        self._parameters = {
            'transmit_power': 0.0,
            'transmit_antenna_gain': 0.0,
            'receive_antenna_gain': 0.0,
            'frequency': 0.0,
            'distance': 5000.0,
            'system_temperature': 290.0,
            'receiver_bandwidth': 0.0,
            'required_snr': 0.0,
            'atmospheric_loss': 0.0
        }
    
    def set_parameters(self, params: Dict[str, float]) -> None:
        """Update model parameters."""
        self._parameters.update(params)
    
    def calculate(self) -> LinkBudgetResult:
        """Calculate link budget based on current parameters."""
        self._validate_inputs()
        
        # Calculate key metrics
        fsl = self._calculate_free_space_loss()
        received_power = self._calculate_received_power(fsl)
        noise_power = self._calculate_noise_power()
        snr = received_power - noise_power
        link_margin = snr - self._parameters['required_snr']
        ber = self._calculate_bit_error_rate(snr, link_margin)
        
        # Get status and recommendations
        status, recommendations = self._get_status_and_recommendations(link_margin)
        
        return LinkBudgetResult(
            received_power=received_power,
            noise_power=noise_power,
            carrier_to_noise=snr,
            bit_error_rate=ber,
            link_margin=link_margin,
            status=status,
            recommendations=recommendations
        )
    
    def _validate_inputs(self) -> None:
        """Validate input parameters."""
        if all(v == 0 for v in self._parameters.values()):
            raise ValueError("All input values are zero. Please enter valid values.")
        if self._parameters['frequency'] == 0:
            raise ValueError("Frequency cannot be zero.")
        if self._parameters['distance'] == 0:
            raise ValueError("Free Space Path Loss cannot be zero.")
    
    def _calculate_free_space_loss(self) -> float:
        """Calculate free space path loss."""
        wavelength = 3e8 / (self._parameters['frequency'] * 1e9)
        return 20 * np.log10(4 * np.pi * self._parameters['distance'] * 1000 / wavelength)
    
    def _calculate_received_power(self, fsl: float) -> float:
        """Calculate received power."""
        return (
            self._parameters['transmit_power'] +
            self._parameters['transmit_antenna_gain'] +
            self._parameters['receive_antenna_gain'] -
            fsl -
            self._parameters['atmospheric_loss']
        )
    
    def _calculate_noise_power(self) -> float:
        """Calculate noise power."""
        return -228.6 + 10 * np.log10(self._parameters['system_temperature']) + \
               10 * np.log10(self._parameters['receiver_bandwidth'] * 1e6)
    
    def _calculate_bit_error_rate(self, snr: float, link_margin: float) -> float:
        """Calculate bit error rate."""
        return 0.5 * np.exp(-np.power(10, (link_margin - snr) / 10) / 2)
    
    def _get_status_and_recommendations(self, link_margin: float) -> Tuple[str, List[str]]:
        """Get link status and improvement recommendations."""
        if link_margin >= 0:
            return " Link margin sufficient — stable connection expected", []
        
        required_improvement = abs(link_margin)
        hints = ["To improve the link:"]
        
        if self._parameters['transmit_power'] < 10:
            hints.append(f"• Increase transmit power by {required_improvement:.1f} dB")
        if self._parameters['transmit_antenna_gain'] < 5:
            hints.append(f"• Increase antenna gain by {required_improvement/2:.1f} dBi")
        if self._parameters['distance'] > 1000:
            hints.append(f"• Reduce link distance by {self._parameters['distance'] * 0.1:.0f} km")
        
        return " Negative link margin — connection unstable", hints
    
    def calculate_margin_vs_parameter(self, param_type: str, value: float, modulation: str = None) -> float:
        """Calculate link margin for different parameters."""
        if param_type == "Frequency":
            return self._calculate_margin_vs_frequency(value)
        elif param_type == "Distance":
            return self._calculate_margin_vs_distance(value)
        elif param_type == "Modulation" and modulation:
            return self._calculate_margin_vs_modulation(value, modulation)
        raise ValueError(f"Invalid parameter type: {param_type}")
    
    def _calculate_margin_vs_frequency(self, freq_ghz: float) -> float:
        """Calculate link margin for a given frequency."""
        wavelength = 3e8 / (freq_ghz * 1e9)
        fsl = 20 * np.log10(4 * np.pi * self._parameters['distance'] * 1000 / wavelength)
        return self._calculate_received_power(fsl)
    
    def _calculate_margin_vs_distance(self, distance_km: float) -> float:
        """Calculate link margin for a given distance."""
        wavelength = 3e8 / (self._parameters['frequency'] * 1e9)
        fsl = 20 * np.log10(4 * np.pi * distance_km * 1000 / wavelength)
        return self._calculate_received_power(fsl)
    
    def _calculate_margin_vs_modulation(self, mod_index: float, scheme: str) -> float:
        """Calculate link margin for different modulation schemes."""
        base_margin = self._calculate_margin_vs_distance(self._parameters['distance'])
        mod_penalties = {
            "QPSK": 0,
            "8PSK": -3,
            "16QAM": -6,
            "64QAM": -9
        }
        return base_margin + mod_penalties.get(scheme, 0) - (mod_index * 0.5) 