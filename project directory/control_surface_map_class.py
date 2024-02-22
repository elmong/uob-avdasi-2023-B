from global_var import *

class Control_Surface:
    
    #object instantiation
    def __init__(self,Name,Rate_adc_angle_table):
        #assign object attributes
        self.table = Rate_adc_angle_table 
        #[0] is Rate values, [1] is ADC reading, [2] is output angle, Rate_adc_angle_table is a list with three entries, [Rate,ADC,Angle]
        self.name = Name
        self.adc_now = None
        
    def __str__(self): #returns object as a string
        return str(str(self.name) + "\n"+ str(self.table))

    #linear interpolation function
    def linear_interpolation(self,x,x1,x2,y1,y2):
        return y1 + ((x-x1)*(y2-y1)/(x2-x1))
    
    def find_closest_value(self,list,number):
        #ai generated code, done by Bing of all things (slightly modified to match our needs)
        aux = []
        
        for value in list:
            aux.append(abs(number - value))
        
        return list[aux.index(min(aux))]
        #checks out


    #for a given adc value, find the closest rate value to the current rate output
    def rate_adc_to_angle(self,rate_now,adc_now):
        #rate is a range of values which map to the pwm and the angle that the servo is allowed to use, rate goes from -1 to +1

        #obtain rates that are closest to adc
        adc_indexes = [[],[]] #store high and low index [[high],[low]]
        possible_rates = []#stores all possible rates from given adc obtained

        if self.table[1].index(adc_now) != None: #assuming individual adc values do not exactly repeat
        #if somehow adc lands on a stored value, return angle directly by index
            rate = self.table[0][self.table[1].index(adc_now)]
            return self.table[2][self.table[0].index(rate)]

        else:
            #find all adc values' indexes in table close to adc_now
            smaller = False #logic variables
            larger = False
            
            #go through adc values in list
            for adc_item in self.table[1]:
                
                if adc_now > adc_item:
                    
                    larger = True
                    if larger & smaller:
                        #value found
                        #store higher and lower indices
                        adc_indexes[0].append(self.table[1].index(adc_item))
                        adc_indexes[1].append(self.table[1].index(adc_item)-1)

                        #reset values
                        larger = False
                        smaller = False

                elif adc_now< adc_item:
                    
                    smaller = True
                    if larger & smaller:
                        #value found
                        #store higher and lower indices
                        adc_indexes[1].append(self.table[1].index(adc_item))
                        adc_indexes[0].append(self.table[1].index(adc_item)-1)
                        #reset values
                        larger = False
                        smaller = False

            i = 0 #keeping track of the index of the next for loop
            for index in adc_indexes[0]:
                #set up values for linear interpolation, to find potential rates
                #x is adc
                #y is pwm
                x = adc_now
                x2 = self.table[1][index]
                x1 = self.table[1][adc_indexes[1][i]] 
                y2 = self.table[0][index]
                y1 = self.table[0][adc_indexes[1][i]]   

                #calculate and store possible rates
                possible_rates.append(self.linear_interpolation(x,x1,x2,y1,y2))
                
                i +=1

            #find closest pwm
            closest_rate = self.find_closest_value(possible_rates,rate_now)
            opposite_rate = None
            angle1 = None
            angle2 = None
            #find other rate value so closest and found rate enclose rate now
            if closest_rate > rate_now:
                for rate in self.table[0]:
                    if rate > rate_now:
                        opposite_rate = self.table[0][self.table[0].index(rate) - 1] #get value just before

                        #find corresponding angles for these rates
                        angle1 = self.table[2][self.table[0].index(opposite_rate)]
                        angle2 = self.table[2][self.table[0].index(rate)]
                        break
            else:
                for rate in self.table[0]:
                    if rate > rate_now:
                        opposite_rate = self.table[0][self.table[0].index(rate)] #get value now

                        #find corresponding angles for these rates
                        angle2 = self.table[2][self.table[0].index(opposite_rate)]
                        angle1 = self.table[2][self.table[0].index(rate)]
                        break
            
            #interpolate angle from converted rate
            interpolated_angle = self.linear_interpolation(rate_now,closest_rate,opposite_rate,angle1,angle2)
            return interpolated_angle
            
            

                    
            