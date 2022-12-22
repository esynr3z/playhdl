`timescale 1ns/1ps
`default_nettype none

module tb;
    bit clk = 0;
    always #5 clk = ~clk;

    initial begin
        $display("Hello world!");
        repeat (10) @(posedge clk);
        $finish;
    end

    initial begin
        $dumpfile("tb.vcd");
        $dumpvars(0, tb);
    end
endmodule
