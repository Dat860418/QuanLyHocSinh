import threading
import tkinter as tk
from tkinter import ttk


class LoadingOverlay:
    """Màn hình chờ dạng modal dùng cho tác vụ nền."""

    def __init__(self, master, message="Đang xử lý..."):
        self.master = master
        self.window = tk.Toplevel(master)
        self.window.title("Vui lòng chờ")
        self.window.geometry("320x140")
        self.window.resizable(False, False)
        self.window.transient(master)
        self.window.grab_set()
        self.window.attributes("-topmost", True)

        frame = ttk.Frame(self.window, padding=16)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text=message, font=("Arial", 11, "bold")).pack(pady=(0, 10))

        self.progress = ttk.Progressbar(frame, mode="indeterminate")
        self.progress.pack(fill="x")
        self.progress.start(10)

    def destroy(self):
        try:
            self.progress.stop()
        except Exception:
            pass
        try:
            self.window.grab_release()
        except Exception:
            pass
        if self.window.winfo_exists():
            self.window.destroy()


class AsyncTaskRunner:
    """Chạy tác vụ nền và hiển thị loading nếu chạy quá 3 giây."""

    def __init__(self, master, message="Đang xử lý..."):
        self.master = master
        self.message = message
        self.overlay = None
        self._timer_id = None
        self._done = False

    def run(self, worker, on_success=None, on_error=None):
        result_holder = {"value": None, "error": None}

        def finish():
            self._done = True
            if self._timer_id is not None:
                try:
                    self.master.after_cancel(self._timer_id)
                except Exception:
                    pass
                self._timer_id = None
            if self.overlay is not None:
                self.overlay.destroy()
                self.overlay = None
            if result_holder["error"] is not None:
                if on_error:
                    on_error(result_holder["error"])
                return
            if on_success:
                on_success(result_holder["value"])

        def target():
            try:
                result_holder["value"] = worker()
            except Exception as exc:
                result_holder["error"] = exc
            self.master.after(0, finish)

        self._timer_id = self.master.after(3000, self._show_overlay)
        threading.Thread(target=target, daemon=True).start()

    def _show_overlay(self):
        if self._done:
            return
        self.overlay = LoadingOverlay(self.master, self.message)
