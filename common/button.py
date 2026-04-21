import tkinter as tk
from tkinter import ttk


class CustomButton(ttk.Button):
    """Button tùy chỉnh với style riêng"""

    def __init__(self, parent, text="", command=None, style_type="primary", **kwargs):
        self.style_type = style_type
        super().__init__(parent, text=text, command=command, **kwargs)
        self.configure_style()

    def configure_style(self):
        """Cấu hình style cho button"""
        style = ttk.Style()

        if self.style_type == "primary":
            style.configure('Primary.TButton',
                            font=('Arial', 10, 'bold'))
        elif self.style_type == "success":
            style.configure('Success.TButton',
                            font=('Arial', 10),
                            foreground='green')
        elif self.style_type == "danger":
            style.configure('Danger.TButton',
                            font=('Arial', 10),
                            foreground='red')
        elif self.style_type == "warning":
            style.configure('Warning.TButton',
                            font=('Arial', 10),
                            foreground='orange')
        elif self.style_type == "info":
            style.configure('Info.TButton',
                            font=('Arial', 10),
                            foreground='blue')
        elif self.style_type == "secondary":
            style.configure('Secondary.TButton',
                            font=('Arial', 10),
                            foreground='gray')

        self.configure(style=f'{self.style_type.capitalize()}.TButton')
