def lerp(point1, point2, x): # a helper
    x1, x2 = point1
    y1, y2 = point2
    return ((y2 - y1) / (x2 - x1)) * (x - x1) + y1

def clamper(value, minimum, maximum):
    if value < minimum:
        return minimum
    elif value > maximum:
        return maximum
    else:
        return value

def within(value, minimum, maximum):
    if value > minimum and value < maximum:
        return True
    return False

class SmoothDamp:
    def __init__(self, initial_velocity=0.0):  ## current velocity is encapsulated
        self.current_velocity = initial_velocity
    def smooth_damp(self, current, target, smooth_time, max_speed, delta_time): ## speed of 1, 1000000 is good for testing
        ## god damn this took me ages to debug. This algorithm was converted from C# in Unity I think
        smooth_time = max(0.0001, smooth_time)
        num = 2.0 / smooth_time
        num2 = num * delta_time
        num3 = 1.0 / (1.0 + num2 + 0.48 * num2 * num2 + 0.235 * num2 * num2 * num2)
        num4 = current - target
        num5 = target
        num6 = max_speed * smooth_time
        num4 = max(min(num4, num6), -num6)
        target = current - num4
        num7 = (self.current_velocity + num * num4) * delta_time
        self.current_velocity = (self.current_velocity - num * num7) * num3
        num8 = target + (num4 + num7) * num3

        if (num5 - current > 0.0) == (num8 > num5):
            num8 = num5
            self.current_velocity = (num8 - num5) / delta_time

        return num8
