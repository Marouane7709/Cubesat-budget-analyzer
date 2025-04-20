import numpy as np
from dataclasses import dataclass
from typing import Literal

@dataclass
class LinkBudgetResult:
    received_power: float
    carrier_to_noise: float
    bit_error_rate: float
    margin: float

class LinkBudgetCalculator:
    def __init__(self):
        self.propagation_models = ['AWGN', 'Rayleigh', 'Rician', 'Log-normal']
        
    def calculate(self, 
                 frequency: float,
                 tx_power: float,
                 tx_antenna_gain: float,
                 rx_antenna_gain: float,
                 path_loss: float,
                 noise_temperature: float = 290,  # Default: 290K
                 bandwidth: float = 1e6,  # Default: 1MHz
                 propagation_model: Literal['AWGN', 'Rayleigh', 'Rician', 'Log-normal'] = 'AWGN'
                 ) -> LinkBudgetResult:
        """
        Calculate link budget parameters.
        
        Args:
            frequency: Carrier frequency in Hz
            tx_power: Transmitter power in dBm
            tx_antenna_gain: Transmitter antenna gain in dBi
            rx_antenna_gain: Receiver antenna gain in dBi
            path_loss: Path loss in dB
            noise_temperature: System noise temperature in Kelvin
            bandwidth: Signal bandwidth in Hz
            propagation_model: Channel propagation model
            
        Returns:
            LinkBudgetResult containing received power, C/N, BER, and margin
        """
        if propagation_model != 'AWGN':
            raise NotImplementedError(f"{propagation_model} propagation model not implemented")
            
        # Convert dBm to watts
        tx_power_watts = 10 ** ((tx_power - 30) / 10)
        
        # Calculate received power
        received_power = tx_power_watts * \
                        (10 ** (tx_antenna_gain / 10)) * \
                        (10 ** (rx_antenna_gain / 10)) * \
                        (10 ** (-path_loss / 10))
        
        # Convert back to dBm
        received_power_db = 10 * np.log10(received_power) + 30
        
        # Calculate noise power
        k = 1.380649e-23  # Boltzmann constant
        noise_power = k * noise_temperature * bandwidth
        noise_power_db = 10 * np.log10(noise_power) + 30
        
        # Calculate C/N ratio
        carrier_to_noise = received_power_db - noise_power_db
        
        # Calculate BER (simplified for BPSK)
        # For AWGN channel with BPSK modulation
        snr_linear = 10 ** (carrier_to_noise / 10)
        bit_error_rate = 0.5 * (1 - np.sqrt(snr_linear / (1 + snr_linear)))
        
        # Calculate margin (assuming required C/N of 10 dB for BPSK)
        required_cn = 10
        margin = carrier_to_noise - required_cn
        
        return LinkBudgetResult(
            received_power=received_power_db,
            carrier_to_noise=carrier_to_noise,
            bit_error_rate=bit_error_rate,
            margin=margin
        ) 