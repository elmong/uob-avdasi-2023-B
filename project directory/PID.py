class Pid_controller:
    def __init__(self, Kp, Ki, Kd, Limits):
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.Limits = Limits

        self.prev_pv = 0
        self.integrator = 0
        self.output = 0

    def update(self, SP, PV, dT):
        rate  = (PV - self.prev_pv) / dT
        self.prev_pv = PV
        error = (SP - PV)

        print(error, self.output, self.Limits[0], self.Limits[1])

        saturated_up = (self.output <= self.Limits[0] and error < 0)
        saturated_dn = (self.output >= self.Limits[1] and error > 0)

        if not saturated_up and not saturated_dn:
            self.integrator += error * self.Ki

        self.output = error * self.Kp
        self.output += self.integrator
        self.output += rate * self.Kd
    
        self.output = max(self.Limits[0], min(self.Limits[1],self.output))
        return self.output