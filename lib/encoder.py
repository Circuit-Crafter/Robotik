# Modified from https://forum.micropython.org/viewtopic.php?t=12277&p=66659

import machine
import rp2

class Encoder:
    _counts_per_motor_shaft_revolution = 12
    
    def __init__(self, index, encAPin: int|str, encBPin: int|str, gear_ratio: int = 210, flip_dir:bool=False):
        """
        Uses the on board PIO State Machine to keep track of encoder positions. 
        Only 4 encoders can be instantiated this way.
        
        :param index: The index of the state machine to be used, indexed 0-3.
        :type index: int
        :param encAPin: The pin the left reflectance sensor is connected to
        :type encAPin: int
        :param encBPin: The pin the right reflectance sensor is connected to
        :type encBPin: int
        """
        # if(abs(encAPin - encBPin) != 1):
        #     raise Exception("Encoder pins must be successive!")
        basePin = machine.Pin(min(encAPin, encBPin), machine.Pin.IN)
        nextPin = machine.Pin(max(encAPin, encBPin), machine.Pin.IN)
        self.resolution = self._counts_per_motor_shaft_revolution * gear_ratio
        self.flip_dir = flip_dir
        self.sm = rp2.StateMachine(index, self._encoder, in_base=basePin)
        self.reset_encoder_position()
        self.sm.active(1)
    
    def reset_encoder_position(self):
        """
        Resets the encoder position to 0
        """
        # It's possible for this to cause issues if in the middle of inrementing
        # or decrementing, but the result should only be off by 1. If that's a
        # problem, an alternative solution is to stop the state machine, then
        # reset both x and the program counter. But that's excessive.
        self.sm.exec("set(x, 0)")
    
    def get_position_counts(self):
        """
        :return: The position of the encoded motor, in counts, relative to the last time reset was called.
        :rtype: int
        """
        # Read 5 times for it to get past the buffer
        counts = self.sm.get()
        counts = self.sm.get()
        counts = self.sm.get()
        counts = self.sm.get()
        counts = self.sm.get()
        if(counts > 2**31):
            counts -= 2**32
        return counts
    
    def get_position(self):
        """
        :return: The position of the encoded motor, in revolutions, relative to the last time reset was called.
        :rtype: float
        """
        if self.flip_dir:
            invert = -1
        else:
            invert = 1
        return self.get_position_counts() / self.resolution *invert

    @rp2.asm_pio(in_shiftdir=rp2.PIO.SHIFT_LEFT, out_shiftdir=rp2.PIO.SHIFT_RIGHT)
    def _encoder():
        # Register descriptions:
        # X - Encoder count, as a 32-bit number
        # OSR - Previous pin values, only last 2 bits are used
        # ISR - Push encoder count, and combine pin states together
        
        # Jump table
        # The program counter is moved to memory address 0000 - 1111, based
        # on the previous (left 2 bits) and current (right  bits) pin states
        jmp("read") # 00 -> 00 No change, continue # type: ignore
        jmp("decr") # 00 -> 01 Reverse, decrement count # type: ignore
        jmp("incr") # 00 -> 10 Forward, increment count # type: ignore
        jmp("read") # 00 -> 11 Impossible, continue # type: ignore
        
        jmp("incr") # 01 -> 00 Forward, increment count # type: ignore
        jmp("read") # 01 -> 01 No change, continue # type: ignore
        jmp("read") # 01 -> 10 Impossible, continue # type: ignore
        jmp("decr") # 01 -> 11 Reverse, decrement count # type: ignore
        
        jmp("decr") # 10 -> 00 Reverse, decrement count # type: ignore
        jmp("read") # 10 -> 01 Impossible, continue # type: ignore
        jmp("read") # 10 -> 10 No change, continue # type: ignore
        jmp("incr") # 10 -> 11 Forward, increment count # type: ignore
        
        jmp("read") # 11 -> 00 Impossible, continue # type: ignore
        jmp("incr") # 11 -> 01 Forward, increment count # type: ignore
        jmp("decr") # 11 -> 10 Reverse, decrement count # type: ignore
        jmp("read") # 11 -> 11 No change, continue # type: ignore
        
        label("read") # type: ignore
        mov(osr, isr)   # Store previous pin states in OSR # type: ignore
        mov(isr, x)     # Copy encoder count to ISR # type: ignore
        push(noblock)   # Push count to RX buffer, and reset ISR to 0 # type: ignore
        out(isr, 2)     # Shift previous pin states into ISR # type: ignore
        in_(pins, 2)    # Shift current pin states into ISR # type: ignore
        mov(pc, isr)    # Move PC to jump table to determine what to do next # type: ignore
        
        label("decr")           # There is no explicite increment intruction, but X can be # type: ignore
        jmp(x_dec, "decr_nop")  # decremented in the jump instruction. So we use that and jump # type: ignore
        label("decr_nop")       # to the next instruction, which is equivalent to just decrementing # type: ignore
        jmp("read") # type: ignore
        
        label("incr")           # There is no explicite increment intruction, but X can be # type: ignore
        mov(x, invert(x))       # decremented in the jump instruction. So we invert X, decrement,  # type: ignore
        jmp(x_dec, "incr_nop")  # then invert again - this is equivalent to incrementing. # type: ignore
        label("incr_nop") # type: ignore
        mov(x, invert(x)) # type: ignore
        jmp("read") # type: ignore
        
        # Fill remaining instruction memory with jumps to ensure nothing bad happens
        # For some reason, weird behavior happens if the instruction memory isn't full
        jmp("read") # type: ignore
        jmp("read") # type: ignore
        jmp("read") # type: ignore
        jmp("read") # type: ignore
