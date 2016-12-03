// Copyright (c) 2011, XMOS Ltd., All rights reserved
// This software is freely distributable under a derivative of the
// University of Illinois/NCSA Open Source License posted in
// LICENSE.txt and at <http://github.xcore.com/>

///////////////////////////////////////////////////////////////////////////////
//
// SPI Slave

#include <xs1.h>
#include <xclib.h>
#include <platform.h>
#include <print.h>
#include "rpi-spi.h"

void spi_slave_init(spi_slave_pins &p_spi)
{
    p_spi.flash_ss <: 1;               //Disable SPI flash on startKIT which is on same bus
    set_clock_on(p_spi.blk);           //Switch on clock block
    set_port_use_on(p_spi.ss);
    p_spi.ss :> void;                  //Make ss port an input
    set_port_pull_down(p_spi.ss);      //Enable pulldowns so that rest of port is in known state. Avoids spurious firing from noise
    set_port_use_on(p_spi.mosi);
    set_port_use_on(p_spi.miso);
    set_port_use_on(p_spi.sclk);
    set_port_no_inv(p_spi.sclk);

    // configure ports and clock blocks
    configure_clock_src(p_spi.blk, p_spi.sclk);
    configure_in_port(p_spi.mosi, p_spi.blk);
    configure_out_port(p_spi.miso, p_spi.blk, 0);
    set_port_strobed(p_spi.mosi);
    set_port_strobed(p_spi.miso);
    set_port_slave(p_spi.mosi);
    set_port_slave(p_spi.miso);
    start_clock(p_spi.blk);
    clearbuf(p_spi.miso);
    clearbuf(p_spi.mosi);
}

void spi_slave_shutdown(spi_slave_pins &p_spi)
{
    stop_clock(p_spi.blk);
    
    set_clock_off(p_spi.blk);
    set_port_use_off(p_spi.ss);
    set_port_use_off(p_spi.mosi);
    set_port_use_off(p_spi.miso);
    set_port_use_off(p_spi.sclk);
}

void spi_slave(spi_slave_pins &p_spi, server interface spi_slave_if i_app)
{
    int ss_val, buff_index = BUFFER_LENGTH; //port temp value & buffer index. Initialise to BUFFER_INDEX for first loop
    int in_data_rev, out_data_rev;          //temp values for bit reversed SPI tx/rx words
    spi_slave_state spi_state = SPI_IDLE;   //State variable and inital state

    //Array of buffers for tx and rx. This declares the storage
    unsigned char spi_tx_data[2][BUFFER_LENGTH] = {{12, 34}, {56, 78}};    //Tx buffers with initial values
    unsigned char spi_rx_data[2][BUFFER_LENGTH];                           //Rx buffers

    unsigned spi_buf_inuse = 0;             //Which of the double buffers is being used by SPI. Either 0 or 1.
    unsigned data_transferred = 1;          //Indicates when client has made a transfer to SPI slave server
    unsigned missed_transfer = 0;           //Error flag showing client missed a SPI transaction

    unsigned char * movable tx_ptr[2] = {spi_tx_data[0], spi_tx_data[1]};
    unsigned char * movable rx_ptr[2] = {spi_rx_data[0], spi_rx_data[1]};

    spi_slave_init(p_spi);
    p_spi.ss :> ss_val;                      //Get initial value of port which includes SPI SS (slave select)

    while(1){
        select{
            //Wait for select line to change
            case p_spi.ss when pinsneq(ss_val) :> ss_val:
                //Check to see if the change to the port means SPI_SS is high or low (selected)
                if (ss_val & SS_BITMASK) {//SS is high - de-selected
                    if (spi_state == SPI_SELECTED); //printstrln("SS cycle without SPI transfer");
                    if ((spi_state == SPI_TRANSFER) && (buff_index < BUFFER_LENGTH)){ //incomplete transfer
                        printstr("Incomplete data transfer. Expected ");
                        printint(BUFFER_LENGTH);
                        printstr(" bytes, got just ");
                        printintln(buff_index);
                    }
                    spi_state = SPI_IDLE; //Return to idle if SS is high (de-asserted)
//                    printstrln("SS gone high");
                }

                else{ //SS is low, active
                    if (spi_state == SPI_IDLE){     //check to see if start of SPI cycle. If so..
                        clearbuf(p_spi.miso);       //clear port buffers in case of previous partial transfer
                        clearbuf(p_spi.mosi);
                        buff_index = 0;             //start the buffer at zero
                        out_data_rev = bitrev(tx_ptr[spi_buf_inuse][buff_index]) >> 24; //Calculate first byte to send for next state
                        p_spi.miso <: out_data_rev; //Put first word into Tx port buffer before first SPI clock edge
                        spi_state = SPI_SELECTED;   //change to next state
//                        printstrln("SS gone low");
                    }
                }
            break;

            //If SCLK goes low following SS, then it's definitely the start of SPI transaction
            case (spi_state == SPI_SELECTED) => p_spi.sclk when pinseq(0) :> void:
                if (!data_transferred) missed_transfer = 1;//Flag that client missed a SPI transfer
                data_transferred = 0;           //Start of new data transfer, so client not up to date anymore
                spi_state = SPI_TRANSFER;       //Change state. Ready for Tx/Rx
//                printstrln("SCLK gone low");
            break;

            //Wait on RX buffer if we're in the transfer state
            case (spi_state == SPI_TRANSFER) => p_spi.mosi :> >> in_data_rev:   //notice extra >> which rotates byte to MSB
                if (buff_index < (BUFFER_LENGTH - 1)){
                    out_data_rev = bitrev(tx_ptr[spi_buf_inuse][buff_index + 1]) >> 24;   //Calculate next tx byte to send
                    p_spi.miso <: out_data_rev;                                 //Load it into the port buffer
                }
                rx_ptr[spi_buf_inuse][buff_index] = (unsigned char) bitrev(in_data_rev);  //pack received byte into rx array
                buff_index++;                       //Set index for next byte in current buffer
                if (buff_index == BUFFER_LENGTH){   //Finished tx/rx of buffer. Exit into IDLE
                    spi_state = SPI_IDLE;           //Ensure we're idle if SS is high (de-asserted)
//                    printstrln("Buffer tx/rx complete");
                    spi_buf_inuse = spi_buf_inuse ? 0 : 1; //Swap buffers by toggling index
                    i_app.transfer_notify();        //Tell client that a SPI transfer has happened
                 }
            break;

            case i_app.get_buffs (void) -> {int missed, unsigned char * movable rd_ptr, unsigned char * movable wr_ptr}:
                rd_ptr = move(rx_ptr[1 - spi_buf_inuse]);   //Pass pointers to buffers to client
                wr_ptr = move(tx_ptr[1 - spi_buf_inuse]);
                missed = missed_transfer;                   //Pass flag showing if data was missed
            break;

            case i_app.return_buffs (unsigned char * movable rd_ptr, unsigned char * movable wr_ptr):
                rx_ptr[1 - spi_buf_inuse] = move(rd_ptr);   //Get pointers back from client
                tx_ptr[1 - spi_buf_inuse] = move(wr_ptr);
                data_transferred = 1;                       //Record that the buffers are now valid
                missed_transfer = 0;                        //Reset flag now buffers up to date
            break;                                          //This function also clears the notfication to the client

        }
    }
}

