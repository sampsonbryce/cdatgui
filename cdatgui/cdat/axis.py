import cdtime


def format_axis(axis):
    if axis.isTime():
        return format_time_axis(axis)
    else:
        return None


def parse_axis(axis):
    if axis.isTime():
        return parse_time_axis(axis)
    else:
        return None


def format_time_axis(axis):
    """Create a function to prettify a time axis value"""
    units = axis.units
    time_increment = units.split(" ")[0]
    calendar = axis.getCalendar()

    def format(value):
        reltime = cdtime.reltime(value, units)
        comptime = reltime.tocomp(calendar)
        if time_increment[0:6] == "second":
            return "%d-%d-%d %d:%d:%d" % (comptime.year, comptime.month, comptime.day, comptime.hour, comptime.minute, comptime.second)
        elif time_increment[0:6] == "minute":
            return "%d-%d-%d %d:%d" % (comptime.year, comptime.month, comptime.day, comptime.hour, comptime.minute)
        elif time_increment[0:4] == "hour":
            return "%d-%d-%d %d:00" % (comptime.year, comptime.month, comptime.day, comptime.hour)
        elif time_increment[0:3] == "day" or time_increment[0:4] == "week":
            return "%d-%d-%d" % (comptime.year, comptime.month, comptime.day)
        elif time_increment[0:5] == "month" or time_increment[0:6] == "season":
            return "%d-%d" % (comptime.year, comptime.month)
        elif time_increment[0:4] == "year":
            return comptime.year

    return format


def parse_time_axis(axis):
    """Create a function to retrieve indices from string"""
    units = axis.units
    time_increment = units.split(" ")[0]
    calendar = axis.getCalendar()

    def parse(value):
        parts = value.split(" ")
        if len(parts) == 1:
            # It's just a date
            date = value
            time = "0:0:0"
        else:
            date, time = parts

        # Parse date
        date_parts = date.split("-")
        num_date = [int(d) for d in date_parts if d != '']
        num_date += [0 for _ in range(3 - len(num_date))]
        year, month, day = num_date

        time_parts = time.split(":")
        num_time = [int(t) for t in time_parts if t != '']
        num_time += [0 for _ in range(3 - len(num_time))]
        hour, minute, second = num_time

        # Check if the units match up with the specificity
        if time_increment[0:6] == "second":
            if 0 in (year, month, day, hour, minute, second):
                return None
        elif time_increment[0:6] == "minute":
            if 0 in (year, month, day, hour, minute):
                return None
        elif time_increment[0:4] == "hour":
            if 0 in (year, month, day, hour):
                return None
        elif time_increment[0:3] == "day" or time_increment[0:4] == "week":
            if 0 in (year, month, day):
                return None
        elif time_increment[0:5] == "month" or time_increment[0:6] == "season":
            if 0 in (year, month):
                return None
        elif time_increment[0:4] == "year":
            if 0 in (year):
                return None

        try:
            comptime = cdtime.comptime(year, month, day, hour, minute, second)
            reltime = comptime.torel(units, calendar)
            return reltime.value
        except:
            return None
    return parse
