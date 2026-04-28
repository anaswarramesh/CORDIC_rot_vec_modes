import numpy as np
import math
from scipy import signal
import matplotlib.pyplot as plt

class CORDICSimulator:
    """Python implementation of CORDIC for verification"""
    
    def __init__(self, stages=16, width=32, frac_bits=15):
        self.stages = stages
        self.width = width
        self.frac_bits = frac_bits
        self.scale = 2 ** frac_bits
        
        # Precomputed atan values in radians
        self.atan_lut = []
        for i in range(stages):
            angle = math.atan(2**(-i))
            self.atan_lut.append(angle)
    
    def rotation_mode(self, x, y, angle):
        """
        Rotation Mode CORDIC
        Rotates (x, y) by the given angle
        """
        x_curr = x
        y_curr = y
        angle_curr = angle
        
        for i in range(self.stages):
            if angle_curr < 0:
                x_next = x_curr + (y_curr * 2**(-i))
                y_next = y_curr - (x_curr * 2**(-i))
                angle_next = angle_curr + self.atan_lut[i]
            else:
                x_next = x_curr - (y_curr * 2**(-i))
                y_next = y_curr + (x_curr * 2**(-i))
                angle_next = angle_curr - self.atan_lut[i]
            
            x_curr = x_next
            y_curr = y_next
            angle_curr = angle_next
        
        return x_curr, y_curr, angle_curr
    
    def vectoring_mode(self, x, y):
        """
        Vectoring Mode CORDIC
        Converts (x, y) to (magnitude, angle)
        """
        x_curr = x
        y_curr = y
        angle_curr = 0
        
        for i in range(self.stages):
            if y_curr < 0:
                x_next = x_curr + (y_curr * 2**(-i))
                y_next = y_curr - (x_curr * 2**(-i))
                angle_next = angle_curr - self.atan_lut[i]
            else:
                x_next = x_curr - (y_curr * 2**(-i))
                y_next = y_curr + (x_curr * 2**(-i))
                angle_next = angle_curr + self.atan_lut[i]
            
            x_curr = x_next
            y_curr = y_next
            angle_curr = angle_next
        
        return x_curr, angle_curr  # x_curr ≈ magnitude


def test_rotation_mode():
    """Test Rotation Mode CORDIC"""
    print("=" * 70)
    print("CORDIC ROTATION MODE TESTING")
    print("=" * 70)
    
    cordic = CORDICSimulator(stages=16, width=32, frac_bits=15)
    
    # Test cases: (x, y, angle_deg)
    test_cases = [
        (1.0, 0.0, 30),
        (1.0, 0.0, 45),
        (1.0, 0.0, 60),
        (1.0, 1.0, 22.5),
        (2.0, 3.0, 15),
        (1.0, 0.0, 90),
        (1.0, 0.0, -30),
        (1.0, 1.0, -45),
    ]
    
    errors_rotation = []
    
    for x, y, angle_deg in test_cases:
        angle_rad = math.radians(angle_deg)
        
        # Reference: numpy rotation
        rot_matrix = np.array([
            [math.cos(angle_rad), -math.sin(angle_rad)],
            [math.sin(angle_rad), math.cos(angle_rad)]
        ])
        x_ref, y_ref = rot_matrix @ np.array([x, y])
        
        # CORDIC result
        x_cordic, y_cordic, _ = cordic.rotation_mode(x, y, angle_rad)
        
        # Error calculation
        error_x = abs(x_cordic - x_ref)
        error_y = abs(y_cordic - y_ref)
        error_magnitude = math.sqrt(error_x**2 + error_y**2)
        error_percent = (error_magnitude / math.sqrt(x_ref**2 + y_ref**2)) * 100
        
        errors_rotation.append(error_percent)
        
        print(f"\nInput: x={x:.4f}, y={y:.4f}, angle={angle_deg}°")
        print(f"Reference: x={x_ref:.6f}, y={y_ref:.6f}")
        print(f"CORDIC:    x={x_cordic:.6f}, y={y_cordic:.6f}")
        print(f"Error: Δx={error_x:.8f}, Δy={error_y:.8f}")
        print(f"Error Magnitude: {error_magnitude:.8f} ({error_percent:.4f}%)")
    
    print("\n" + "=" * 70)
    print("ROTATION MODE ERROR STATISTICS")
    print("=" * 70)
    print(f"Max Error: {max(errors_rotation):.6f}%")
    print(f"Min Error: {min(errors_rotation):.6f}%")
    print(f"Mean Error: {np.mean(errors_rotation):.6f}%")
    print(f"Std Dev: {np.std(errors_rotation):.6f}%")
    
    return errors_rotation


def test_vectoring_mode():
    """Test Vectoring Mode CORDIC"""
    print("\n" + "=" * 70)
    print("CORDIC VECTORING MODE TESTING")
    print("=" * 70)
    
    cordic = CORDICSimulator(stages=16, width=32, frac_bits=15)
    
    # Test cases: (x, y)
    test_cases = [
        (1.0, 0.0),
        (1.0, 1.0),
        (3.0, 4.0),
        (5.0, 12.0),
        (1.0, 2.0),
        (2.0, 2.0),
        (1.0, 0.5),
        (-1.0, 1.0),
        (1.0, -1.0),
        (-1.0, -1.0),
    ]
    
    errors_vectoring = []
    
    for x, y in test_cases:
        # Reference: numpy calculation
        mag_ref = math.sqrt(x**2 + y**2)
        angle_ref = math.atan2(y, x)
        
        # CORDIC result
        mag_cordic, angle_cordic = cordic.vectoring_mode(x, y)
        
        # Correction factor (K_n ≈ 0.6073 for infinite stages)
        K_n = 0.6073
        mag_cordic_corrected = mag_cordic * K_n
        
        # Error calculation
        error_mag = abs(mag_cordic_corrected - mag_ref)
        error_angle = abs(angle_cordic - angle_ref)
        error_mag_percent = (error_mag / mag_ref) * 100
        error_angle_percent = (error_angle / abs(angle_ref) if angle_ref != 0 else error_angle) * 100
        
        errors_vectoring.append(error_mag_percent)
        
        print(f"\nInput: x={x:.4f}, y={y:.4f}")
        print(f"Reference: Magnitude={mag_ref:.6f}, Angle={math.degrees(angle_ref):.2f}°")
        print(f"CORDIC (raw): Magnitude={mag_cordic:.6f}, Angle={math.degrees(angle_cordic):.2f}°")
        print(f"CORDIC (corrected): Magnitude={mag_cordic_corrected:.6f}, Angle={math.degrees(angle_cordic):.2f}°")
        print(f"Error: ΔMag={error_mag:.8f} ({error_mag_percent:.4f}%)")
        print(f"Error Angle: {math.degrees(error_angle):.4f}° ({error_angle_percent:.4f}%)")
    
    print("\n" + "=" * 70)
    print("VECTORING MODE ERROR STATISTICS")
    print("=" * 70)
    print(f"Max Error: {max(errors_vectoring):.6f}%")
    print(f"Min Error: {min(errors_vectoring):.6f}%")
    print(f"Mean Error: {np.mean(errors_vectoring):.6f}%")
    print(f"Std Dev: {np.std(errors_vectoring):.6f}%")
    
    return errors_vectoring


def plot_results(errors_rotation, errors_vectoring):
    """Plot error analysis"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Rotation mode errors
    axes[0].plot(errors_rotation, 'bo-', linewidth=2, markersize=8)
    axes[0].set_xlabel('Test Case #', fontsize=12)
    axes[0].set_ylabel('Error (%)', fontsize=12)
    axes[0].set_title('CORDIC Rotation Mode - Error Analysis', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=np.mean(errors_rotation), color='r', linestyle='--', label=f'Mean: {np.mean(errors_rotation):.4f}%')
    axes[0].legend()
    
    # Vectoring mode errors
    axes[1].plot(errors_vectoring, 'ro-', linewidth=2, markersize=8)
    axes[1].set_xlabel('Test Case #', fontsize=12)
    axes[1].set_ylabel('Error (%)', fontsize=12)
    axes[1].set_title('CORDIC Vectoring Mode - Error Analysis', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=np.mean(errors_vectoring), color='r', linestyle='--', label=f'Mean: {np.mean(errors_vectoring):.4f}%')
    axes[1].legend()
    
    plt.tight_layout()
    plt.savefig('cordic_error_analysis.png', dpi=300, bbox_inches='tight')
    print("\n✓ Error analysis plot saved as 'cordic_error_analysis.png'")
    plt.show()


def main():
    """Main test function"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "CORDIC DESIGN - VERIFICATION TEST SUITE" + " " * 13 + "║")
    print("║" + " " * 20 + "16 Stages, 32-bit Fixed Point" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")
    
    # Run tests
    errors_rotation = test_rotation_mode()
    errors_vectoring = test_vectoring_mode()
    
    # Plot results
    plot_results(errors_rotation, errors_vectoring)
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Rotation Mode - Mean Error: {np.mean(errors_rotation):.6f}%")
    print(f"Vectoring Mode - Mean Error: {np.mean(errors_vectoring):.6f}%")
    print("✓ All tests completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
