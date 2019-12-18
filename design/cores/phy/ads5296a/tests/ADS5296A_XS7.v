/* Machine-generated using Migen */
module top(
	input adclk_i_p,
	input adclk_i_n,
	input lclk_i_p,
	input lclk_i_n,
	input dat_0_i_p,
	input dat_0_i_n,
	input dat_1_i_p,
	input dat_1_i_n,
	input dat_2_i_p,
	input dat_2_i_n,
	input dat_3_i_p,
	input dat_3_i_n,
	input dat_4_i_p,
	input dat_4_i_n,
	input dat_5_i_p,
	input dat_5_i_n,
	input dat_6_i_p,
	input dat_6_i_n,
	input dat_7_i_p,
	input dat_7_i_n,
	input sys_clk,
	input sys_rst,
	output data_clk_o,
	output reg bitslip_done,
	output [9:0] data_0_o,
	output [9:0] data_1_o,
	output [9:0] data_2_o,
	output [9:0] data_3_o,
	output [9:0] data_4_o,
	output [9:0] data_5_o,
	output [9:0] data_6_o,
	output [9:0] data_7_o,
	input [4:0] idelay_val_0_i,
	input [4:0] idelay_val_1_i,
	input [4:0] idelay_val_2_i,
	input [4:0] idelay_val_3_i,
	input [4:0] idelay_val_4_i,
	input [4:0] idelay_val_5_i,
	input [4:0] idelay_val_6_i,
	input [4:0] idelay_val_7_i,
	input [4:0] idelay_val_8_i,
	input idelay_ld_i,
	input rst_i,
	input ref_clk_200M
);

wire [9:0] dut_data_8_o;
wire dut_rdy;
wire dut_line_delayed_0;
wire dut_line_delayed_1;
wire dut_line_delayed_2;
wire dut_line_delayed_3;
wire dut_line_delayed_4;
wire dut_line_delayed_5;
wire dut_line_delayed_6;
wire dut_line_delayed_7;
wire dut_line_delayed_8;
wire dut_line_buffer0;
wire dut_line_buffer1;
wire dut_line_buffer2;
wire dut_line_buffer3;
wire dut_line_buffer4;
wire dut_line_buffer5;
wire dut_line_buffer6;
wire dut_line_buffer7;
wire dut_line_buffer8;
wire dut_lclk_ibuf;
wire dut_lclk_bufio;
wire adclk_clkdiv_clk;
wire adclk_clkdiv_rst;
reg dut_bitslip = 1'd0;
reg [3:0] dut_bitslip_cnt = 4'd0;
wire dut_shift1_0;
wire dut_shift2_0;
wire dut_output_test_master_0;
wire dut_shift1_1;
wire dut_shift2_1;
wire dut_output_test_master_1;
wire dut_shift1_2;
wire dut_shift2_2;
wire dut_output_test_master_2;
wire dut_shift1_3;
wire dut_shift2_3;
wire dut_output_test_master_3;
wire dut_shift1_4;
wire dut_shift2_4;
wire dut_output_test_master_4;
wire dut_shift1_5;
wire dut_shift2_5;
wire dut_output_test_master_5;
wire dut_shift1_6;
wire dut_shift2_6;
wire dut_output_test_master_6;
wire dut_shift1_7;
wire dut_shift2_7;
wire dut_output_test_master_7;
wire dut_shift1_8;
wire dut_shift2_8;
wire dut_output_test_master_8;

// synthesis translate_off
reg dummy_s;
initial dummy_s <= 1'd0;
// synthesis translate_on

assign adclk_clkdiv_rst = (~dut_rdy);

always @(posedge adclk_clkdiv_clk) begin
	dut_bitslip <= 1'd0;
	dut_bitslip_cnt <= (dut_bitslip_cnt + 1'd1);
	bitslip_done <= (dut_data_8_o == 10'd992);
	if ((dut_bitslip_cnt == 1'd0)) begin
		if ((~bitslip_done)) begin
			dut_bitslip <= 1'd1;
		end
	end
	if (adclk_clkdiv_rst) begin
		bitslip_done <= 1'd0;
		dut_bitslip <= 1'd0;
		dut_bitslip_cnt <= 4'd0;
	end
end

IDELAYCTRL IDELAYCTRL(
	.REFCLK(ref_clk_200M),
	.RST(sys_rst),
	.RDY(dut_rdy)
);

IDELAYE2 #(
	.DELAY_SRC("IDATAIN"),
	.HIGH_PERFORMANCE_MODE("TRUE"),
	.IDELAY_TYPE("VAR_LOAD"),
	.IDELAY_VALUE(1'd0),
	.PIPE_SEL("FALSE"),
	.REFCLK_FREQUENCY(200.0),
	.SIGNAL_PATTERN("DATA")
) IDELAYE2 (
	.C(sys_clk),
	.CE(1'd0),
	.CINVCTRL(1'd0),
	.CNTVALUEIN(idelay_val_0_i),
	.DATAIN(1'd0),
	.IDATAIN(dut_line_buffer0),
	.INC(1'd0),
	.LD(idelay_ld_i),
	.LDPIPEEN(1'd0),
	.REGRST(sys_rst),
	.DATAOUT(dut_line_delayed_0)
);

IDELAYE2 #(
	.DELAY_SRC("IDATAIN"),
	.HIGH_PERFORMANCE_MODE("TRUE"),
	.IDELAY_TYPE("VAR_LOAD"),
	.IDELAY_VALUE(1'd0),
	.PIPE_SEL("FALSE"),
	.REFCLK_FREQUENCY(200.0),
	.SIGNAL_PATTERN("DATA")
) IDELAYE2_1 (
	.C(sys_clk),
	.CE(1'd0),
	.CINVCTRL(1'd0),
	.CNTVALUEIN(idelay_val_1_i),
	.DATAIN(1'd0),
	.IDATAIN(dut_line_buffer1),
	.INC(1'd0),
	.LD(idelay_ld_i),
	.LDPIPEEN(1'd0),
	.REGRST(sys_rst),
	.DATAOUT(dut_line_delayed_1)
);

IDELAYE2 #(
	.DELAY_SRC("IDATAIN"),
	.HIGH_PERFORMANCE_MODE("TRUE"),
	.IDELAY_TYPE("VAR_LOAD"),
	.IDELAY_VALUE(1'd0),
	.PIPE_SEL("FALSE"),
	.REFCLK_FREQUENCY(200.0),
	.SIGNAL_PATTERN("DATA")
) IDELAYE2_2 (
	.C(sys_clk),
	.CE(1'd0),
	.CINVCTRL(1'd0),
	.CNTVALUEIN(idelay_val_2_i),
	.DATAIN(1'd0),
	.IDATAIN(dut_line_buffer2),
	.INC(1'd0),
	.LD(idelay_ld_i),
	.LDPIPEEN(1'd0),
	.REGRST(sys_rst),
	.DATAOUT(dut_line_delayed_2)
);

IDELAYE2 #(
	.DELAY_SRC("IDATAIN"),
	.HIGH_PERFORMANCE_MODE("TRUE"),
	.IDELAY_TYPE("VAR_LOAD"),
	.IDELAY_VALUE(1'd0),
	.PIPE_SEL("FALSE"),
	.REFCLK_FREQUENCY(200.0),
	.SIGNAL_PATTERN("DATA")
) IDELAYE2_3 (
	.C(sys_clk),
	.CE(1'd0),
	.CINVCTRL(1'd0),
	.CNTVALUEIN(idelay_val_3_i),
	.DATAIN(1'd0),
	.IDATAIN(dut_line_buffer3),
	.INC(1'd0),
	.LD(idelay_ld_i),
	.LDPIPEEN(1'd0),
	.REGRST(sys_rst),
	.DATAOUT(dut_line_delayed_3)
);

IDELAYE2 #(
	.DELAY_SRC("IDATAIN"),
	.HIGH_PERFORMANCE_MODE("TRUE"),
	.IDELAY_TYPE("VAR_LOAD"),
	.IDELAY_VALUE(1'd0),
	.PIPE_SEL("FALSE"),
	.REFCLK_FREQUENCY(200.0),
	.SIGNAL_PATTERN("DATA")
) IDELAYE2_4 (
	.C(sys_clk),
	.CE(1'd0),
	.CINVCTRL(1'd0),
	.CNTVALUEIN(idelay_val_4_i),
	.DATAIN(1'd0),
	.IDATAIN(dut_line_buffer4),
	.INC(1'd0),
	.LD(idelay_ld_i),
	.LDPIPEEN(1'd0),
	.REGRST(sys_rst),
	.DATAOUT(dut_line_delayed_4)
);

IDELAYE2 #(
	.DELAY_SRC("IDATAIN"),
	.HIGH_PERFORMANCE_MODE("TRUE"),
	.IDELAY_TYPE("VAR_LOAD"),
	.IDELAY_VALUE(1'd0),
	.PIPE_SEL("FALSE"),
	.REFCLK_FREQUENCY(200.0),
	.SIGNAL_PATTERN("DATA")
) IDELAYE2_5 (
	.C(sys_clk),
	.CE(1'd0),
	.CINVCTRL(1'd0),
	.CNTVALUEIN(idelay_val_5_i),
	.DATAIN(1'd0),
	.IDATAIN(dut_line_buffer5),
	.INC(1'd0),
	.LD(idelay_ld_i),
	.LDPIPEEN(1'd0),
	.REGRST(sys_rst),
	.DATAOUT(dut_line_delayed_5)
);

IDELAYE2 #(
	.DELAY_SRC("IDATAIN"),
	.HIGH_PERFORMANCE_MODE("TRUE"),
	.IDELAY_TYPE("VAR_LOAD"),
	.IDELAY_VALUE(1'd0),
	.PIPE_SEL("FALSE"),
	.REFCLK_FREQUENCY(200.0),
	.SIGNAL_PATTERN("DATA")
) IDELAYE2_6 (
	.C(sys_clk),
	.CE(1'd0),
	.CINVCTRL(1'd0),
	.CNTVALUEIN(idelay_val_6_i),
	.DATAIN(1'd0),
	.IDATAIN(dut_line_buffer6),
	.INC(1'd0),
	.LD(idelay_ld_i),
	.LDPIPEEN(1'd0),
	.REGRST(sys_rst),
	.DATAOUT(dut_line_delayed_6)
);

IDELAYE2 #(
	.DELAY_SRC("IDATAIN"),
	.HIGH_PERFORMANCE_MODE("TRUE"),
	.IDELAY_TYPE("VAR_LOAD"),
	.IDELAY_VALUE(1'd0),
	.PIPE_SEL("FALSE"),
	.REFCLK_FREQUENCY(200.0),
	.SIGNAL_PATTERN("DATA")
) IDELAYE2_7 (
	.C(sys_clk),
	.CE(1'd0),
	.CINVCTRL(1'd0),
	.CNTVALUEIN(idelay_val_7_i),
	.DATAIN(1'd0),
	.IDATAIN(dut_line_buffer7),
	.INC(1'd0),
	.LD(idelay_ld_i),
	.LDPIPEEN(1'd0),
	.REGRST(sys_rst),
	.DATAOUT(dut_line_delayed_7)
);

IDELAYE2 #(
	.DELAY_SRC("IDATAIN"),
	.HIGH_PERFORMANCE_MODE("TRUE"),
	.IDELAY_TYPE("VAR_LOAD"),
	.IDELAY_VALUE(1'd0),
	.PIPE_SEL("FALSE"),
	.REFCLK_FREQUENCY(200.0),
	.SIGNAL_PATTERN("DATA")
) IDELAYE2_8 (
	.C(sys_clk),
	.CE(1'd0),
	.CINVCTRL(1'd0),
	.CNTVALUEIN(idelay_val_8_i),
	.DATAIN(1'd0),
	.IDATAIN(dut_line_buffer8),
	.INC(1'd0),
	.LD(idelay_ld_i),
	.LDPIPEEN(1'd0),
	.REGRST(sys_rst),
	.DATAOUT(dut_line_delayed_8)
);

BUFIO BUFIO(
	.I(dut_lclk_ibuf),
	.O(dut_lclk_bufio)
);

BUFR #(
	.BUFR_DIVIDE("5")
) BUFR (
	.CE(1'd1),
	.CLR(1'd0),
	.I(dut_lclk_ibuf),
	.O(adclk_clkdiv_clk)
);

BUFG BUFG(
	.I(adclk_clkdiv_clk),
	.O(data_clk_o)
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("MASTER")
) ISERDESE2 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DDLY(dut_line_delayed_0),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.O(dut_output_test_master_0),
	.Q1(data_0_o[0]),
	.Q2(data_0_o[1]),
	.Q3(data_0_o[2]),
	.Q4(data_0_o[3]),
	.Q5(data_0_o[4]),
	.Q6(data_0_o[5]),
	.Q7(data_0_o[6]),
	.Q8(data_0_o[7]),
	.SHIFTOUT1(dut_shift1_0),
	.SHIFTOUT2(dut_shift2_0)
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("SLAVE")
) ISERDESE2_1 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.SHIFTIN1(dut_shift1_0),
	.SHIFTIN2(dut_shift2_0),
	.Q3(data_0_o[8]),
	.Q4(data_0_o[9])
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("MASTER")
) ISERDESE2_2 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DDLY(dut_line_delayed_1),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.O(dut_output_test_master_1),
	.Q1(data_1_o[0]),
	.Q2(data_1_o[1]),
	.Q3(data_1_o[2]),
	.Q4(data_1_o[3]),
	.Q5(data_1_o[4]),
	.Q6(data_1_o[5]),
	.Q7(data_1_o[6]),
	.Q8(data_1_o[7]),
	.SHIFTOUT1(dut_shift1_1),
	.SHIFTOUT2(dut_shift2_1)
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("SLAVE")
) ISERDESE2_3 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.SHIFTIN1(dut_shift1_1),
	.SHIFTIN2(dut_shift2_1),
	.Q3(data_1_o[8]),
	.Q4(data_1_o[9])
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("MASTER")
) ISERDESE2_4 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DDLY(dut_line_delayed_2),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.O(dut_output_test_master_2),
	.Q1(data_2_o[0]),
	.Q2(data_2_o[1]),
	.Q3(data_2_o[2]),
	.Q4(data_2_o[3]),
	.Q5(data_2_o[4]),
	.Q6(data_2_o[5]),
	.Q7(data_2_o[6]),
	.Q8(data_2_o[7]),
	.SHIFTOUT1(dut_shift1_2),
	.SHIFTOUT2(dut_shift2_2)
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("SLAVE")
) ISERDESE2_5 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.SHIFTIN1(dut_shift1_2),
	.SHIFTIN2(dut_shift2_2),
	.Q3(data_2_o[8]),
	.Q4(data_2_o[9])
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("MASTER")
) ISERDESE2_6 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DDLY(dut_line_delayed_3),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.O(dut_output_test_master_3),
	.Q1(data_3_o[0]),
	.Q2(data_3_o[1]),
	.Q3(data_3_o[2]),
	.Q4(data_3_o[3]),
	.Q5(data_3_o[4]),
	.Q6(data_3_o[5]),
	.Q7(data_3_o[6]),
	.Q8(data_3_o[7]),
	.SHIFTOUT1(dut_shift1_3),
	.SHIFTOUT2(dut_shift2_3)
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("SLAVE")
) ISERDESE2_7 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.SHIFTIN1(dut_shift1_3),
	.SHIFTIN2(dut_shift2_3),
	.Q3(data_3_o[8]),
	.Q4(data_3_o[9])
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("MASTER")
) ISERDESE2_8 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DDLY(dut_line_delayed_4),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.O(dut_output_test_master_4),
	.Q1(data_4_o[0]),
	.Q2(data_4_o[1]),
	.Q3(data_4_o[2]),
	.Q4(data_4_o[3]),
	.Q5(data_4_o[4]),
	.Q6(data_4_o[5]),
	.Q7(data_4_o[6]),
	.Q8(data_4_o[7]),
	.SHIFTOUT1(dut_shift1_4),
	.SHIFTOUT2(dut_shift2_4)
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("SLAVE")
) ISERDESE2_9 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.SHIFTIN1(dut_shift1_4),
	.SHIFTIN2(dut_shift2_4),
	.Q3(data_4_o[8]),
	.Q4(data_4_o[9])
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("MASTER")
) ISERDESE2_10 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DDLY(dut_line_delayed_5),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.O(dut_output_test_master_5),
	.Q1(data_5_o[0]),
	.Q2(data_5_o[1]),
	.Q3(data_5_o[2]),
	.Q4(data_5_o[3]),
	.Q5(data_5_o[4]),
	.Q6(data_5_o[5]),
	.Q7(data_5_o[6]),
	.Q8(data_5_o[7]),
	.SHIFTOUT1(dut_shift1_5),
	.SHIFTOUT2(dut_shift2_5)
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("SLAVE")
) ISERDESE2_11 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.SHIFTIN1(dut_shift1_5),
	.SHIFTIN2(dut_shift2_5),
	.Q3(data_5_o[8]),
	.Q4(data_5_o[9])
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("MASTER")
) ISERDESE2_12 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DDLY(dut_line_delayed_6),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.O(dut_output_test_master_6),
	.Q1(data_6_o[0]),
	.Q2(data_6_o[1]),
	.Q3(data_6_o[2]),
	.Q4(data_6_o[3]),
	.Q5(data_6_o[4]),
	.Q6(data_6_o[5]),
	.Q7(data_6_o[6]),
	.Q8(data_6_o[7]),
	.SHIFTOUT1(dut_shift1_6),
	.SHIFTOUT2(dut_shift2_6)
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("SLAVE")
) ISERDESE2_13 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.SHIFTIN1(dut_shift1_6),
	.SHIFTIN2(dut_shift2_6),
	.Q3(data_6_o[8]),
	.Q4(data_6_o[9])
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("MASTER")
) ISERDESE2_14 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DDLY(dut_line_delayed_7),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.O(dut_output_test_master_7),
	.Q1(data_7_o[0]),
	.Q2(data_7_o[1]),
	.Q3(data_7_o[2]),
	.Q4(data_7_o[3]),
	.Q5(data_7_o[4]),
	.Q6(data_7_o[5]),
	.Q7(data_7_o[6]),
	.Q8(data_7_o[7]),
	.SHIFTOUT1(dut_shift1_7),
	.SHIFTOUT2(dut_shift2_7)
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("SLAVE")
) ISERDESE2_15 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.SHIFTIN1(dut_shift1_7),
	.SHIFTIN2(dut_shift2_7),
	.Q3(data_7_o[8]),
	.Q4(data_7_o[9])
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("MASTER")
) ISERDESE2_16 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DDLY(dut_line_delayed_8),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.O(dut_output_test_master_8),
	.Q1(dut_data_8_o[0]),
	.Q2(dut_data_8_o[1]),
	.Q3(dut_data_8_o[2]),
	.Q4(dut_data_8_o[3]),
	.Q5(dut_data_8_o[4]),
	.Q6(dut_data_8_o[5]),
	.Q7(dut_data_8_o[6]),
	.Q8(dut_data_8_o[7]),
	.SHIFTOUT1(dut_shift1_8),
	.SHIFTOUT2(dut_shift2_8)
);

ISERDESE2 #(
	.DATA_RATE("DDR"),
	.DATA_WIDTH(4'd10),
	.INTERFACE_TYPE("NETWORKING"),
	.IOBDELAY("BOTH"),
	.NUM_CE(1'd1),
	.SERDES_MODE("SLAVE")
) ISERDESE2_17 (
	.BITSLIP(dut_bitslip),
	.CE1(1'd1),
	.CLK(dut_lclk_bufio),
	.CLKB((~dut_lclk_bufio)),
	.CLKDIV(adclk_clkdiv_clk),
	.CLKDIVP(1'd0),
	.DYNCLKDIVSEL(1'd0),
	.DYNCLKSEL(1'd0),
	.RST(adclk_clkdiv_rst),
	.SHIFTIN1(dut_shift1_8),
	.SHIFTIN2(dut_shift2_8),
	.Q3(dut_data_8_o[8]),
	.Q4(dut_data_8_o[9])
);

IBUFDS IBUFDS(
	.I(dat_0_i_p),
	.IB(dat_0_i_n),
	.O(dut_line_buffer0)
);

IBUFDS IBUFDS_1(
	.I(dat_1_i_p),
	.IB(dat_1_i_n),
	.O(dut_line_buffer1)
);

IBUFDS IBUFDS_2(
	.I(dat_2_i_p),
	.IB(dat_2_i_n),
	.O(dut_line_buffer2)
);

IBUFDS IBUFDS_3(
	.I(dat_3_i_p),
	.IB(dat_3_i_n),
	.O(dut_line_buffer3)
);

IBUFDS IBUFDS_4(
	.I(dat_4_i_p),
	.IB(dat_4_i_n),
	.O(dut_line_buffer4)
);

IBUFDS IBUFDS_5(
	.I(dat_5_i_p),
	.IB(dat_5_i_n),
	.O(dut_line_buffer5)
);

IBUFDS IBUFDS_6(
	.I(dat_6_i_p),
	.IB(dat_6_i_n),
	.O(dut_line_buffer6)
);

IBUFDS IBUFDS_7(
	.I(dat_7_i_p),
	.IB(dat_7_i_n),
	.O(dut_line_buffer7)
);

IBUFDS IBUFDS_8(
	.I(adclk_i_p),
	.IB(adclk_i_n),
	.O(dut_line_buffer8)
);

IBUFDS IBUFDS_9(
	.I(lclk_i_p),
	.IB(lclk_i_n),
	.O(dut_lclk_ibuf)
);

endmodule
