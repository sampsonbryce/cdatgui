def getRoiSize( roi ):
    if roi == None: return 0
    return abs((roi[2]-roi[0])*(roi[3]-roi[1]))

def getTitle( dsid, name, attributes, showUnits=False ):
       long_name = attributes.get( 'long_name', attributes.get( 'standard_name', name ) )
       if not showUnits: return "%s:%s" % ( dsid, long_name )
       units = attributes.get( 'units', 'unitless' )
       return  "%s:%s (%s)" % ( dsid, long_name, units )
   
def isDesignated( axis ):
    return ( axis.isLatitude() or axis.isLongitude() or axis.isLevel() or axis.isTime() )

def matchesAxisType( axis, axis_attr, axis_aliases ):
    matches = False
    aname = axis.id.lower()
    axis_attribute = axis.attributes.get('axis',None)
    if axis_attribute and ( axis_attribute.lower() in axis_attr ):
        matches = True
    else:
        for axis_alias in axis_aliases:
            if ( aname.find( axis_alias ) >= 0): 
                matches = True
                break
    return matches

class AxisType:
    NONE = 0
    Time = 1
    Longitude = 2
    Latitude = 3
    Level = 4
    lev_aliases = [ 'bottom', 'top', 'zdim' ]
    lev_axis_attr = [ 'z' ]
    lat_aliases = [ 'north', 'south', 'ydim' ]
    lat_axis_attr = [ 'y' ]
    lon_aliases = [ 'east', 'west', 'xdim' ]
    lon_axis_attr = [ 'x' ]

def getAxisType(axis):
    if axis.isLevel() or matchesAxisType( axis, AxisType.lev_axis_attr, AxisType.lev_aliases ):
        return AxisType.Level      
    elif axis.isLatitude() or matchesAxisType( axis, AxisType.lat_axis_attr, AxisType.lat_aliases ):
        return AxisType.Latitude                   
    elif axis.isLongitude() or matchesAxisType( axis, AxisType.lon_axis_attr, AxisType.lon_aliases ):
        return AxisType.Longitude     
    elif axis.isTime():
        return AxisType.Time
    else: return  AxisType.NONE    

def designateAxisType(self, axis):
    if not isDesignated( axis ):
        if matchesAxisType( axis, AxisType.lev_axis_attr, AxisType.lev_aliases ):
            axis.designateLevel() 
            return AxisType.Level         
        elif matchesAxisType( axis, AxisType.lat_axis_attr, AxisType.lat_aliases ):
            axis.designateLatitude() 
            return AxisType.Latitude                    
        elif matchesAxisType( axis, AxisType.lon_axis_attr, AxisType.lon_aliases ):
            axis.designateLongitude()
            return AxisType.Longitude    
    return getAxisType(axis)

                   
