`timescale 1ns/1ps
`default_nettype none

module tb;
    reg clk = 0;
    always #5 clk = ~clk;

    initial begin
        #100;
        $display("Hello world!");
        #100;
        $finish;
    end

    initial begin
        $dumpfile("tb.vcd");
        $dumpvars(0, tb);
    end
endmodule
