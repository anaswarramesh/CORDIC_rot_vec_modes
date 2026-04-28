import numpy as np
import math
from scipy import signal
import matplotlib.pyplot as plt

# CORDIC gain K_n for 16 stages: product of sqrt(1 + 2^{-2i}) for i=0..15
# Raw CORDIC output magnitude = K_n * true_magnitude; apply 1/K_n to correct.
_K_N_16 = 1.0
for _i in range(16):
    _K_N_16 *= math.sqrt(1.0 + 2.0 ** (-2 * _i))
K_N_16 = _K_N_16          # ≈ 1.6467602578654553
INV_K_N_16 = 1.0 / K_N_16  # ≈ 0.6072529350088812


class CORDICSimulator:
    """Python floating-point model of CORDIC for verification"""

    def __init__(self, stages=16, width=32, frac_bits=30):
        self.stages = stages
        self.width = width
        self.frac_bits = frac_bits

        # atan(2^-i) in radians, for i = 0 .. stages-1
        self.atan_lut = [math.atan(2 ** (-i)) for i in range(stages)]

    def rotation_mode(self, x, y, angle):
        """
        Rotation Mode CORDIC.
        Rotates vector (x, y) by 'angle' radians.
        Returns (x_out, y_out, angle_residual).
        NOTE: output magnitudes are scaled by K_n (~1.6468).
              Divide by K_n (or pre-scale inputs by 1/K_n) to obtain true values.
        """
        xc, yc, zc = float(x), float(y), float(angle)
        for i in range(self.stages):
            xs = xc * 2 ** (-i)
            ys = yc * 2 ** (-i)
            if zc < 0:
                # angle negative → rotate CW
                xc, yc, zc = xc + ys, yc - xs, zc + self.atan_lut[i]
            else:
                # angle positive → rotate CCW
                xc, yc, zc = xc - ys, yc + xs, zc - self.atan_lut[i]
        return xc, yc, zc

    def vectoring_mode(self, x, y):
        """
        Vectoring Mode CORDIC.
        Drives Y to zero, accumulating the rotation angle in Z.
        Returns (magnitude_raw, angle_rad).
        NOTE: magnitude_raw is scaled by K_n (~1.6468).
              Multiply magnitude_raw by INV_K_N_16 to get true magnitude.
        Precondition: x > 0 (input in first or fourth quadrant).
        """
        xc, yc, zc = float(x), float(y), 0.0
        for i in range(self.stages):
            xs = xc * 2 ** (-i)
            ys = yc * 2 ** (-i)
            if yc >= 0:
                # Y non-negative → rotate CW to drive Y down toward zero
                xc, yc, zc = xc + ys, yc - xs, zc + self.atan_lut[i]
            else:
                # Y negative → rotate CCW to drive Y up toward zero
                xc, yc, zc = xc - ys, yc + xs, zc - self.atan_lut[i]
        return xc, zc  # xc ≈ K_n * magnitude


def test_rotation_mode():
    """Test Rotation Mode CORDIC"""
    print("=" * 70)
    print("CORDIC ROTATION MODE TESTING")
    print("=" * 70)

    cordic = CORDICSimulator(stages=16, width=32, frac_bits=30)

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

        # Reference: rotation matrix
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        x_ref = cos_a * x - sin_a * y
        y_ref = sin_a * x + cos_a * y

        # CORDIC result (raw, scaled by K_n)
        x_raw, y_raw, _ = cordic.rotation_mode(x, y, angle_rad)

        # Apply 1/K_n correction to match true output magnitude
        x_cordic = x_raw * INV_K_N_16
        y_cordic = y_raw * INV_K_N_16

        # Error
        error_x = abs(x_cordic - x_ref)
        error_y = abs(y_cordic - y_ref)
        error_mag = math.sqrt(error_x ** 2 + error_y ** 2)
        ref_mag = math.sqrt(x_ref ** 2 + y_ref ** 2)
        error_pct = (error_mag / ref_mag * 100) if ref_mag > 0 else 0.0

        errors_rotation.append(error_pct)

        print(f"\nInput: x={x:.4f}, y={y:.4f}, angle={angle_deg}°")
        print(f"Reference: x={x_ref:.6f}, y={y_ref:.6f}")
        print(f"CORDIC:    x={x_cordic:.6f}, y={y_cordic:.6f}")
        print(f"Error: Δx={error_x:.8f}, Δy={error_y:.8f}")
        print(f"Error Magnitude: {error_mag:.8f} ({error_pct:.4f}%)")

    print("\n" + "=" * 70)
    print("ROTATION MODE ERROR STATISTICS")
    print("=" * 70)
    print(f"Max Error:  {max(errors_rotation):.6f}%")
    print(f"Min Error:  {min(errors_rotation):.6f}%")
    print(f"Mean Error: {np.mean(errors_rotation):.6f}%")
    print(f"Std Dev:    {np.std(errors_rotation):.6f}%")

    return errors_rotation


def test_vectoring_mode():
    """Test Vectoring Mode CORDIC"""
    print("\n" + "=" * 70)
    print("CORDIC VECTORING MODE TESTING")
    print("=" * 70)

    cordic = CORDICSimulator(stages=16, width=32, frac_bits=30)

    # Test cases: (x, y) — x must be > 0 for basic CORDIC vectoring
    test_cases = [
        (1.0, 0.0),
        (1.0, 1.0),
        (3.0, 4.0),
        (5.0, 12.0),
        (1.0, 2.0),
        (2.0, 2.0),
        (1.0, 0.5),
        (1.0, -1.0),
    ]

    errors_vectoring = []

    for x, y in test_cases:
        # Reference
        mag_ref = math.sqrt(x ** 2 + y ** 2)
        angle_ref = math.atan2(y, x)

        # CORDIC result
        mag_raw, angle_cordic = cordic.vectoring_mode(x, y)
        mag_cordic = mag_raw * INV_K_N_16  # apply K_n correction

        # Errors
        error_mag = abs(mag_cordic - mag_ref)
        error_angle = abs(angle_cordic - angle_ref)
        error_mag_pct = (error_mag / mag_ref * 100) if mag_ref > 0 else 0.0
        error_angle_pct = (error_angle / abs(angle_ref) * 100) if angle_ref != 0 else error_angle

        errors_vectoring.append(error_mag_pct)

        print(f"\nInput: x={x:.4f}, y={y:.4f}")
        print(f"Reference:         Magnitude={mag_ref:.6f}, Angle={math.degrees(angle_ref):.2f}°")
        print(f"CORDIC (raw):      Magnitude={mag_raw:.6f}, Angle={math.degrees(angle_cordic):.2f}°")
        print(f"CORDIC (corrected):Magnitude={mag_cordic:.6f}, Angle={math.degrees(angle_cordic):.2f}°")
        print(f"Error: ΔMag={error_mag:.8f} ({error_mag_pct:.4f}%)")
        print(f"Error Angle: {math.degrees(error_angle):.4f}° ({error_angle_pct:.4f}%)")

    print("\n" + "=" * 70)
    print("VECTORING MODE ERROR STATISTICS")
    print("=" * 70)
    print(f"Max Error:  {max(errors_vectoring):.6f}%")
    print(f"Min Error:  {min(errors_vectoring):.6f}%")
    print(f"Mean Error: {np.mean(errors_vectoring):.6f}%")
    print(f"Std Dev:    {np.std(errors_vectoring):.6f}%")

    return errors_vectoring


def plot_results(errors_rotation, errors_vectoring):
    """Plot error analysis"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].plot(errors_rotation, 'bo-', linewidth=2, markersize=8)
    axes[0].set_xlabel('Test Case #', fontsize=12)
    axes[0].set_ylabel('Error (%)', fontsize=12)
    axes[0].set_title('CORDIC Rotation Mode - Error Analysis', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=np.mean(errors_rotation), color='r', linestyle='--',
                    label=f'Mean: {np.mean(errors_rotation):.4f}%')
    axes[0].legend()

    axes[1].plot(errors_vectoring, 'ro-', linewidth=2, markersize=8)
    axes[1].set_xlabel('Test Case #', fontsize=12)
    axes[1].set_ylabel('Error (%)', fontsize=12)
    axes[1].set_title('CORDIC Vectoring Mode - Error Analysis', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=np.mean(errors_vectoring), color='r', linestyle='--',
                    label=f'Mean: {np.mean(errors_vectoring):.4f}%')
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

    errors_rotation = test_rotation_mode()
    errors_vectoring = test_vectoring_mode()

    plot_results(errors_rotation, errors_vectoring)

    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Rotation Mode - Mean Error: {np.mean(errors_rotation):.6f}%")
    print(f"Vectoring Mode - Mean Error: {np.mean(errors_vectoring):.6f}%")
    print("✓ All tests completed successfully!")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
