import sys
from svgpathtools import svg2paths, Path, Line, Arc, CubicBezier, QuadraticBezier
import numpy as np

def path_to_gcode(path, scale=1.0, feedrate=1000, z_lift=0.2, extrusion_factor=0.1):
    gcode = []
    z_height = 0.2
    e_position = 0.0

    def move_to(x, y, z=None, extrude=False):
        nonlocal e_position
        if z is not None:
            gcode.append(f"G1 Z{z:.2f} F300")
        if extrude:
            dist = np.sqrt((x - move_to.last_x) ** 2 + (y - move_to.last_y) ** 2)
            e_position += dist * extrusion_factor
            gcode.append(f"G1 X{x:.2f} Y{y:.2f} E{e_position:.5f} F{feedrate}")
        else:
            gcode.append(f"G0 X{x:.2f} Y{y:.2f} F{feedrate}")

        move_to.last_x = x
        move_to.last_y = y

    move_to.last_x = 0
    move_to.last_y = 0

    for element in path:
        if isinstance(element, Line):
            start = element.start
            end = element.end
            move_to(start.real * scale, -start.imag * scale, z=z_height)  # Invert Y-axis
            move_to(end.real * scale, -end.imag * scale, z=z_height, extrude=True)  # Invert Y-axis
        elif isinstance(element, (CubicBezier, QuadraticBezier)):
            points = [element.start, *element.control_points, element.end]
            move_to(points[0].real * scale, -points[0].imag * scale, z=z_height)  # Invert Y-axis
            for p in points[1:]:
                move_to(p.real * scale, -p.imag * scale, z=z_height, extrude=True)  # Invert Y-axis
        elif isinstance(element, Arc):
            start = element.start
            end = element.end
            move_to(start.real * scale, -start.imag * scale, z=z_height)  # Invert Y-axis
            move_to(end.real * scale, -end.imag * scale, z=z_height, extrude=True)  # Invert Y-axis

    return gcode

def svg_to_gcode(svg_file, output_file, scale=1.0, feedrate=1000, z_lift=0.2, extrusion_factor=0.1):
    paths, attributes = svg2paths(svg_file)
    with open(output_file, 'w') as f:
        # Initial setup commands for CR-10 S Pro
        f.write("G21 ; Set units to millimeters\n")
        f.write("G90 ; Use absolute positioning\n")
        f.write("M82 ; Use absolute distances for extrusion\n")
        f.write("G28 ; Home all axes\n")
        f.write("G1 Z10.0 F3000 ; Move Z Axis up to 10mm\n")
        f.write("M104 S200 ; Set extruder temperature to 200C\n")
        f.write("M140 S60 ; Set bed temperature to 60C\n")
        f.write("M109 S200 ; Wait for extruder temperature\n")
        f.write("M190 S60 ; Wait for bed temperature\n")
        f.write("G92 E0 ; Reset the extruder position\n")
        f.write("G1 F140 E30 ; Prime the nozzle\n")
        f.write("G92 E0 ; Reset the extruder position again\n")

        # Process each path in the SVG
        for path in paths:
            gcode = path_to_gcode(path, scale, feedrate, z_lift, extrusion_factor)
            for line in gcode:
                f.write(line + '\n')

        # End commands for CR-10 S Pro
        f.write("M104 S0 ; Turn off extruder\n")
        f.write("M140 S0 ; Turn off bed\n")
        f.write("G1 X0 Y0 F3000 ; Move the head to the home position\n")
        f.write("M84 ; Disable motors\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python svg_to_gcode_cr10_extrusion.py input.svg output.gcode")
    else:
        svg_file = sys.argv[1]
        output_file = sys.argv[2]
        svg_to_gcode(svg_file, output_file)
