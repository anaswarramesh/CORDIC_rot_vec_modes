import numpy as np
import math
from scipy import signal
import matplotlib.pyplot as plt

class CORDICSimulator:
    """Python implementation of CORDIC for verification with detailed debugging"""
    
    def __init__(self, stages=16, width=32, frac_bits=15):
        self.stages = stages
        self.width = width
        self.frac_bits = frac_bits
        self.scale = 2 ** frac_bits  # 2^15 = 32768
        
        # Precomputed atan values in RADIANS (floating-point)
        self.atan_lut = []
        print("\n" + "="*80)
        print("ATAN LOOKUP TABLE VERIFICATION")
        print("="*80)
        for i in range(stages):
            angle = math.atan(2**(-i))
            self.atan_lut.append(angle)
            print(f"atan_lut[{i:2d}] = atan(2^-{i:2d}) = {angle:.15f} rad = {math.degrees(angle):10.6f}°")
    
    def rotation_mode_debug(self, x, y, angle_deg, verbose=True):
        """
        Rotation Mode CORDIC with detailed debugging
        """
        angle = math.radians(angle_deg)
        x_curr = float(x)
        y_curr = float(y)
        angle_curr = float(angle)
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"ROTATION MODE - DETAILED TRACE")
            print(f"{'='*80}")
            print(f"Input: x={x_curr:.10f}, y={y_curr:.10f}, angle={angle_deg:.2f}°")
            print(f"Reference (NumPy):")
            rot_matrix = np.array([
                [math.cos(angle), -math.sin(angle)],
                [math.sin(angle), math.cos(angle)]
            ])
            x_ref, y_ref = rot_matrix @ np.array([x_curr, y_curr])
            print(f"  x_ref={x_ref:.10f}, y_ref={y_ref:.10f}")
        
        for i in range(self.stages):
            if verbose and i < 4:
                print(f"\n--- Stage {i} ---")
                print(f"Before: x={x_curr:.10f}, y={y_curr:.10f}, angle={math.degrees(angle_curr):.6f}°")
            
            # Calculate shifts
            x_shift = x_curr * (2 ** (-i))
            y_shift = y_curr * (2 ** (-i))
            
            if verbose and i < 4:
                print(f"  Shifts: x >> {i} = {x_shift:.10f}, y >> {i} = {y_shift:.10f}")
                print(f"  atan_lut[{i}] = {math.degrees(self.atan_lut[i]):.6f}°")
            
            if angle_curr < 0:
                # Rotate clockwise
                x_next = x_curr + y_shift
                y_next = y_curr - x_shift
                angle_next = angle_curr + self.atan_lut[i]
                if verbose and i < 4:
                    print(f"  angle < 0 → Rotate CLOCKWISE")
            else:
                # Rotate counter-clockwise
                x_next = x_curr - y_shift
                y_next = y_curr + x_shift
                angle_next = angle_curr - self.atan_lut[i]
                if verbose and i < 4:
                    print(f"  angle > 0 → Rotate COUNTER-CLOCKWISE")
            
            x_curr = x_next
            y_curr = y_next
            angle_curr = angle_next
            
            if verbose and i < 4:
                print(f"After:  x={x_curr:.10f}, y={y_curr:.10f}, angle={math.degrees(angle_curr):.6f}°")
        
        if verbose:
            print(f"\n--- Final Result (Stage 16) ---")
            print(f"CORDIC: x={x_curr:.10f}, y={y_curr:.10f}")
            print(f"Ref:    x={x_ref:.10f}, y={y_ref:.10f}")
            print(f"Error:  Δx={abs(x_curr - x_ref):.10f}, Δy={abs(y_curr - y_ref):.10f}")
            
            error_magnitude = math.sqrt((x_curr - x_ref)**2 + (y_curr - y_ref)**2)
            ref_magnitude = math.sqrt(x_ref**2 + y_ref**2)
            error_percent = (error_magnitude / ref_magnitude) * 100 if ref_magnitude > 0 else 0
            print(f"Error %: {error_percent:.6f}%")
        
        return x_curr, y_curr, angle_curr
    
    def vectoring_mode_debug(self, x, y, verbose=True):
        """
        Vectoring Mode CORDIC with detailed debugging
        """
        x_curr = float(x)
        y_curr = float(y)
        angle_curr = 0.0
        
        if verbose:
            print(f"\n{'='*80}")
            print(f"VECTORING MODE - DETAILED TRACE")
            print(f"{'='*80}")
            print(f"Input: x={x_curr:.10f}, y={y_curr:.10f}")
            print(f"Reference (NumPy):")
            mag_ref = math.sqrt(x_curr**2 + y_curr**2)
            angle_ref = math.atan2(y_curr, x_curr)
            print(f"  magnitude={mag_ref:.10f}, angle={math.degrees(angle_ref):.6f}°")
        
        for i in range(self.stages):
            if verbose and i < 4:
                print(f"\n--- Stage {i} ---")
                print(f"Before: x={x_curr:.10f}, y={y_curr:.10f}, angle={math.degrees(angle_curr):.6f}°")
            
            # Calculate shifts
            x_shift = x_curr * (2 ** (-i))
            y_shift = y_curr * (2 ** (-i))
            
            if verbose and i < 4:
                print(f"  Shifts: x >> {i} = {x_shift:.10f}, y >> {i} = {y_shift:.10f}")
                print(f"  atan_lut[{i}] = {math.degrees(self.atan_lut[i]):.6f}°")
            
            if y_curr < 0:
                # Rotate clockwise
                x_next = x_curr + y_shift
                y_next = y_curr - x_shift
                angle_next = angle_curr - self.atan_lut[i]
                if verbose and i < 4:
                    print(f"  y < 0 → Rotate CLOCKWISE")
            else:
                # Rotate counter-clockwise
                x_next = x_curr - y_shift
                y_next = y_curr + x_shift
                angle_next = angle_curr + self.atan_lut[i]
                if verbose and i < 4:
                    print(f"  y > 0 → Rotate COUNTER-CLOCKWISE")
            
            x_curr = x_next
            y_curr = y_next
            angle_curr = angle_next
            
            if verbose and i < 4:
                print(f"After:  x={x_curr:.10f}, y={y_curr:.10f}, angle={math.degrees(angle_curr):.6f}°")
        
        if verbose:
            print(f"\n--- Final Result (Stage 16) ---")
            print(f"CORDIC (raw): magnitude={x_curr:.10f}, angle={math.degrees(angle_curr):.6f}°")
            
            K_n = 0.6072529350088812
            mag_cordic_corrected = x_curr * K_n
            print(f"CORDIC (corrected with K_n={K_n}): magnitude={mag_cordic_corrected:.10f}")
            print(f"Ref:                             magnitude={mag_ref:.10f}, angle={math.degrees(angle_ref):.6f}°")
            
            error_mag = abs(mag_cordic_corrected - mag_ref)
            error_angle = abs(angle_curr - angle_ref)
            error_percent = (error_mag / mag_ref) * 100 if mag_ref > 0 else 0
            
            print(f"Error: ΔMag={error_mag:.10f}, Error %={error_percent:.6f}%")
            print(f"Angle Error: {math.degrees(error_angle):.6f}°")
        
        return x_curr, angle_curr


def test_rotation_mode_detailed():
    """Test Rotation Mode with detailed output"""
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 18 + "ROTATION MODE - DETAILED DEBUG TEST" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    
    cordic = CORDICSimulator(stages=16, width=32, frac_bits=15)
    
    # Test case 1: Rotate (1, 0) by 45°
    print("\n" + "█"*80)
    print("TEST 1: Rotate (1.0, 0.0) by 45°")
    print("█"*80)
    x, y, angle = cordic.rotation_mode_debug(1.0, 0.0, 45, verbose=True)
    
    # Test case 2: Rotate (1, 0) by 30°
    print("\n" + "█"*80)
    print("TEST 2: Rotate (1.0, 0.0) by 30°")
    print("█"*80)
    x, y, angle = cordic.rotation_mode_debug(1.0, 0.0, 30, verbose=True)
    
    # Test case 3: Rotate (1, 1) by 22.5°
    print("\n" + "█"*80)
    print("TEST 3: Rotate (1.0, 1.0) by 22.5°")
    print("█"*80)
    x, y, angle = cordic.rotation_mode_debug(1.0, 1.0, 22.5, verbose=True)


def test_vectoring_mode_detailed():
    """Test Vectoring Mode with detailed output"""
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 18 + "VECTORING MODE - DETAILED DEBUG TEST" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    
    cordic = CORDICSimulator(stages=16, width=32, frac_bits=15)
    
    # Test case 1: Convert (1, 0) to polar
    print("\n" + "█"*80)
    print("TEST 1: Convert (1.0, 0.0) to polar")
    print("█"*80)
    mag, angle = cordic.vectoring_mode_debug(1.0, 0.0, verbose=True)
    
    # Test case 2: Convert (1, 1) to polar
    print("\n" + "█"*80)
    print("TEST 2: Convert (1.0, 1.0) to polar")
    print("█"*80)
    mag, angle = cordic.vectoring_mode_debug(1.0, 1.0, verbose=True)
    
    # Test case 3: Convert (3, 4) to polar
    print("\n" + "█"*80)
    print("TEST 3: Convert (3.0, 4.0) to polar")
    print("█"*80)
    mag, angle = cordic.vectoring_mode_debug(3.0, 4.0, verbose=True)


def main():
    """Main test function"""
    test_rotation_mode_detailed()
    test_vectoring_mode_detailed()
    
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "DEBUG TEST COMPLETED" + " " * 34 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\nNEXT STEPS:")
    print("1. Check atan_lut values - should be in radians (0.785, 0.464, etc.)")
    print("2. Check iteration trace - see where error accumulates")
    print("3. Verify shifts are correct - x >> i should be x * 2^-i")
    print("4. Compare with reference (NumPy) at each stage")
    print()


if __name__ == "__main__":
    main()
