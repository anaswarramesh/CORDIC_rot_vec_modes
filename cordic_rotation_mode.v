// CORDIC Rotation Mode - 16 Stages
// Rotates an input vector by a given angle
// N-bit fixed point arithmetic
// Author: CORDIC Design
// Date: 2026

module cordic_rotation_mode #(
    parameter WIDTH = 32,           // Bit width of data
    parameter STAGES = 16,          // Number of CORDIC stages
    parameter FRAC_BITS = 15        // Fractional bits for fixed-point
) (
    input clk,
    input rst,
    input valid_in,
    input signed [WIDTH-1:0] x_in,  // Input X coordinate
    input signed [WIDTH-1:0] y_in,  // Input Y coordinate
    input signed [WIDTH-1:0] angle_in, // Input rotation angle (in fixed-point radians)
    output reg valid_out,
    output reg signed [WIDTH-1:0] x_out, // Rotated X
    output reg signed [WIDTH-1:0] y_out, // Rotated Y
    output reg signed [WIDTH-1:0] angle_out // Remaining angle
);

// CORDIC rotation constants (precomputed atan values in fixed-point)
// atan(2^-i) for i = 0 to 15
reg signed [WIDTH-1:0] atan_lut [0:15];

integer i, stage;
reg signed [WIDTH-1:0] x_temp, y_temp, angle_temp;
reg signed [WIDTH-1:0] x_shift, y_shift;
reg signed [WIDTH-1:0] x_stages [0:STAGES];
reg signed [WIDTH-1:0] y_stages [0:STAGES];
reg signed [WIDTH-1:0] angle_stages [0:STAGES];
reg valid_stages [0:STAGES];

// Initialize LUT with precomputed atan values (Q1.15 format for 16-bit)
// These are atan(2^-i) values scaled to fixed-point
initial begin
    atan_lut[0]  = 32'h2C8CBE8F;  // atan(1) ≈ 0.7853981634
    atan_lut[1]  = 32'h15B5BA8C;  // atan(0.5) ≈ 0.4636476090
    atan_lut[2]  = 32'h0B5B94FB;  // atan(0.25) ≈ 0.2449786631
    atan_lut[3]  = 32'h05B5B594;  // atan(0.125) ≈ 0.1243556048
    atan_lut[4]  = 32'h02DAD94C;  // atan(0.0625) ≈ 0.0624188100
    atan_lut[5]  = 32'h016D6A58;  // atan(0.03125) ≈ 0.0312398334
    atan_lut[6]  = 32'h00B5B99E;  // atan(0.015625) ≈ 0.0156237286
    atan_lut[7]  = 32'h005ADAD7;  // atan(0.0078125) ≈ 0.0078123410
    atan_lut[8]  = 32'h002D6D6E;  // atan(0.00390625) ≈ 0.0039062301
    atan_lut[9]  = 32'h0016B6B7;  // atan(0.001953125) ≈ 0.0019531226
    atan_lut[10] = 32'h000B5B5C;  // atan(0.0009765625) ≈ 0.0009765621
    atan_lut[11] = 32'h0005ADAE;  // atan(0.00048828125) ≈ 0.0004882812
    atan_lut[12] = 32'h0002D6D7;  // atan(0.000244140625) ≈ 0.0002441406
    atan_lut[13] = 32'h00016B6B;  // atan(0.0001220703125) ≈ 0.0001220703
    atan_lut[14] = 32'h0000B5B6;  // atan(0.00006103515625) ≈ 0.0000610352
    atan_lut[15] = 32'h00005ADB;  // atan(0.000030517578125) ≈ 0.0000305176
end

// Pipeline stages
always @(posedge clk or posedge rst) begin
    if (rst) begin
        valid_out <= 1'b0;
        x_out <= 32'b0;
        y_out <= 32'b0;
        angle_out <= 32'b0;
    end else begin
        // Initialize first stage
        x_stages[0] <= x_in;
        y_stages[0] <= y_in;
        angle_stages[0] <= angle_in;
        valid_stages[0] <= valid_in;
        
        // CORDIC iterations (16 stages)
        for (stage = 0; stage < STAGES; stage = stage + 1) begin
            if (angle_stages[stage][WIDTH-1] == 1'b1) begin
                // Angle is negative, rotate clockwise (subtract angle)
                x_stages[stage+1] <= x_stages[stage] + (y_stages[stage] >>> stage);
                y_stages[stage+1] <= y_stages[stage] - (x_stages[stage] >>> stage);
                angle_stages[stage+1] <= angle_stages[stage] + atan_lut[stage];
            end else begin
                // Angle is positive, rotate counter-clockwise (add angle)
                x_stages[stage+1] <= x_stages[stage] - (y_stages[stage] >>> stage);
                y_stages[stage+1] <= y_stages[stage] + (x_stages[stage] >>> stage);
                angle_stages[stage+1] <= angle_stages[stage] - atan_lut[stage];
            end
            valid_stages[stage+1] <= valid_stages[stage];
        end
        
        // Output from last stage
        x_out <= x_stages[STAGES];
        y_out <= y_stages[STAGES];
        angle_out <= angle_stages[STAGES];
        valid_out <= valid_stages[STAGES];
    end
end

endmodule
