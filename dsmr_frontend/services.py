import struct


def hex_color_to_rgb(hex_color):
    """
    Converts a hex color string to an RGB list.
    Thanks to: http://stackoverflow.com/a/4296263/5905550
    """
    hex_color = hex_color.replace('#', '')
    return struct.unpack('BBB', bytes.fromhex(hex_color))
