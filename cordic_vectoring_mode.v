// CORDIC Vectoring Mode - 16 Stages
// Converts Cartesian coordinates to Polar (Magnitude & Angle)
// N-bit fixed point arithmetic
// Author: CORDIC Design
// Date: 2026

module cordic_vectoring_mode #(
    parameter WIDTH = 32,           // Bit width of data
    parameter STAGES = 16,          // Number of CORDIC stages
    parameter FRAC_BITS = 15        // Fractional bits for fixed-point
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

initial begin
    atan_lut[0]  = 32'h2C8CBE8F;  // atan(1)
    atan_lut[1]  = 32'h15B5BA8C;  // atan(0.5)
    atan_lut[2]  = 32'h0B5B94FB;  // atan(0.25)
    atan_lut[3]  = 32'h05B5B594;  // atan(0.125)
    atan_lut[4]  = 32'h02DAD94C;  // atan(0.0625)
    atan_lut[5]  = 32'h016D6A58;  // atan(0.03125)
    atan_lut[6]  = 32'h00B5B99E;  // atan(0.015625)
    atan_lut[7]  = 32'h005ADAD7;  // atan(0.0078125)
    atan_lut[8]  = 32'h002D6D6E;  // atan(0.00390625)
    atan_lut[9]  = 32'h0016B6B7;  // atan(0.001953125)
    atan_lut[10] = 32'h000B5B5C;  // atan(0.0009765625)
    atan_lut[11] = 32'h0005ADAE;  // atan(0.00048828125)
    atan_lut[12] = 32'h0002D6D7;  // atan(0.000244140625)
    atan_lut[13] = 32'h00016B6B;  // atan(0.0001220703125)
    atan_lut[14] = 32'h0000B5B6;  // atan(0.00006103515625)
    atan_lut[15] = 32'h00005ADB;  // atan(0.000030517578125)
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
            if (y_stages[stage][WIDTH-1] == 1'b1) begin
                // Y is negative, rotate clockwise
                x_stages[stage+1] <= x_stages[stage] + (y_stages[stage] >>> stage);
                y_stages[stage+1] <= y_stages[stage] - (x_stages[stage] >>> stage);
                angle_stages[stage+1] <= angle_stages[stage] - atan_lut[stage];
            end else begin
                // Y is positive, rotate counter-clockwise
                x_stages[stage+1] <= x_stages[stage] - (y_stages[stage] >>> stage);
                y_stages[stage+1] <= y_stages[stage] + (x_stages[stage] >>> stage);
                angle_stages[stage+1] <= angle_stages[stage] + atan_lut[stage];
            end
            valid_stages[stage+1] <= valid_stages[stage];
        end
        
        magnitude <= x_stages[STAGES];
        angle <= angle_stages[STAGES];
        valid_out <= valid_stages[STAGES];
    end
end

endmodule
