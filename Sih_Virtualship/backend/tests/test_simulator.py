import pytest
import random
from app.simulator.vessel_simulator import VesselSimulator
from app.simulator.scenario_engine import ScenarioType
from app.schemas.telemetry import OperationalState

def test_simulator_initial_state():
    """Verify simulator starts in CRUISE with normal metrics."""
    random.seed(0)
    sim = VesselSimulator()
    state = sim.tick(dt=0)
    
    assert state.vessel_id == "MV_TITAN_PRO"
    assert sim.sim_state == "CRUISE"
    assert sim.rpm > 0
    assert state.state == OperationalState.CRUISING

def test_simulator_state_transitions():
    """Verify simulator state transitions update target throttle speeds."""
    random.seed(0)
    sim = VesselSimulator()
    
    # Transition to OFF state
    sim.set_simulator_state("OFF")
    
    # Tick to let thermodynamic parameters settle
    for _ in range(120):
        sim.tick(dt=1.0)
        
    assert sim.sim_state == "OFF"
    assert sim.rpm < 5.0  # RPM should drop close to 0
    assert sim.coolant_temp < 35.0  # Temperature should cool down

def test_simulator_scenario_modifiers():
    """Verify that selecting scenarios modifies physical targets dynamically."""
    random.seed(0)
    sim = VesselSimulator()
    sim.set_simulator_state("CRUISE")
    
    # Default voyage variables settling
    for _ in range(20):
        sim.tick(dt=1.0)
        
    normal_strain = sim.tick(dt=0).hull.strain
    assert normal_strain < 150.0  # Settle near baseline 120.0
    
    # Toggle Heavy Weather scenario
    sim.set_scenario(ScenarioType.HEAVY_WEATHER)
    
    # Tick multiple times to allow weather metrics to drift
    for _ in range(50):
        state = sim.tick(dt=1.0)
    
    assert sim.wind_speed > 25.0  # Storm wind targets rise
    assert state.hull.strain > 200.0  # Heavy weather forces structural strain targets up
