`timescale 1ns / 1ps

module cordic_tb;

parameter WIDTH = 32;
parameter STAGES = 16;
parameter FRAC_BITS = 15;
parameter CLK_PERIOD = 10;

reg clk, rst;
reg valid_in;
reg signed [WIDTH-1:0] x_in, y_in;
reg signed [WIDTH-1:0] angle_in, x_vec_in, y_vec_in;

wire valid_out_rot;
wire signed [WIDTH-1:0] x_out_rot, y_out_rot, angle_out_rot;

wire valid_out_vec;
wire signed [WIDTH-1:0] magnitude, angle_out_vec;

// Instantiate modules
cordic_rotation_mode #(.WIDTH(WIDTH), .STAGES(STAGES), .FRAC_BITS(FRAC_BITS))
    dut_rot (
        .clk(clk), .rst(rst), .valid_in(valid_in),
        .x_in(x_in), .y_in(y_in), .angle_in(angle_in),
        .valid_out(valid_out_rot), .x_out(x_out_rot), .y_out(y_out_rot), .angle_out(angle_out_rot)
    );

cordic_vectoring_mode #(.WIDTH(WIDTH), .STAGES(STAGES), .FRAC_BITS(FRAC_BITS))
    dut_vec (
        .clk(clk), .rst(rst), .valid_in(valid_in),
        .x_in(x_vec_in), .y_in(y_vec_in),
        .valid_out(valid_out_vec), .magnitude(magnitude), .angle(angle_out_vec)
    );

// Clock generation
initial begin
    clk = 0;
    forever #(CLK_PERIOD/2) clk = ~clk;
end

// Test stimuli
initial begin
    rst = 1;
    valid_in = 0;
    x_in = 0;
    y_in = 0;
    angle_in = 0;
    x_vec_in = 0;
    y_vec_in = 0;
    
    #20 rst = 0;
    
    // Test rotation mode - rotate (1, 0) by 45 degrees
    #10 valid_in = 1; x_in = 32'h4000_0000; y_in = 0; angle_in = 32'h2000_0000;
    #10 valid_in = 0;
    
    // Test vectoring mode - convert (1, 1) to polar
    #100 valid_in = 1; x_vec_in = 32'h4000_0000; y_vec_in = 32'h4000_0000;
    #10 valid_in = 0;
    
    #500 $finish;
end

// Monitor output
initial begin
    $monitor("Time=%0t | ROT: valid=%b x=%h y=%h | VEC: valid=%b mag=%h angle=%h",
             $time, valid_out_rot, x_out_rot, y_out_rot, valid_out_vec, magnitude, angle_out_vec);
end

initial begin
    $dumpfile("cordic_tb.vcd");
    $dumpvars(0, cordic_tb);
end

endmodule
