/*
 * raspberry-spi.xc
 *
 *  Created on: Dec 16, 2013
 *      Author: Ed
 */

#include <platform.h>
#include <xscope.h>
#include <print.h>
#include <xclib.h>
#include "rpi-spi.h"

#define XSCOPE //Use xSCOPE fast printing (will need to enable this in run configuration or xrun command line

//Declare SPI resources (pins and clock block) as per startKIT
spi_slave_pins spi_ssif = {
    on tile[0]: XS1_PORT_32A,   //RPI_SS   - XD51, P32A bit 2
    on tile[0]: XS1_PORT_1A,    //MOSI     - XD00, P1A
    on tile[0]: XS1_PORT_1D,    //MISO     - XD11, P1D
    on tile[0]: XS1_PORT_1C,    //SCLK     - XD10, P1C
    on tile[0]: XS1_PORT_1B,    //FLASH_SS - XD01, P1B
    on tile[0]: XS1_CLKBLK_3    //Any free clock block.
};

#ifdef XSCOPE
void xscope_user_init(void) {
    xscope_register(0, 0, "", 0, "");   //No xSCOPE probes
    xscope_config_io(XSCOPE_IO_BASIC);  //Enable xSCOPE fast printing
}
#endif

//Print routine to display buffer.
void print_buff(unsigned char *buff){
    for (int i = 0; i < BUFFER_LENGTH; i++){
        if (buff[i] <= 0xF) printstr("0");
        printhex(buff[i]);
        printstr(" ");
        if (!((1 + i) % 16)) printstr("\n");
    }
    printstr("\n");
}

void app(client interface spi_slave_if i_rpi_spi){

    int notification = 0;               //Flag to show SPI transfer notfication
    int missed;                         //Flag to indicate SPI transfer missed by this client
    unsigned char data = 0;             //Data to transmit
    unsigned char spi_mosi_data[BUFFER_LENGTH]; //Local mosi buffer copy
    unsigned char spi_miso_data[BUFFER_LENGTH]; //Local miso buffer copy
    unsigned char * movable mosi_buf;   //Master out slave in - data from RPI
    unsigned char * movable miso_buf;   //Master in slave out - data to RPI
    unsigned char * movable tmp;        //Temp ptr for pointer move operations

    while(1)
        select{
        case i_rpi_spi.transfer_notify():  //Case fires when SPI transfer occured
            notification = 1;              //Set flag and "get out"
//            printstrln("Notified of incoming data!");
            {missed, mosi_buf, miso_buf} = i_rpi_spi.get_buffs();   //Get buffer pointers from SPI slave
            if (missed) printstrln("Missed a SPI transfer");        //Report if overrun occurred
            for(int i = 0; i < BUFFER_LENGTH; i++){                 //Make local copy of received data
                spi_mosi_data[i] = mosi_buf[i];
                miso_buf[i] = spi_miso_data[i];                     //Make copy of local tx data
            }
            i_rpi_spi.return_buffs(move(mosi_buf), move(miso_buf)); //Release pointers back to SPI task
        break;

        default:
            if (notification){
                for(int i = 0; i < BUFFER_LENGTH; i++) spi_miso_data[i] = data;//Write data back to SPI slave tx
                data++;

                printstr("Received - ");                            //Show what we got
                print_buff(spi_mosi_data);
                mosi_buf = move(tmp);

                printstr("Sent - ");                                //Show what we sent
                print_buff(spi_miso_data);
                notification = 0;
            }
            break;
    }
}


int main(void){
    interface spi_slave_if i_spi_slave;
    par{
        on tile[0]: {
            printstrln ("Welcome to the raspberry SPI startKIT demo");
            spi_slave(spi_ssif, i_spi_slave); //RPI slave server never returns
        }
        on tile[0]: app(i_spi_slave);         //The app/client which gets data from SPI slave server
    }
    return 0;
}
