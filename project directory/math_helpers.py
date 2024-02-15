import time

def lerp(point1, point2, x): # a helper
    x1, x2 = point1
    y1, y2 = point2
    return ((y2 - y1) / (x2 - x1)) * (x - x1) + y1

def remap(old_min, old_max, new_min, new_max, old_val):
    return (new_max - new_min)*(old_val - old_min) / (old_max - old_min) + new_min

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

def ratio_to_pwm(ratio):
    return clamper(1500 + ratio * 500, 1000, 2000)

class SmoothDamp:
    def __init__(self, initial_velocity=0.0):  ## current velocity is encapsulated
        self.current_velocity = initial_velocity
        self.current_val = 0
    def smooth_damp(self, target, smooth_time, max_speed, delta_time): ## speed of 1, 1000000 is good for testing
        ## god damn this took me ages to debug. This algorithm was converted from C# in Unity I think
        smooth_time = max(0.0001, smooth_time)
        num = 2.0 / smooth_time
        num2 = num * delta_time
        num3 = 1.0 / (1.0 + num2 + 0.48 * num2 * num2 + 0.235 * num2 * num2 * num2)
        num4 = self.current_val - target
        num5 = target
        num6 = max_speed * smooth_time
        num4 = max(min(num4, num6), -num6)
        target = self.current_val - num4
        num7 = (self.current_velocity + num * num4) * delta_time
        self.current_velocity = (self.current_velocity - num * num7) * num3
        num8 = target + (num4 + num7) * num3

        if (num5 - self.current_val > 0.0) == (num8 > num5):
            num8 = num5
            self.current_velocity = (num8 - num5) / delta_time

        self.current_val = num8
        return num8

class Interpolator:
    # Use it like this:
    # foo_interpolator = Interpolator([(0, 10), (1, 20), (2, 40), (3, 40)])
    # to retrieve:
    # y = foo_interpolator.value(x)

    def __init__(self, points):
        # Sort points based on x values
        self.points = sorted(points, key=lambda point: point[0])
        self.min_x = self.points[0][0]
        self.max_x = self.points[-1][0]

    def value(self, x):
        if x <= self.min_x:
            return self.points[0][1]
        elif x >= self.max_x:
            return self.points[-1][1]
        else:
            # Find the two closest points for interpolation
            for i in range(len(self.points) - 1):
                if self.points[i][0] <= x <= self.points[i + 1][0]:
                    x1, y1 = self.points[i]
                    x2, y2 = self.points[i + 1]
                    # Linear interpolation formula
                    return y1 + (y2 - y1) * (x - x1) / (x2 - x1)

class MovingAverage:
    def __init__(self, window_size):
        self.window_size = window_size
        self.values = []

    def update(self, new_value):
        self.values.append(new_value)

        # Remove the oldest value if the window size is exceeded
        if len(self.values) > self.window_size:
            self.values.pop(0)

    def get_value(self):
        if not self.values:
            return None  # Return None if no values in the filter

        return sum(self.values) / len(self.values)

class Timer:
    def __init__(self):
        self.last_time = time.time()
        self.DELTA_TIME = 0.000001
        self.DELTA_TIME_SMOOTH = 0.000001
        self.refresh_rate = 0
        self.filter = MovingAverage(15)

    def update(self):
        current_time = time.time()
        self.DELTA_TIME = max(current_time - self.last_time, 0.000001)
        self.refresh_rate = 1 / self.DELTA_TIME if self.DELTA_TIME > 0 else 0
        self.last_time = current_time

        self.filter.update(self.DELTA_TIME)
        self.DELTA_TIME_SMOOTH = self.filter.get_value()

    def get_refresh_rate(self):
        return self.refresh_rate

class Stopwatch:
    def __init__(self):
        self.start_time = 0
    def get_time(self):
        return time.time() - self.start_time
    def start(self):
        self.start_time = time.time()

    def reset(self):
        self.start_time = 0
