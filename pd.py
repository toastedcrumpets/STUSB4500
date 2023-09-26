##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2012-2020 Uwe Hermann <uwe@hermann-uwe.de>
## Copyright (C) 2013 Matt Ranostay <mranostay@gmail.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import re
import sigrokdecode as srd
from common.srdhelper import bcd2int, SrdIntEnum

REGs = {
 0x06: ('BCD_TYPEC_REV_LOW', None),
 0x07: ('BCD_TYPEC_REV_HIGH', None),
 0x08: ('BCD_USBPD_REV_LOW', None),
 0x09: ('BCD_USBPD_REV_HIGH', None),
 0x0A: ('DEVICE_CAPAB_HIGH', None),
 0x0B: ('ALERT_STATUS_1', None),
 0x0C: ('ALERT_STATUS_1_MASK', None),
 0x0D: ('PORT_STATUS_0', None),
 0x0E: ('PORT_STATUS_1', None),
 0x0F: ('TYPEC_MONITORING_STATUS_0', None),
 0x10: ('TYPEC_MONITORING_STATUS_1', None),
 0x11: ('CC_STATUS', None),
 0x12: ('CC_HW_FAULT_STATUS_0', None),
 0x13: ('CC_HW_FAULT_STATUS_1', None),
 0x14: ('PD_TYPEC_STATUS', None),
 0x15: ('TYPEC_STATUS', None),
 0x16: ('PRT_STATUS', None),
 0x1A: ('PD_COMMAND_CTRL', None),
 0x20: ('MONITORING_CTRL_0', None),
 0x22: ('MONITORING_CTRL_2', None),
 0x23: ('RESET_CTRL', None),
 0x25: ('VBUS_DISCHARGE_TIME_CTRL', None),
 0x26: ('VBUS_DISCHARGE_CTRL', None),
 0x27: ('VBUS_CTRL', None),
 0x29: ('PE_FSM', None),
 0x2D: ('GPIO_SW_GPIO', None),
 0x2F: ('Device_ID', None),
 0x31: ('RX_HEADER_LOW', None),
 0x32: ('RX_HEADER_HIGH', None),
 0x33: ('RX_DATA_OBJ1_0', None),
 0x34: ('RX_DATA_OBJ1_1', None),
 0x35: ('RX_DATA_OBJ1_2', None),
 0x36: ('RX_DATA_OBJ1_3', None),
 0x37: ('RX_DATA_OBJ2_0', None),
 0x38: ('RX_DATA_OBJ2_1', None),
 0x39: ('RX_DATA_OBJ2_2', None),
 0x3A: ('RX_DATA_OBJ2_3', None),
 0x3B: ('RX_DATA_OBJ3_0', None),
 0x3C: ('RX_DATA_OBJ3_1', None),
 0x3D: ('RX_DATA_OBJ3_2', None),
 0x3E: ('RX_DATA_OBJ3_3', None),
 0x3F: ('RX_DATA_OBJ4_0', None),
 0x40: ('RX_DATA_OBJ4_1', None),
 0x41: ('RX_DATA_OBJ4_2', None),
 0x42: ('RX_DATA_OBJ4_3', None),
 0x43: ('RX_DATA_OBJ5_0', None),
 0x44: ('RX_DATA_OBJ5_1', None),
 0x45: ('RX_DATA_OBJ5_2', None),
 0x46: ('RX_DATA_OBJ5_3', None),
 0x47: ('RX_DATA_OBJ6_0', None),
 0x48: ('RX_DATA_OBJ6_1', None),
 0x49: ('RX_DATA_OBJ6_2', None),
 0x4A: ('RX_DATA_OBJ6_3', None),
 0x4B: ('RX_DATA_OBJ7_0', None),
 0x4C: ('RX_DATA_OBJ7_1', None),
 0x4D: ('RX_DATA_OBJ7_2', None),
 0x4E: ('RX_DATA_OBJ7_3', None),
 0x51: ('TX_HEADER_LOW', None),
 0x52: ('TX_HEADER_HIGH', None),
 0x70: ('DPM_PDO_NUMB', None),
 0x85: ('DPM_SNK_PDO1_0', None),
 0x86: ('DPM_SNK_PDO1_1', None),
 0x87: ('DPM_SNK_PDO1_2', None),
 0x88: ('DPM_SNK_PDO1_3', None),
 0x89: ('DPM_SNK_PDO2_0', None),
 0x8A: ('DPM_SNK_PDO2_1', None),
 0x8B: ('DPM_SNK_PDO2_2', None),
 0x8C: ('DPM_SNK_PDO2_3', None),
 0x8D: ('DPM_SNK_PDO3_0', None),
 0x8E: ('DPM_SNK_PDO3_1', None),
 0x8F: ('DPM_SNK_PDO3_2', None),
 0x90: ('DPM_SNK_PDO3_3', None),
 0x91: ('RDO_REG_STATUS_0', None),
 0x92: ('RDO_REG_STATUS_1', None),
 0x93: ('RDO_REG_STATUS_2', None),
 0x94: ('RDO_REG_STATUS_3', None),
}

class Decoder(srd.Decoder):
    api_version = 3
    id = 'stusb4500'
    name = 'STUSB4500'
    longname = 'ST USB4500 USBPD Controller'
    desc = 'The ST4500USB USB Power Delivery controller'
    license = 'gplv2+'
    inputs = ['i2c']
    outputs = []
    tags = ['IC']
    annotations =  (
        ('address', 'Address'),
        ('register', 'Register'),
        ('warning', 'Warning'),
        ('errors', 'Error'),
    )
    annotation_rows = (
        ('addresses', 'Addresses', (0,)),
        ('registers', 'Registers', (1,)),
        ('warnings', 'Warnings', (2,)),
        ('errors', 'Errors', (3,))
    )

    ANN_ADDRESS = 0
    ANN_REGISTER = 1
    ANN_WARNING = 2
    ANN_ERROR = 3

    options = (
        {'id': 'address', 'desc': 'I2C Address', 'default': '0x28', 'values': ('0x28', '0x29', '0x2A', '0x2B')},
    )

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 'IDLE'
        self.reg = None
        self.write = None
        self.bits = []

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.address = {'0x28':0x28, '0x29':0x29, '0x2A':0x2A, '0x2B':0x2B}[self.options['address']]

    def putx(self, data):
        self.put(self.ss, self.es, self.out_ann, data)

    def putd(self, bit1, bit2, data):
        self.put(self.bits[bit1][1], self.bits[bit2][2], self.out_ann, data)
    
    #def putr(self, bit):
    #    self.put(self.bits[bit][1], self.bits[bit][2], self.out_ann,
    #             [Ann.BIT_RESERVED, ['Reserved bit', 'Reserved', 'Rsvd', 'R']])

    def handle_write_reg(self, b):
        if self.reg in REGs:
            name = REGs[self.reg][0]
            self.putx([self.ANN_REGISTER, ['Write '+name, name]])
        else:
            self.putx([self.ANN_REGISTER, ['Write Unknown reg %02X'%self.reg, "Unknown"]])
        #fn = getattr(self, 'handle_reg_0x%02x' % r)
        #fn(b)
        self.reg += 1

    def handle_read_reg(self, b):
        if self.reg in REGs:
            name = REGs[self.reg][0]
            self.putx([self.ANN_REGISTER, ['Read '+name, name]])
        else:
            self.putx([self.ANN_REGISTER, ['Read Unknown reg %02X'%self.reg, "Unknown"]])
        #fn = getattr(self, 'handle_reg_0x%02x' % r)
        #fn(b)
        self.reg += 1

    def handle_ACK(self):
        if self.needACK == True:
            #self.putx([self.ANN_ERROR, ['ACK Handled']])
            self.needACK = False
            return True
        else:
            self.putx([self.ANN_ERROR, ['Unxpected ACK']])
            return False

    def is_correct_chip(self, addr):
        addr = addr >> 1
        if addr == self.address:
            self.put(self.ss_block, self.es, self.out_ann, [self.ANN_ADDRESS, ['Address (slave 0x%02X)' % addr]])
            return True
        else:
            self.put(self.ss_block, self.es, self.out_ann, [self.ANN_ADDRESS, ['Ignoring wrong addr (slave 0x%02X)' % addr]])
            return False

    def setReg(self, reg):
        self.reg = reg
        if self.reg in REGs:
            name = REGs[self.reg][0]
            self.putx([self.ANN_REGISTER, ["Register "+name, name]])
        else:
            self.putx([self.ANN_REGISTER, ["Unknown Register %02X"%self.reg]])

    def decode(self, ss, es, data):
        cmd, databyte = data

        # Collect the 'BITS' packet, then return. The next packet is
        # guaranteed to belong to these bits we just stored.
        if cmd == 'BITS':
            self.bits = databyte
            return

        # Store the start/end samples of this IÂ²C packet.
        self.ss, self.es = ss, es

        # State machine.
        if self.state == 'IDLE':
            # Wait for an I²C START condition.
            if cmd != 'START':
                return
            # Now wait to confirm what the slave address is
            self.state = 'GET SLAVE ADDR'
            self.ss_block = ss
        elif self.state == 'GET SLAVE ADDR':
            # Here we verify the correct I2C address is being targetted
            if (cmd != 'ADDRESS WRITE') and (cmd != 'ADDRESS READ'):
                #Some error here, restart back to the idle state
                self.putx([self.ANN_ERROR, ['Expected READ/WRITE']])
                self.state = 'IDLE'
                return
            
            if not self.is_correct_chip(databyte):
                #This is not the correct I2C address, so reset the state machine
                self.state = 'IDLE'
                return

            self.needACK = True
            if cmd == 'ADDRESS WRITE':
                #Now if we're writing, then this first byte is the address
                self.state = 'GET REG ADDR'
            else:
                #If we're reading, then we're loading reg data
                self.state = 'READ REGS'
        elif self.state == 'GET REG ADDR':
            # Wait for a data write (master selects the slave register).
            if cmd == "ACK":
                if self.handle_ACK():
                    return
                else:
                    self.state = "IDLE"
                    return

            if cmd != 'DATA WRITE':
                self.putx([self.ANN_ERROR, ['Expected DATA WRITE (got '+cmd+')', 'ERR']])
                self.state = 'IDLE'
                return
            #The data byte is the register we're now addressing
            self.setReg(databyte)
            self.state = 'WRITE REGS'
            self.needACK = True
        elif self.state == 'WRITE REGS':
            if cmd == "ACK":
                if self.handle_ACK():
                    return
                else:
                    self.state = "IDLE"
                    return

            if cmd == 'DATA WRITE':
                self.handle_write_reg(databyte)
                self.needACK = True
            elif cmd == 'STOP':
                self.state = 'IDLE'
            else:
                self.putx([self.ANN_ERROR, ['Expected DATA WRITE or STOP', 'ERR']])
        elif self.state == 'READ REGS':
            if cmd == "ACK":
                if self.handle_ACK():
                    return
                else:
                    self.state = "IDLE"
                    return
            
            if cmd == 'NACK':
                self.state = 'IDLE'
                self.needACK = False
            elif cmd == 'DATA READ':
                self.handle_read_reg(databyte)
                self.needACK = True
            elif cmd == 'STOP':
                self.state = 'IDLE'
            else:
                self.putx([self.ANN_ERROR, ['Expected DATA READ or STOP', 'ERR']])
