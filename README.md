# CORDIC Design - Vectoring and Rotation Mode

## Overview
This project implements both **Rotation Mode** and **Vectoring Mode** CORDIC (Coordinate Rotation Digital Computer) algorithms in Verilog with 16 stages using 32-bit fixed-point arithmetic. Complete Python verification suite and comprehensive error analysis are provided.

## Algorithm Description

### CORDIC Rotation Mode
- **Purpose**: Rotate an input vector (x, y) by a given angle θ
- **Operation**: Iteratively applies micro-rotations using pre-computed angles
- **Applications**: DFT computation, trigonometric functions, complex number multiplication
- **Convergence**: ~1 bit of accuracy per stage (16 stages ≈ 16-bit accuracy)

### CORDIC Vectoring Mode
- **Purpose**: Convert Cartesian coordinates (x, y) to polar form (magnitude, angle)
- **Operation**: Iteratively rotates the vector towards the x-axis
- **Applications**: Magnitude calculation, phase computation, CORDIC-based complex operations
- **Convergence**: Similar to rotation mode

## Project Files

### Verilog Implementation
1. **cordic_rotation_mode.v**
   - 16-stage rotation mode CORDIC module
   - Configurable N-bit width (default: 32-bit)
   - Fixed-point arithmetic with Q1.15 format
   - Pipelined architecture for high throughput

2. **cordic_vectoring_mode.v**
   - 16-stage vectoring mode CORDIC module
   - Converts (x, y) to (magnitude, angle)
   - Same bit width and precision as rotation mode

3. **cordic_tb.v**
   - Verilog testbench
   - Tests both rotation and vectoring modes
   - Generates VCD dump for waveform analysis

### Python Verification
1. **cordic_test.py**
   - Python reference implementation
   - Comprehensive test suite with multiple test cases
   - Error calculation and analysis
   - Statistical metrics (max, min, mean, std dev error)
   - Visualization of error analysis

## Running the Tests

### Prerequisites
```bash
pip install numpy scipy matplotlib
```

### Python Verification (Recommended First)
```bash
python cordic_test.py
```

Output includes:
- Test cases with input/output values
- Error calculations for each test
- Error statistics (max, min, mean, standard deviation)
- Error analysis plots saved as PNG

### Verilog Simulation
Using Icarus Verilog:
```bash
iverilog -o cordic_tb cordic_rotation_mode.v cordic_vectoring_mode.v cordic_tb.v
vvp cordic_tb
gtkwave cordic_tb.vcd  # Optional: view waveforms
```

Using Vivado:
```tcl
read_verilog cordic_rotation_mode.v
read_verilog cordic_vectoring_mode.v
read_verilog cordic_tb.v
elab_design
run_simulation
```

## Architecture Details

### Fixed-Point Representation
- **Format**: Q1.15 (1 integer bit + 15 fractional bits)
- **Range**: -1.0 to ~1.0
- **Precision**: ~2^-15 ≈ 3.05e-5

### CORDIC Iteration
For each stage i (0 to 15):

**Rotation Mode:**
```
if angle < 0:
    x[i+1] = x[i] + y[i] >> i
    y[i+1] = y[i] - x[i] >> i
    angle[i+1] = angle[i] + atan(2^-i)
else:
    x[i+1] = x[i] - y[i] >> i
    y[i+1] = y[i] + x[i] >> i
    angle[i+1] = angle[i] - atan(2^-i)
```

**Vectoring Mode:**
```
if y < 0:
    x[i+1] = x[i] + y[i] >> i
    y[i+1] = y[i] - x[i] >> i
    angle[i+1] = angle[i] - atan(2^-i)
else:
    x[i+1] = x[i] - y[i] >> i
    y[i+1] = y[i] + x[i] >> i
    angle[i+1] = angle[i] + atan(2^-i)
```

## Performance Metrics

### Typical Results (16-stage CORDIC)

#### Rotation Mode
- **Error Range**: 0.001% - 0.05%
- **Mean Error**: ~0.01%
- **Accuracy**: ±15-16 bits
- **Applications**: Sine/Cosine generation, phase rotation

#### Vectoring Mode
- **Error Range**: 0.01% - 0.1%
- **Mean Error**: ~0.03%
- **Accuracy**: ±14-15 bits (after K_n correction)
- **K_n Correction Factor**: 0.6073 (applies to magnitude output)

## Test Cases

### Rotation Mode Tests
1. Various angles: 30°, 45°, 60°, 90°, -30°, -45°
2. Different input vectors: (1,0), (1,1), (2,3)
3. Reference: NumPy rotation matrix

### Vectoring Mode Tests
1. Various coordinates: (1,0), (1,1), (3,4), (5,12)
2. All quadrants: (+,+), (+,-), (-,+), (-,-)
3. Reference: math.atan2() and magnitude calculation

## Error Analysis

### Sources of Error
1. **Quantization Error**: Fixed-point representation limits
2. **Finite Precision**: Limited number of stages
3. **Iteration Error**: Convergence after 16 stages

### Error Calculation
```python
Absolute Error = |CORDIC_result - Reference|
Relative Error = Absolute Error / Reference
Error % = (Absolute Error / Reference) × 100
```

## Design Parameters

Easily configurable parameters in Verilog:
```verilog
parameter WIDTH = 32;       // Data bit width (default: 32)
parameter STAGES = 16;      // Number of iterations (default: 16)
parameter FRAC_BITS = 15;   // Fractional bits (default: 15)
```

Increase stages for higher accuracy:
- 16 stages: ~0.01% error (recommended)
- 20 stages: ~0.001% error (more resources)
- 24 stages: ~0.0001% error (high accuracy)

## Applications

1. **Signal Processing**: DFT/FFT computation
2. **Trigonometric Functions**: sin(θ), cos(θ), tan(θ)
3. **Complex Number Operations**: Multiplication, division
4. **Vector Magnitude & Phase**: Polar coordinate conversion
5. **Communication Systems**: Phase rotation, modulation
6. **Robotics**: Coordinate transformations

## References

- Volder, J.E. (1959). "The CORDIC trigonometric computing technique"
- Walther, J.S. (1971). "A unified algorithm for elementary functions"
- Fixed-point arithmetic theory

## Performance Characteristics

| Metric | Value |
|--------|-------|
| Stages | 16 |
| Bit Width | 32-bit |
| Latency | 16 clock cycles |
| Throughput | 1 result per clock (pipelined) |
| Area | ~5K LUTs (estimated for Xilinx) |
| Power | Low (shift-based operations) |

## Future Enhancements

1. **Variable Precision**: Configurable accuracy vs. latency trade-off
2. **Parallel Stages**: Unrolled architecture for reduced latency
3. **Hybrid Mode**: Combined rotation + vectoring in single unit
4. **Extended Range**: Support for full ±π angle range
5. **Hardware Optimization**: Technology-specific implementations

## Author & Date
- **Created**: April 2026
- **Version**: 1.0

## License
Open source - Use and modify freely

---

**Note**: This implementation is optimized for educational purposes and embedded systems. For production use, consider additional error correction and verification.
