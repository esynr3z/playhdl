`default_nettype none

module tb;
    import uvm_pkg::*;
    `include "uvm_macros.svh"

    bit clk = 0;
    always #5 clk = ~clk;

    initial begin
        `uvm_info("tb", "Hello world!", UVM_LOW);
        repeat (10) @(posedge clk);
        $finish;
    end

    initial begin
        $dumpfile("tb.vcd");
        $dumpvars(0, tb);
    end
endmodule
