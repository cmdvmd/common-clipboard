"""
GUI to edit the current port the application is running on
"""

import tkinter
from tkinter import ttk
from tkinter import messagebox


class PortEditor:
    def __init__(self, current_port):
        self.applied = False

        self.root = tkinter.Tk()
        self.root.title('Edit Port')
        self.root.iconbitmap('systray_icon.ico')
        self.root.geometry('250x75')
        self.root.resizable(False, False)
        self.root.bind('<Return>', lambda _: self.apply_port_number())

        self.port_label = ttk.Label(self.root, text='Enter a port number:', font=('Arial', 11))
        self.port_label.pack(side=tkinter.TOP, padx=5, pady=5, fill=tkinter.X)

        self.entry_frame = ttk.Frame(self.root)

        self.port_number = tkinter.IntVar(value=current_port)
        self.validate_command = self.root.register(lambda text: text.isdigit() or not text)
        self.port_input = ttk.Entry(self.root, textvariable=self.port_number, font=('Arial', 11), validate='all',
                                    validatecommand=(self.validate_command, '%P'))
        self.port_input.pack(side=tkinter.LEFT, padx=(5, 2), fill=tkinter.X, expand=True)

        self.apply_button = ttk.Button(self.root, text='Apply', command=self.apply_port_number)
        self.apply_button.pack(side=tkinter.RIGHT, padx=(2, 5))

        self.entry_frame.pack(side=tkinter.BOTTOM)

        self.root.mainloop()

    def apply_port_number(self):
        min_port = 1024
        max_port = 65535

        if min_port <= self.port_number.get() <= max_port:
            self.applied = True
            self.root.destroy()
        else:
            messagebox.showwarning(title='Invalid Port Number',
                                   message=f'Port numbers must be between {min_port} and {max_port}')
