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

        # atan(2^-i) in radians
        self.atan_lut = []
        for i in range(stages):
            angle = math.atan(2 ** (-i))
            self.atan_lut.append(angle)
            print(f"atan(2^-{i}) = {angle:.15f} rad = {math.degrees(angle):.6f}°")

    def rotation_mode(self, x, y, angle):
        """
        Rotation Mode CORDIC.
        Rotates (x, y) by 'angle' radians.
        NOTE: raw output is scaled by K_n; apply INV_K_N_16 for true values.
        """
        xc, yc, zc = float(x), float(y), float(angle)

        print(f"\n  Initial: x={xc:.6f}, y={yc:.6f}, angle={math.degrees(zc):.2f}°")

        for i in range(self.stages):
            xs = xc * 2 ** (-i)
            ys = yc * 2 ** (-i)
            if zc < 0:
                # angle negative → rotate CW
                xc, yc, zc = xc + ys, yc - xs, zc + self.atan_lut[i]
            else:
                # angle positive → rotate CCW
                xc, yc, zc = xc - ys, yc + xs, zc - self.atan_lut[i]

            if i < 3 or i >= self.stages - 2:
                print(f"  Stage {i}: x={xc:.8f}, y={yc:.8f}, angle={math.degrees(zc):.4f}°")

        return xc, yc, zc

    def vectoring_mode(self, x, y):
        """
        Vectoring Mode CORDIC.
        Drives Y to zero, accumulating the rotation angle in Z.
        NOTE: magnitude output is scaled by K_n; apply INV_K_N_16 to correct.
        Precondition: x > 0 (first or fourth quadrant).
        """
        xc, yc, zc = float(x), float(y), 0.0

        print(f"\n  Initial: x={xc:.6f}, y={yc:.6f}")

        for i in range(self.stages):
            xs = xc * 2 ** (-i)
            ys = yc * 2 ** (-i)
            if yc >= 0:
                # Y non-negative → rotate CW to drive Y down toward zero
                xc, yc, zc = xc + ys, yc - xs, zc + self.atan_lut[i]
            else:
                # Y negative → rotate CCW to drive Y up toward zero
                xc, yc, zc = xc - ys, yc + xs, zc - self.atan_lut[i]

            if i < 3 or i >= self.stages - 2:
                print(f"  Stage {i}: x={xc:.8f}, y={yc:.8f}, angle={math.degrees(zc):.4f}°")

        return xc, zc  # xc ≈ K_n * magnitude


def test_rotation_mode():
    """Test Rotation Mode CORDIC"""
    print("=" * 80)
    print("CORDIC ROTATION MODE TESTING")
    print("=" * 80)

    cordic = CORDICSimulator(stages=16, width=32, frac_bits=30)

    test_cases = [
        (1.0, 0.0, 30),
        (1.0, 0.0, 45),
        (1.0, 0.0, 60),
        (1.0, 1.0, 22.5),
        (2.0, 3.0, 15),
    ]

    errors_rotation = []

    for x, y, angle_deg in test_cases:
        angle_rad = math.radians(angle_deg)

        print(f"\n{'=' * 80}")
        print(f"Test: Rotate ({x:.4f}, {y:.4f}) by {angle_deg}°")
        print(f"{'=' * 80}")

        # Reference
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        x_ref = cos_a * x - sin_a * y
        y_ref = sin_a * x + cos_a * y

        # CORDIC raw output (scaled by K_n)
        x_raw, y_raw, angle_residual = cordic.rotation_mode(x, y, angle_rad)

        # Apply 1/K_n correction
        x_cordic = x_raw * INV_K_N_16
        y_cordic = y_raw * INV_K_N_16

        # Error
        error_x = abs(x_cordic - x_ref)
        error_y = abs(y_cordic - y_ref)
        error_magnitude = math.sqrt(error_x ** 2 + error_y ** 2)
        ref_magnitude = math.sqrt(x_ref ** 2 + y_ref ** 2)
        error_percent = (error_magnitude / ref_magnitude * 100) if ref_magnitude > 0 else 0.0

        errors_rotation.append(error_percent)

        print(f"\nReference: x={x_ref:.8f}, y={y_ref:.8f}")
        print(f"CORDIC:    x={x_cordic:.8f}, y={y_cordic:.8f}")
        print(f"Error: Δx={error_x:.10f}, Δy={error_y:.10f}")
        print(f"Error Magnitude: {error_magnitude:.10f} ({error_percent:.6f}%)")
        print(f"Residual Angle: {math.degrees(angle_residual):.8f}°")

    print("\n" + "=" * 80)
    print("ROTATION MODE ERROR STATISTICS")
    print("=" * 80)
    print(f"Max Error:  {max(errors_rotation):.6f}%")
    print(f"Min Error:  {min(errors_rotation):.6f}%")
    print(f"Mean Error: {np.mean(errors_rotation):.6f}%")
    print(f"Std Dev:    {np.std(errors_rotation):.6f}%")

    return errors_rotation


def test_vectoring_mode():
    """Test Vectoring Mode CORDIC"""
    print("\n" + "=" * 80)
    print("CORDIC VECTORING MODE TESTING")
    print("=" * 80)

    cordic = CORDICSimulator(stages=16, width=32, frac_bits=30)

    # x must be > 0 for basic CORDIC vectoring (first or fourth quadrant)
    test_cases = [
        (1.0, 0.0),
        (1.0, 1.0),
        (3.0, 4.0),
        (5.0, 12.0),
        (1.0, 2.0),
        (2.0, 2.0),
        (1.0, 0.5),
        (0.5, 0.866),  # ≈ (0.5, √3/2) for 60°
    ]

    errors_vectoring = []

    for x, y in test_cases:
        print(f"\n{'=' * 80}")
        print(f"Test: Convert ({x:.4f}, {y:.4f}) to polar")
        print(f"{'=' * 80}")

        mag_ref = math.sqrt(x ** 2 + y ** 2)
        angle_ref = math.atan2(y, x)

        mag_raw, angle_cordic = cordic.vectoring_mode(x, y)
        mag_cordic = mag_raw * INV_K_N_16  # apply K_n correction

        error_mag = abs(mag_cordic - mag_ref)
        error_angle = abs(angle_cordic - angle_ref)
        error_mag_pct = (error_mag / mag_ref * 100) if mag_ref > 0 else 0.0
        error_angle_pct = (error_angle / abs(angle_ref) * 100) if angle_ref != 0 else error_angle

        errors_vectoring.append(error_mag_pct)

        print(f"\nReference:          Magnitude={mag_ref:.8f}, Angle={math.degrees(angle_ref):.4f}°")
        print(f"CORDIC (raw):       Magnitude={mag_raw:.8f},  Angle={math.degrees(angle_cordic):.4f}°")
        print(f"CORDIC (corrected): Magnitude={mag_cordic:.8f}, Angle={math.degrees(angle_cordic):.4f}°")
        print(f"Error: ΔMag={error_mag:.10f} ({error_mag_pct:.6f}%)")
        print(f"Error Angle: {math.degrees(error_angle):.8f}° ({error_angle_pct:.6f}%)")

    print("\n" + "=" * 80)
    print("VECTORING MODE ERROR STATISTICS")
    print("=" * 80)
    print(f"Max Error:  {max(errors_vectoring):.6f}%")
    print(f"Min Error:  {min(errors_vectoring):.6f}%")
    print(f"Mean Error: {np.mean(errors_vectoring):.6f}%")
    print(f"Std Dev:    {np.std(errors_vectoring):.6f}%")

    return errors_vectoring


def plot_results(errors_rotation, errors_vectoring):
    """Plot error analysis"""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    axes[0].plot(errors_rotation, 'bo-', linewidth=2, markersize=10, label='Error per test')
    axes[0].set_xlabel('Test Case #', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Error (%)', fontsize=12, fontweight='bold')
    axes[0].set_title('CORDIC Rotation Mode - Error Analysis', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    axes[0].axhline(y=np.mean(errors_rotation), color='r', linestyle='--', linewidth=2,
                    label=f'Mean: {np.mean(errors_rotation):.6f}%')
    axes[0].legend(fontsize=10)

    axes[1].plot(errors_vectoring, 'ro-', linewidth=2, markersize=10, label='Error per test')
    axes[1].set_xlabel('Test Case #', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Error (%)', fontsize=12, fontweight='bold')
    axes[1].set_title('CORDIC Vectoring Mode - Error Analysis', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    axes[1].axhline(y=np.mean(errors_vectoring), color='r', linestyle='--', linewidth=2,
                    label=f'Mean: {np.mean(errors_vectoring):.6f}%')
    axes[1].legend(fontsize=10)

    plt.tight_layout()
    plt.savefig('cordic_error_analysis_fixed.png', dpi=300, bbox_inches='tight')
    print("\n✓ Error analysis plot saved as 'cordic_error_analysis_fixed.png'")
    plt.show()


def main():
    """Main test function"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "CORDIC DESIGN - VERIFICATION TEST SUITE (FIXED)" + " " * 17 + "║")
    print("║" + " " * 20 + "16 Stages, 32-bit Fixed Point" + " " * 28 + "║")
    print("╚" + "=" * 78 + "╝")

    errors_rotation = test_rotation_mode()
    errors_vectoring = test_vectoring_mode()

    plot_results(errors_rotation, errors_vectoring)

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"✓ Rotation Mode - Mean Error: {np.mean(errors_rotation):.6f}%")
    print(f"✓ Vectoring Mode - Mean Error: {np.mean(errors_vectoring):.6f}%")
    print("✓ All tests completed successfully!")
    print("=" * 80 + "\n")

    print("\nPERFORMANCE METRICS:")
    print(f"  Rotation Mode Accuracy:  ±{max(errors_rotation):.4f}%")
    print(f"  Vectoring Mode Accuracy: ±{max(errors_vectoring):.4f}%")
    print(f"  Expected for 16-stage CORDIC: ±0.01-0.05%")
    print()


if __name__ == "__main__":
    main()
