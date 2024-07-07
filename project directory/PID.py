from math_helpers import *

class Pid_controller:
    def __init__(self, Limits, Window):
        self.Limits = Limits

        self.prev_pv = 0
        self.integrator = 0
        self.output = 0
        self.output_unclamped = 0

        self.derivative_filter = MovingAverage(Window)

    def update(self, SP, PV, dT, Kp, Ki, Kd, **kwargs):
        rate = 0

        rate  = (PV - self.prev_pv) / dT
        self.derivative_filter.update(rate)

        self.prev_pv = PV
        error = (SP - PV)

        saturated_up = (self.output <= self.Limits[0] and error < 0)
        saturated_dn = (self.output >= self.Limits[1] and error > 0)

        if not saturated_up and not saturated_dn:
            self.integrator += error * Ki
            
        self.output = error * Kp
        self.output += self.integrator
        self.output -= self.derivative_filter.get_value() * Kd
        
        self.output_unclamped = self.output
        self.output = max(self.Limits[0], min(self.Limits[1],self.output))
        return self.output, self.output_unclamped

    def reset_integrator(self):
        self.integrator = 0