from __future__ import with_statement

from numpy import pi
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import letter

from kiva.pdf import GraphicsContext

def draw_ellipse(gc, x, y, major, minor, angle):
    """ Draws an ellipse given major and minor axis lengths.  **angle** is
    the angle between the major axis and the X axis, in radians.
    """
    with gc:
        gc.translate_ctm(x, y)
        ratio = float(major) / minor
        gc.rotate_ctm(angle)
        gc.scale_ctm(ratio, 1.0)
        gc.arc(0, 0, minor, 0.0, 2 * pi)
        gc.stroke_path()
        gc.move_to(-minor, 0)
        gc.line_to(minor, 0)
        gc.move_to(0, -minor)
        gc.line_to(0, minor)
        gc.stroke_path()

def draw_round_rect(gc):
    """ Draws a black rect with round corners.
    """
    w = 500
    h = 500

    r = max(1, min(w,h)/10)
    gc.set_line_width(2.0)
    gc.set_stroke_color((0.0, 0.0, 0.0, 1.0))
    gc.move_to(w/3, h/2)

    gc.arc_to(w/3, 2*h/3,
              w/2, 2*h/3,
              r)
    gc.arc_to(2*w/3, 2*h/3,
              2*w/3, h/2,
              r)
    gc.arc_to(2*w/3, h/3,
              w/2, h/3,
              r)
    gc.arc_to(w/3, h/3,
              w/3, h/2,
              r)
    gc.line_to(w/3, h/2)
    gc.stroke_path()


canvas = Canvas(filename='arcs.pdf', pagesize=letter)
gc = GraphicsContext(canvas)

gc.set_alpha(0.3)
gc.set_stroke_color((1.0,0.0,0.0))
gc.set_fill_color((0.0,1.0,0.0))
gc.rect(95, 95, 10, 10)
gc.fill_path()
draw_ellipse(gc, 100, 100, 35.0, 25.0, pi / 6)
draw_round_rect(gc)
gc.save()

