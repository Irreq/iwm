#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, subprocess

from Xlib import X, display, XK

# User Configuration
TERMINAL = "/usr/bin/alacritty"

MOD = (1 << 6)  # Super (mod4), aka "Windows" key
SHIFT = (1 << 0)
CONTROL = (1 << 2)

class WM:
    def __init__(self):
        pass
    def warp(self):
        print("Hello")
        pass

wm = WM()

def debug(message):
    print(message, file=sys.stderr)

def cmd(*args):
    """Perform a command"""
    command = "".join(args) 
    subprocess.Popen(command.split())

def restart():
        debug('restarting %s...' % sys.argv[0])
        os.execv(sys.argv[0], sys.argv)

def quit():
    debug('terminating...')
    sys.exit()

def destroy():
    pass

def warp(direction):
    def _warp():
        pass

    return _warp

def run(command):
    def _run():
        cmd(command)
    return _run

def destroy():
    pass

def resize():
    pass

keybinds = {
    (MOD, "Left"):  warp("left"),
    (MOD, "Down"):  warp("down"),
    (MOD, "Up"):    warp("up"),
    (MOD, "Right"): warp("right"),

    (MOD, "Control_L"): resize,  # Move pointer to resize

    (MOD | SHIFT, "q"): destroy,
    (MOD | SHIFT, "e"): quit,
    (MOD | SHIFT, "r"): restart,

    (MOD, "Return"): run(TERMINAL),
}

root_display = display.Display()
root_screen = root_display.screen()
mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask
            | X.EnterWindowMask | X.LeaveWindowMask | X.FocusChangeMask)
root_screen.root.change_attributes(event_mask=mask)

# Configure the root window to receive key inputs defined in `keybinds`.
key_handlers = {}

for modifier, key in keybinds:
    code = root_display.keysym_to_keycode(XK.string_to_keysym(key))
    root_screen.root.grab_key(code, modifier, 1, X.GrabModeAsync,
                                X.GrabModeAsync)
    key_handlers[(modifier, code)] = (key, keybinds[(modifier, key)])

# Handle modifier
root_screen.root.grab_key(
    root_display.keysym_to_keycode(XK.string_to_keysym("Super_L")), 
    X.AnyModifier, 1, X.GrabModeAsync, X.GrabModeAsync
)

windows_managed = []
windows_exposed = []

is_managed_window = lambda window: window in windows_managed

def unmanage_window(window):
    if is_managed_window(window):
        windows_managed.remove(window)
        if window in windows_exposed:
            windows_exposed.remove(window)

        window.unmap()

def manage_window(window):
    if is_managed_window(window):
        return
    
    try:
        attrs = window.get_attributes()
        if attrs is None:
            return
        if attrs.override_redirect:
            return
    except:
        return
    
    windows_managed.append(window)
    windows_exposed.append(window)

    window.map()
    mask = X.EnterWindowMask | X.LeaveWindowMask
    window.change_attributes(event_mask=mask)

# ---------------- event handlers
def handle_keypress(event):
    (_, entry) = key_handlers.get((event.state, event.detail), (None, None))
    if entry:
        entry()

def handle_key_release(event):
    root_display.ungrab_pointer(0)

def handle_enter_notify(event):
    window = event.window
    if window in windows_exposed:
        window.set_input_focus(X.RevertToParent, 0)
        window.configure(stack_mode=X.Above)

def handle_destroy_notify(event):
    window = event.window
    unmanage_window(window)

def handle_unmap_notify(event):
    window = event.window
    if window in windows_exposed:
        unmanage_window(window)

def handle_map_notify(event):
    window = event.window
    if not is_managed_window(window):
        manage_window(window)


EVENT_HANDLER = {
        X.KeyPress: handle_keypress,  # 2
        X.KeyRelease: handle_key_release,  # 3
        # X.MotionNotify: "handle_motion_notify",  # 6
        X.EnterNotify: handle_enter_notify,  # 7
        X.DestroyNotify: handle_destroy_notify,  # 17
        X.UnmapNotify: handle_unmap_notify,  # 18
        X.MapNotify: "handle_map_notify",  # 19
        X.MapRequest: "handle_map_request",  # 20
        X.ConfigureRequest: "handle_configure_request",  # 23
}

while True:
    event = root_display.next_event()
    handler = EVENT_HANDLER.get(event.type, None)
    if handler:
        handler(event)
    else:
        debug(str(event)) # Unhandled event