import cocotb
import random
import logging
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ClockCycles, ReadOnly
from cocotb.clock import Clock

from cocotbext.dvi.tmds import TMDS


def list_hex(L):
    return "["+ ",".join(["{:x}".format(x) for x in L]) + "]"



async def reset(wire,clock):
    wire.value = 1
    await ClockCycles(clock,3)
    wire.value = 0

async def validate_tmds(rgb,control,tmds,enable,clock,reset,correct_response_list):
    tmds_model = TMDS()
    while True:
        await RisingEdge(clock)
        await ReadOnly()
        # assert( tmds.value.integer == prev_cycle_output )
        # print(tmds.value,tmds_model.bias,"{:010b}".format(prev_cycle_output))
        correct_response_list.append( tmds_model.encode(
            rgb.value.integer,
            de = enable.value.integer
            ))

async def monitor_encoded_output(tmds,clock,reset,captured_response_list):
    wait_cycles = 3
    while True:
        await RisingEdge(clock)
        await ReadOnly()
        if (wait_cycles == 0):
            captured_response_list.append( tmds.value.integer )
        else:
            wait_cycles -= 1


async def drive_video_data(wire,clock,data):
    for byteval in data:
        wire.value = byteval
        await ClockCycles(clock,1)


def encode_sequence(tmds_model,data):
    out = []
    for byteval in data:
        out.append( tmds_model.encode(byteval) )
    return out


@cocotb.test()
async def sample_unencoded_data(dut):
    """ Pass a small number of data bytes through TMDS, demo currently-incorrect bias calculation """ 
    clk = dut.PixelClk
    rst = dut.aRst
    rgb = dut.pDataOut
    c0 = dut.pC0
    c1 = dut.pC1
    vde = dut.pVde
    tmds = dut.pDataOutRaw


    cocotb.start_soon( Clock(clk,10,units='ns').start() )

    c0.value = 0
    c1.value = 0
    rgb.value = 0
    vde.value = 0
    predicted_responses = []
    captured_responses = []
    cocotb.start_soon( validate_tmds(rgb,c0,tmds,vde,clk,rst,predicted_responses ))
    cocotb.start_soon( monitor_encoded_output(tmds,clk,rst, captured_responses) )
    await reset(rst,clk)

    video_data = [
            0x88,
            0x21,
            0x9a,
            0x8a,
            0x01,
            0xab,
            0xff
            ]
    await ClockCycles(clk,5)
    vde.value = 1
    c0.value = 0
    
    await drive_video_data(rgb,clk,video_data)
    await ClockCycles(clk,3)
    # cut off extra responses that haven't pipelined through TMDS encoder (3 stage delay)
    predicted_responses = predicted_responses[:len(captured_responses)]
    dut._log.info(f"Predicted: {list_hex(predicted_responses)}")
    dut._log.info(f"Captured: {list_hex(captured_responses)}")
    assert(predicted_responses == captured_responses) 


