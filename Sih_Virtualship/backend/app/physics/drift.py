import random
import math

def calculate_ou_drift(current: float, target: float, k: float, dt: float, noise_std: float, min_val: float = None, max_val: float = None) -> float:
    """
    Computes one step of the discretized Ornstein-Uhlenbeck process:
    dX = k * (Target - X) * dt + Sigma * dW
    
    This ensures smooth, continuous drift towards target boundaries rather than blocky random numbers.
    """
    # Calculate drift velocity
    drift = k * (target - current) * dt
    
    # Calculate white noise scaled by square root of dt
    noise = random.gauss(0, noise_std) * math.sqrt(dt)
    
    new_val = current + drift + noise
    
    # Apply optional constraints
    if min_val is not None:
        new_val = max(min_val, new_val)
    if max_val is not None:
        new_val = min(max_val, new_val)
        
    return new_val
