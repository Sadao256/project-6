"""
Open and close time calculations
for ACP-sanctioned brevets
following rules described at https://rusa.org/octime_acp.html
and https://rusa.org/pages/rulesForRiders
"""
import arrow

speed_min = [15, 15, 15, 11.428, 11.428, 13.333]
speed_max = [34, 32, 30, 28, 28, 26]

def open_time(control_dist_km, brevet_dist_km, brevet_start_time):

    time_min = 0
    index = 0

    if control_dist_km > brevet_dist_km:
        control_dist_km = brevet_dist_km

    if control_dist_km == 0:
        return brevet_start_time
    else:

        while control_dist_km > 200:
            time_min += 200 / speed_max[index]
            index += 1
            control_dist_km -= 200

        # Calculate the time it takes to reach the control point
        time_min += (control_dist_km / speed_max[index])
        time_min = (time_min*60)+.5

        # shift the the start time based on the minimum time needed going the fastest speed
        open_time_calc = arrow.get(brevet_start_time).shift(minutes=time_min)

        return open_time_calc

def close_time(control_dist_km, brevet_dist_km, brevet_start_time):
    time_max = 0

    if control_dist_km > brevet_dist_km:
        control_dist_km = brevet_dist_km

    if brevet_dist_km == 200 and control_dist_km == 200:
        # Calculate the time it takes to reach the control point
        time_max = control_dist_km / speed_min[0]

        # Calculate the open time based on the brevet start time
        close_time_calc = arrow.get(brevet_start_time).shift(minutes=(((time_max*60) + .5)+10))

        return close_time_calc
    
    if brevet_dist_km == 400 and control_dist_km == 400:
        # Calculate the time it takes to reach the control point
        time_max = control_dist_km / speed_min[2]

        # Calculate the open time based on the brevet start time
        close_time_calc = arrow.get(brevet_start_time).shift(minutes=((time_max*60) + .5)+20)
        
        return close_time_calc

    index = 0
    if control_dist_km <= 60:
        # For controls within the first 60 kilometers
        time_max = (control_dist_km / 20) + 1
        close_time_calc = arrow.get(brevet_start_time).shift(minutes=((time_max*60) + .5))
        return close_time_calc
    else:
        # For controls more than 60 kilometers (60 < control)
        while control_dist_km > 200:
            time_max += 200 / speed_min[index]
            control_dist_km -= 200
            index += 1
            
        #calculate the close time9
        time_max += (control_dist_km/speed_min[index])  
        time_max = ((time_max*60) + .5)

         # shift the the start time based on the maximum time needed going the fastest speed
        close_time_calc = arrow.get(brevet_start_time).shift(minutes=time_max)

        return close_time_calc


