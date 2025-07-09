import customtkinter as ctk
from tkinter import colorchooser, filedialog
import ctypes
import sys
import subprocess
import time
import ctypes.wintypes

# Get primary monitor resolution
user32 = ctypes.windll.user32
user32.SetProcessDPIAware()
APP_WIDTH = user32.GetSystemMetrics(0)
APP_HEIGHT = user32.GetSystemMetrics(1)

# Windows API constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20
SWP_NOZORDER = 0x0004
SWP_NOACTIVATE = 0x0010

# Helper to get the toplevel window from a widget
def get_toplevel_window(widget):
    return widget.winfo_toplevel()

# Set or unset click-through (passthrough) for a window
def set_click_through(window, enable=True):
    hwnd = int(window.winfo_id())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    if enable:
        style |= WS_EX_LAYERED | WS_EX_TRANSPARENT
    else:
        style &= ~(WS_EX_TRANSPARENT)
    ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)

# Find window by process id
FindWindow = ctypes.windll.user32.FindWindowW
EnumWindows = ctypes.windll.user32.EnumWindows
GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
SetParent = ctypes.windll.user32.SetParent
SetWindowPos = ctypes.windll.user32.SetWindowPos
IsWindowVisible = ctypes.windll.user32.IsWindowVisible

selected_exe = None
embedded_proc = None
embedded_hwnd = None

# Helper to find the main window handle for a process
def get_hwnd_for_pid(pid):
    hwnds = []
    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    def enum_windows(hwnd, lParam):
        if IsWindowVisible(hwnd):
            pid_ = ctypes.c_ulong()
            GetWindowThreadProcessId(hwnd, ctypes.byref(pid_))
            if pid_.value == pid:
                hwnds.append(hwnd)
        return True
    EnumWindows(enum_windows, 0)
    return hwnds[0] if hwnds else None

# UI logic
def launch_app(parent):
    global selected_exe, embedded_proc, embedded_hwnd
    frame = ctk.CTkFrame(parent)
    frame.pack(fill="both", expand=True)
    frame.pack_propagate(False)
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)  # Make frame always fullscreen

    def select_exe():
        global selected_exe
        exe = filedialog.askopenfilename(
            title="Select an EXE",
            filetypes=[("Executable Files", "*.exe")]
        )
        if exe:
            selected_exe = exe
            exe_label.configure(text=f"Selected: {exe}")

    def embed_exe():
        global embedded_proc, embedded_hwnd
        if not selected_exe:
            exe_label.configure(text="No EXE selected!")
            return
        # Launch the process
        embedded_proc = subprocess.Popen(selected_exe)
        # Wait for the window to appear
        for _ in range(50):
            hwnd = get_hwnd_for_pid(embedded_proc.pid)
            if hwnd:
                embedded_hwnd = hwnd
                break
            time.sleep(0.1)
        else:
            exe_label.configure(text="Window not found!")
            return
        # Set window style to borderless (windowed fullscreen)
        GWL_STYLE = -16
        WS_POPUP = 0x80000000
        SWP_SHOWWINDOW = 0x0040
        # Remove window borders and title bar
        style = ctypes.windll.user32.GetWindowLongW(embedded_hwnd, GWL_STYLE)
        style &= ~(0x00CF0000 | 0x00040000 | 0x00020000 | 0x00010000 | 0x00080000)  # Remove caption, thickframe, sysmenu, minimize, maximize
        style |= WS_POPUP
        ctypes.windll.user32.SetWindowLongW(embedded_hwnd, GWL_STYLE, style)
        # Resize/move the window to cover the entire screen
        ctypes.windll.user32.SetWindowPos(embedded_hwnd, None, 0, 0, APP_WIDTH, APP_HEIGHT, SWP_NOZORDER | SWP_NOACTIVATE | SWP_SHOWWINDOW)
        # Maximize the embedded window as if the user clicked the maximize button
        WM_SYSCOMMAND = 0x0112
        SC_MAXIMIZE = 0xF030
        ctypes.windll.user32.ShowWindow(embedded_hwnd, 3)  # SW_MAXIMIZE
        ctypes.windll.user32.PostMessageW(embedded_hwnd, WM_SYSCOMMAND, SC_MAXIMIZE, 0)
        # Set parent to our frame
        SetParent(embedded_hwnd, frame.winfo_id())
        exe_label.configure(text=f"Embedded: {selected_exe}")
        # Get window rect and log resolution
        rect = ctypes.wintypes.RECT()
        ctypes.windll.user32.GetWindowRect(embedded_hwnd, ctypes.byref(rect))
        width = rect.right - rect.left
        height = rect.bottom - rect.top
        #with open("log.txt", "a") as logf:
        #    logf.write(f"Embedded EXE: {selected_exe}\nResolution: {width}x{height}\n\n")
        maximize_embedded()

    def maximize_embedded():
        if embedded_hwnd:
            WM_SYSCOMMAND = 0x0112
            SC_MAXIMIZE = 0xF030
            ctypes.windll.user32.ShowWindow(embedded_hwnd, 3)  # SW_MAXIMIZE
            ctypes.windll.user32.PostMessageW(embedded_hwnd, WM_SYSCOMMAND, SC_MAXIMIZE, 0)

    exe_btn = ctk.CTkButton(frame, text="Select EXE", command=select_exe)
    exe_btn.pack(pady=10)
    exe_label = ctk.CTkLabel(frame, text="No EXE selected")
    exe_label.pack(pady=5)

    embed_btn = ctk.CTkButton(frame, text="Start EXE", command=embed_exe)
    embed_btn.pack(pady=10)
