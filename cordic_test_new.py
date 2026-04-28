import numpy as np
import math
import matplotlib.pyplot as plt

class CORDICSimulator:
    """
    Python implementation of CORDIC for verification.
    Matches a 16-stage pipelined hardware architecture.
    """
    
    def __init__(self, stages=16, width=32, frac_bits=15):
        self.stages = stages
        self.width = width
        self.frac_bits = frac_bits
        
        # CORDIC Gain Inverse (K_inv) for 16 stages
        # This compensates for the vector growth (approx 1.6467x)
        self.k_inv = 0.6072529350088812
        
        # Precomputed atan lookup table
        self.atan_lut = [math.atan(2**(-i)) for i in range(stages)]
    
    def rotation_mode(self, x, y, angle):
        """Rotates vector (x, y) by target angle"""
        x_curr, y_curr, angle_curr = float(x), float(y), float(angle)
        
        for i in range(self.stages):
            x_shift = x_curr * (2 ** (-i))
            y_shift = y_curr * (2 ** (-i))
            
            # Rotation Mode Decision: Drive remaining angle to zero
            if angle_curr < 0:
                # Rotate counter-clockwise
                x_next = x_curr + y_shift
                y_next = y_curr - x_shift
                angle_next = angle_curr + self.atan_lut[i]
            else:
                # Rotate clockwise
                x_next = x_curr - y_shift
                y_next = y_curr + x_shift
                angle_next = angle_curr - self.atan_lut[i]
            
            x_curr, y_curr, angle_curr = x_next, y_next, angle_next
            
        return x_curr, y_curr, angle_curr
    
    def vectoring_mode(self, x, y):
        """Converts (x, y) to Magnitude and Angle by driving y to 0"""
        x_curr, y_curr, angle_curr = float(x), float(y), 0.0
        
        for i in range(self.stages):
            x_shift = x_curr * (2 ** (-i))
            y_shift = y_curr * (2 ** (-i))
            
            # Vectoring Mode Decision: Drive Y to zero
            # If Y is negative, rotate counter-clockwise (add to Y)
            if y_curr < 0: 
                x_next = x_curr - y_shift
                y_next = y_curr + x_shift
                angle_next = angle_curr - self.atan_lut[i]
            # If Y is positive, rotate clockwise (subtract from Y)
            else: 
                x_next = x_curr + y_shift
                y_next = y_curr - x_shift
                angle_next = angle_curr + self.atan_lut[i]
            
            x_curr, y_curr, angle_curr = x_next, y_next, angle_next
            
        return x_curr, angle_curr

def test_rotation_mode(sim):
    print("\n" + "="*60 + "\nCORDIC ROTATION MODE TESTING\n" + "="*60)
    test_cases = [(1.0, 0.0, 30), (1.0, 0.0, 45), (1.0, 0.0, 60), (1.0, 1.0, 22.5)]
    errors = []

    for x, y, deg in test_cases:
        rad = math.radians(deg)
        # Math Reference
        x_ref = x * math.cos(rad) - y * math.sin(rad)
        y_ref = x * math.sin(rad) + y * math.cos(rad)
        
        # CORDIC Simulation
        x_raw, y_raw, _ = sim.rotation_mode(x, y, rad)
        
        # Apply Gain Compensation
        x_cordic = x_raw * sim.k_inv
        y_cordic = y_raw * sim.k_inv
        
        err = math.sqrt((x_cordic - x_ref)**2 + (y_cordic - y_ref)**2)
        errors.append(err * 100)
        print(f"Angle {deg:>4}°: Ref({x_ref:.4f}, {y_ref:.4f}) | CORDIC({x_cordic:.4f}, {y_cordic:.4f}) | Err: {err*100:.6f}%")
    return errors

def test_vectoring_mode(sim):
    print("\n" + "="*60 + "\nCORDIC VECTORING MODE TESTING\n" + "="*60)
    test_cases = [(1.0, 1.0), (3.0, 4.0), (0.5, 0.866), (1.0, 0.0)]
    errors = []

    for x, y in test_cases:
        # Math Reference
        mag_ref = math.sqrt(x**2 + y**2)
        ang_ref = math.atan2(y, x)
        
        # CORDIC Simulation
        mag_raw, ang_cordic = sim.vectoring_mode(x, y)
        
        # Apply Gain Compensation
        mag_cordic = mag_raw * sim.k_inv
        
        err_mag = abs(mag_cordic - mag_ref) / mag_ref * 100 if mag_ref != 0 else 0
        errors.append(err_mag)
        
        print(f"In({x:.1f}, {y:.1f}): Ref Mag {mag_ref:.4f}, Ang {math.degrees(ang_ref):>5.2f}° | "
              f"CORDIC Mag {mag_cordic:.4f}, Ang {math.degrees(ang_cordic):>5.2f}° | Err: {err_mag:.6f}%")
    return errors

if __name__ == "__main__":
    # Initialize Simulator
    cordic_sim = CORDICSimulator(stages=16)
    
    # Run Tests
    rot_errors = test_rotation_mode(cordic_sim)
    vec_errors = test_vectoring_mode(cordic_sim)
    
    # Final Summary
    print("\n" + "="*60)
    print(f"FINAL PERFORMANCE SUMMARY")
    print(f"Average Rotation Error:  {np.mean(rot_errors):.6f}%")
    print(f"Average Vectoring Error: {np.mean(vec_errors):.6f}%")
    print("="*60 + "\n")
