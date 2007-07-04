"""
Define a standard horizontal and vertical Enable 'scrollbar' component.
"""

# Global Imports
import wx
from types import TupleType

# Enthought Imports
from enthought.traits.api import Event, Property, Trait, TraitError, \
     Any, Str, Bool, Float, false, Int
from enthought.traits.ui.api import Group, View, Include

from enthought.enable2.component import Component

def valid_range ( object, name, value ):
    "Verify that a set of range values for a scrollbar is valid"
    try:
        if (type( value ) is TupleType) and (len( value ) == 4):
            low, high, page_size, line_size = value
            if high < low:
                low, high = high, low
            elif high == low:
                high = low + 1.0
            page_size = max( min( page_size, high - low ), 0.0 )
            line_size = max( min( line_size, page_size ),  0.0 )
            return ( float( low ),       float( high ),
                     float( page_size ), float( line_size ) )
    except:
        raise
    raise TraitError

valid_range.info = 'a (low,high,page_size,line_size) range tuple'


def valid_scroll_position ( object, name, value ):
    "Verify that a specified scroll bar position is valid"
    try:
        low, high, page_size, line_size = object.range
        return max( min( float( value ), high - page_size ), low ) 
    except:
        raise
    raise TraitError



class NativeScrollBar(Component):
    """Native scroll bar for Enable"""
    
    #-------------------------------------------
    # Public Traits
    #-------------------------------------------
    
    scroll_position = Trait( 0.0, valid_scroll_position )
    #Range is (low, high, page_size, line_size
    range = Trait( ( 0.0, 100.0, 10.0, 1.0 ), valid_range )
    orientation = Trait("horizontal", "vertical")
    origin = Trait('bottom', 'top')
    enabled = Bool(True)
    
    
    mouse_wheel_speed = Int(3)

    #--------------------------------------------
    # Private Traits
    #--------------------------------------------
    _control = Any(None)
    _clean = false
    _last_widget_x = Float(0)
    _last_widget_y = Float(0)
    _last_widget_height = Float(0)
    _list_widget_width = Float(0)

    #--------------------------------------------
    # Public Methods
    #--------------------------------------------
    
    def destroy(self):
        """Destroy the native widget associated with this component"""
        if self._control:
            self._control.Destroy()
        return

    #--------------------------------------------
    # Trait Event Handlers
    #--------------------------------------------

    def __low_get ( self ):
        return self.range[0]
        
    def __low_set ( self, low ):
        ignore, high, page_size, line_size = self.range
        self._clean = False
        self.range = ( low, high, page_size, line_size )
        
    def __high_get ( self ):
        return self.range[1]
        
    def __high_set ( self, high ):
        low, ignore, page_size, line_size = self.range
        self._clean = False
        self.range = ( low, high, page_size, line_size )
        
    def __page_size_get ( self ):
        return self.range[2]
        
    def __page_size_set ( self, page_size ):
        low, high, ignore, line_size = self.range
        self._clean = False
        self.range = ( low, high, page_size, line_size )
        
    def __line_size_get ( self ):
        return self.range[3]
        
    def __line_size_set ( self, line_size ):
        low, high, page_size, ignore = self.range
        self._clean = False
        self.range = ( low, high, page_size, line_size )
        
    # Define 'scroll_position, low, high, page_size' properties:
    low = Property( __low_get, __low_set )
    high = Property( __high_get, __high_set )
    page_size = Property( __page_size_get, __page_size_set)
    line_size = Property( __line_size_get, __line_size_set)


    def __del__(self):
        self.destroy()
        return

    def _draw(self, gc, view_bounds=None, mode="default"):
        """Draw the component."""
        # To determine whether to actually redraw the component, we first check whether
        # we're clean or not.  If we are clean, we must additionally check whether we
        # have moved in wx coordinate space.  There's no easy way to get trait notification
        # on this because it depends on the entire position stack above us.  Therefore, we
        # compute this each time and redraw if it has changed.
        
        x_pos, y_pos = self.position
        x_size, y_size = self.bounds

        wx_xpos, wx_ypos = self.container.get_absolute_coords(x_pos, y_pos+y_size-1)
        
        # We have to do this flip_y business because wx and enable use opposite
        # coordinate systems, and enable defines the component's position as its
        # lower left corner, while wx defines it as the upper left corner.
        window = getattr(gc, "window", None)
        if window is None:
            return
        wx_ypos = window._flip_y(wx_ypos)


        if self._clean and \
               self._last_widget_x == wx_xpos and \
               self._last_widget_y == wx_ypos and \
               self._last_widget_width == x_size and \
               self._last_widget_height == y_size:
            return

        self._last_widget_x = wx_xpos
        self._last_widget_y = wx_ypos
        self._last_widget_width = x_size
        self._last_widget_height = y_size
        
        
        low, high, page_size, line_size = self.range
        if self.orientation == 'horizontal':
            wxstyle = wx.HORIZONTAL
        else:
            wxstyle = wx.VERTICAL
        tmp = self._enable_to_wx_spec(self.range + (self.scroll_position,))
        (wxpos, wxthumbsize, wxrange)  = tmp
        
        if not self._control:
            self._control = wx.ScrollBar(window.control, size=wx.Size(x_size, y_size), \
                                         style=wxstyle)
            self._control.SetScrollbar(wxpos, wxthumbsize, wxrange, wxthumbsize, True)
            wx.EVT_SCROLL(self._control, self._wx_scroll_handler)
            wx.EVT_SET_FOCUS(self._control, self._yield_focus)
            self._control.Disable()
        
        
        # Ideally we would only SetPosition if the position change came from the
        # program rather than from the user.  Perhaps we should have a position_dirty
        # variable which is set by _scroll_position_changed or something like that.
        self._control.SetPosition(wx.Point(wx_xpos, wx_ypos))
        controlsize = self._control.GetSize()
        if x_size != controlsize[0] or y_size != controlsize[1]:
            self._control.SetSize(wx.Size(x_size, y_size))
        self._control.SetScrollbar(wxpos, wxthumbsize, wxrange, wxthumbsize, True)

        self._clean = True
        return
    
    def _yield_focus(self, event):
        """ Yields focus to our window, when we acquire focus via user interaction. """
        window = event.GetWindow()
        if window:
            window.SetFocus()
        return
    
    def _mouse_wheel_changed(self, event):
        event.handled  = True
        self.scroll_position -= (event.mouse_wheel * self.range[3] * self.mouse_wheel_speed)
        return

    def _scroll_position_changed(self):
        self._clean = False
        self.request_redraw()
        return
    
    def _range_changed(self):
        low, high, page_size, line_size = self.range
        self.scroll_position = max(min(self.scroll_position, high-page_size), low)
        self._clean = False
        self.request_redraw()
        return

    def _range_items_changed(self):
        self._range_changed()
        return

    def _wx_scroll_handler(self, event):
        """Handle wx scroll events"""
        #If the user moved the scrollbar, set the scroll position, but don't
        #tell wx to move the scrollbar.  Doing so causes jerkiness
        self.scroll_position = self._wx_to_enable_pos(self._control.GetThumbPosition())
        self._clean = True
        return
        
    def _enable_to_wx_spec(self, enable_spec):
        """Return the WX equivalent of an enable scroll bar specification
        From a tuple of (low, high, page_size, line_size, position),
        return (position, thumbsize, range)"""
        low, high, page_size, line_size, position = enable_spec
        if self.origin == 'bottom' and self.orientation == 'vertical':
            position = (high-page_size)-position
        if line_size == 0.0:
            return (0,high-low,high-low)
        else:
            return map(int, ((position-low)/line_size, page_size/line_size, (high-low)/line_size))

    def _wx_to_enable_pos(self, pos):
        """Translate the position that the Wx scrollbar returns into the position we store
        internally.  The difference is that we have a high and a low and a line size, while
        wx assumes low is 0 and line size is 1."""
        low, high, page_size, line_size = self.range
        enablepos = pos*line_size+low
        #If we're a veritcal scrollbar with a bottom origin, flip
        #the coordinates, since in WX the origin is always the top.
        if self.origin == 'bottom' and self.orientation == 'vertical':
            enablepos = (high-page_size)-enablepos
        return enablepos

# EOF