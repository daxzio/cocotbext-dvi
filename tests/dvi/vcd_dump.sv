module vcd_dump ();

   //`ifdef COCOTB_SIM
    `ifdef COCOTB_ICARUS
    initial begin
        $dumpfile ("dut.vcd");
        $dumpvars (0, dut);
        /* verilator lint_off STMTDLY */
        #1;
        /* verilator lint_on STMTDLY */
    end
    `endif    

endmodule
