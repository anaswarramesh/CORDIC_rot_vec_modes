// CORDIC Vectoring Mode - 16 Stages
// Converts Cartesian coordinates to Polar (Magnitude & Angle)
// N-bit fixed point arithmetic, Q2.30 format (scale = 2^30)
// Input coordinates use Q2.30: real_value = fixed_value / 2^30
// Output magnitude is raw CORDIC value (scaled by K_n ~1.6468); divide by K_n to correct
// Output angle is in Q2.30 radians
// Author: CORDIC Design
// Date: 2026

module cordic_vectoring_mode #(
    parameter WIDTH = 32,           // Bit width of data
    parameter STAGES = 16,          // Number of CORDIC stages
    parameter FRAC_BITS = 30        // Fractional bits for fixed-point (Q2.30)
) (
    input clk,
    input rst,
    input valid_in,
    input signed [WIDTH-1:0] x_in,  // Input X coordinate
    input signed [WIDTH-1:0] y_in,  // Input Y coordinate
    output reg valid_out,
    output reg signed [WIDTH-1:0] magnitude, // Output magnitude
    output reg signed [WIDTH-1:0] angle      // Output angle
);

// CORDIC rotation constants
reg signed [WIDTH-1:0] atan_lut [0:15];

// Initialize LUT with precomputed atan values in Q2.30 fixed-point format
// atan(2^-i) * 2^30  for i = 0 to 15
initial begin
    atan_lut[0]  = 32'h3243F6A9;  // atan(2^0)  = 0.785398163 rad (45.0000 deg)
    atan_lut[1]  = 32'h1DAC6705;  // atan(2^-1) = 0.463647609 rad (26.5651 deg)
    atan_lut[2]  = 32'h0FADBAFD;  // atan(2^-2) = 0.244978663 rad (14.0362 deg)
    atan_lut[3]  = 32'h07F56EA7;  // atan(2^-3) = 0.124354995 rad ( 7.1250 deg)
    atan_lut[4]  = 32'h03FEAB77;  // atan(2^-4) = 0.062418810 rad ( 3.5763 deg)
    atan_lut[5]  = 32'h01FFD55C;  // atan(2^-5) = 0.031239833 rad ( 1.7899 deg)
    atan_lut[6]  = 32'h00FFFAAB;  // atan(2^-6) = 0.015623729 rad ( 0.8952 deg)
    atan_lut[7]  = 32'h007FFF55;  // atan(2^-7) = 0.007812341 rad ( 0.4476 deg)
    atan_lut[8]  = 32'h003FFFEB;  // atan(2^-8) = 0.003906230 rad ( 0.2238 deg)
    atan_lut[9]  = 32'h001FFFFD;  // atan(2^-9) = 0.001953123 rad ( 0.1119 deg)
    atan_lut[10] = 32'h00100000;  // atan(2^-10)= 0.000976562 rad ( 0.0560 deg)
    atan_lut[11] = 32'h00080000;  // atan(2^-11)= 0.000488281 rad ( 0.0280 deg)
    atan_lut[12] = 32'h00040000;  // atan(2^-12)= 0.000244141 rad ( 0.0140 deg)
    atan_lut[13] = 32'h00020000;  // atan(2^-13)= 0.000122070 rad ( 0.0070 deg)
    atan_lut[14] = 32'h00010000;  // atan(2^-14)= 0.000061035 rad ( 0.0035 deg)
    atan_lut[15] = 32'h00008000;  // atan(2^-15)= 0.000030518 rad ( 0.0017 deg)
end

reg signed [WIDTH-1:0] x_stages [0:STAGES];
reg signed [WIDTH-1:0] y_stages [0:STAGES];
reg signed [WIDTH-1:0] angle_stages [0:STAGES];
reg valid_stages [0:STAGES];

integer stage;

always @(posedge clk or posedge rst) begin
    if (rst) begin
        valid_out <= 1'b0;
        magnitude <= 32'b0;
        angle <= 32'b0;
    end else begin
        x_stages[0] <= x_in;
        y_stages[0] <= y_in;
        angle_stages[0] <= 32'b0;
        valid_stages[0] <= valid_in;
        
        // CORDIC iterations
        for (stage = 0; stage < STAGES; stage = stage + 1) begin
            if (y_stages[stage][WIDTH-1] == 1'b0) begin
                // Y is non-negative: rotate CW to drive Y toward zero
                x_stages[stage+1] <= x_stages[stage] + (y_stages[stage] >>> stage);
                y_stages[stage+1] <= y_stages[stage] - (x_stages[stage] >>> stage);
                angle_stages[stage+1] <= angle_stages[stage] + atan_lut[stage];
            end else begin
                // Y is negative: rotate CCW to drive Y toward zero
                x_stages[stage+1] <= x_stages[stage] - (y_stages[stage] >>> stage);
                y_stages[stage+1] <= y_stages[stage] + (x_stages[stage] >>> stage);
                angle_stages[stage+1] <= angle_stages[stage] - atan_lut[stage];
            end
            valid_stages[stage+1] <= valid_stages[stage];
        end
        
        magnitude <= x_stages[STAGES];
        angle <= angle_stages[STAGES];
        valid_out <= valid_stages[STAGES];
    end
end

endmodule
