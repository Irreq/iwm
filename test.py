# import Xlib.display
# import time
#
# display = Xlib.display.Display()
#
# time.sleep(1)
#
# def get_active_window():
#     """Retrieve current focused window's name"""
#     window = display.get_input_focus().focus
#     wmclass = window.get_wm_class()
#     if wmclass is None: #or wmname is None:
#         window = window.query_tree().parent
#         wmclass = window.get_wm_class()
#     return wmclass[1]
#
# a = get_active_window()
#
# print(a)

# win.get_wm_name()

# def anonymous(cls):
#     return cls()
#
# @anonymous
# class foo:
#      x = 42
#
#      def bar(self):
#           return self.x
#
# The decorator in this case causes the class foo to be instantiated an put into the variable foo instead of the class itself. The class itself will not be accessible from any namespace although it has a name:
#
# >>> foo
# <__main__.foo instance at 0x7fd2938d8320>
# >>> foo.bar()
# 42

#!/usr/bin/env python3

import Xlib
from Xlib import display, X   # X is also needed

display = Xlib.display.Display()
screen = display.screen()
root = screen.root

#print(root.get_attributes())
root.change_attributes(event_mask=X.ExposureMask)  # "adds" this event mask
#print(root.get_attributes())  # see the difference

gc = root.create_gc(foreground = screen.white_pixel, background = screen.black_pixel)

def draw_it():
    root.draw_text(gc, 100, 100, b"Hello, world!")
    display.flush()

draw_it()
while 1:
    if display.pending_events() != 0:  # check to safely apply next_event
        event = display.next_event()
        if event.type == X.Expose and event.count == 0:
            draw_it()
