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

def within(val, minimum, maximum):
    if value > minimum and value < maximum:
        return True
    return False