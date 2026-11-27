from machine import Pin
from array import array
import rp2
from rp2 import PIO

SENSOR_COUNT = const(6)
TIMEOUT = const(1024)

class QTRRCSensors:
    """A multi-channel QTR sensor reader using PIO"""

    def __init__(self, index=5, pin1=14):
        for i in range(SENSOR_COUNT):
            Pin(pin1+i, Pin.IN, pull=None)

        p = Pin(pin1, Pin.OUT, value=1)
        for i in range(1, SENSOR_COUNT):
            Pin(pin1+i, Pin.OUT, value=1)

        self.sm = rp2.StateMachine(index, self.counter, freq=8000000, in_base=p, out_base=p)
        self.data_line = array('H', [0] * SENSOR_COUNT)

        # Compile and save away PIO instructions that initialize registers in
        # the state machine so that we don't need to waste precious PIO code
        # space.
        self.pio_instrs = array('H')
        # Set OSR to 32 bits of 1s for future shifting out to initialize pindirs and y.
        self.pio_instrs.append(rp2.asm_pio_encode("mov(osr, invert(null))", 0))
        # Set Y counter to 255 by pulling 8 high bits from OSR. At 8MHz this results in ~32us of charge time.
        self.pio_instrs.append(rp2.asm_pio_encode("out(y, 8)", 0))
        # Initialize X (last pin state) to 6 bits of 1s.
        self.pio_instrs.append(rp2.asm_pio_encode("out(x, 6)", 0))

    @rp2.asm_pio(
        out_init=(PIO.OUT_HIGH,) * SENSOR_COUNT,
        autopush=True, # saves push instructions
        push_thresh=SENSOR_COUNT + 16,
        fifo_join=PIO.JOIN_RX
        )
    def counter():
        # The CPU initializes a few of the registers before this PIO program is restarted.
        #   OSR = 32 bits of 1s for future shifting out to initialize pindirs and Y.
        #         This requires SENSOR_COUNT + 10 bits.
        #   Y = 255 this will result in the loop at 'change' below delaying for ~32usec.
        #   X = 6 bits of 1s as the last pin state.

        # OSR already contains 32 bits of 1s put there by the CPU before restarting the state machine.
        # Set pindirs to 6 bits of 1s to enable output and start charging the capacitor.
        out(pindirs, SENSOR_COUNT) # type: ignore

        # Charge up the capacitors for ~32us.
        # Y was initialized already by the CPU before restarting the state machine.
        label("charge") # type: ignore
        jmp(y_dec, "charge") # type: ignore

        # Use bits still in OSR from previous CPU initialization.
        # Load 1023 (10 bits of 1s) into Y as a counter
        out(y, 10) # type: ignore

        # Set pins back to inputs by writing 0s to pindirs.
        mov(osr, null) # type: ignore
        out(pindirs, SENSOR_COUNT) # type: ignore

        # loop is 8 instructions long = 1us
        label("loop") # type: ignore

        # read pins into ISR
        in_(pins, SENSOR_COUNT) # type: ignore

        # save y in OSR
        mov(osr, y) # type: ignore

        # compare x to ISR
        mov(y, isr) # new value -> y # type: ignore
        jmp(x_not_y, "change") # type: ignore

        # discard the pin values and reset shift counter
        mov(isr, null) # type: ignore
        jmp("decrement") # type: ignore

        # a pin changed!
        label("change") # type: ignore
        mov(x, y) # save new pins # type: ignore

        # save and write data
        # 6 pins are in low bits of ISR
        in_(osr, 16) # time # type: ignore

        label("decrement") # type: ignore
        mov(y, osr) # restore y # type: ignore
        jmp(y_dec, "loop") # type: ignore

        # END OF PROGRAM
        label("finish") # type: ignore

        # Send 0xFFFFFFFF to tell the CPU we are done.
        in_(y, 32) # type: ignore

        wrap_target() # type: ignore
        nop() # type: ignore
        wrap() # type: ignore

    def run(self):
        self.sm.active(0)
        while self.sm.rx_fifo():
            self.sm.get()
        self.sm.restart()
        for instr in self.pio_instrs:
            self.sm.exec(instr)
        self.sm.active(1)

    @micropython.viper  # type: ignore
    def read(self):
        self.run()

        last_states = uint(0x3f0000)  # type: ignore
        data = ptr16(self.data_line)  # type: ignore
        for i in range(6):
            data[i] = 0

        sm = self.sm
        while True:  # TODO: TIMEOUT?
            val = uint(sm.get())  # type: ignore
            if(val == uint(0xffffffff)):  # type: ignore
                break
            new_zeros = last_states ^ val
            if new_zeros & 0x200000:
                data[1] = val
            if new_zeros & 0x100000:
                data[0] = val
            if new_zeros & 0x80000:
                data[2] = val
            if new_zeros & 0x40000:
                data[3] = val
            if new_zeros & 0x20000:
                data[4] = val
            if new_zeros & 0x10000:
                data[5] = val
            last_states = val
        return self.data_line
