import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

class DNSRazzleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DNSRazzle GUI")
        self.geometry("700x500")
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self)
        frm.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(frm, text="Domain(s)").grid(row=0, column=0, sticky=tk.W)
        self.domain_var = tk.StringVar()
        ttk.Entry(frm, textvariable=self.domain_var, width=40).grid(row=0, column=1, sticky=tk.W)

        ttk.Label(frm, text="Domain list file").grid(row=1, column=0, sticky=tk.W)
        self.file_var = tk.StringVar()
        entry_file = ttk.Entry(frm, textvariable=self.file_var, width=35)
        entry_file.grid(row=1, column=1, sticky=tk.W)
        ttk.Button(frm, text="Browse", command=self.browse_file).grid(row=1, column=2)

        ttk.Label(frm, text="Output directory").grid(row=2, column=0, sticky=tk.W)
        self.out_var = tk.StringVar()
        entry_out = ttk.Entry(frm, textvariable=self.out_var, width=35)
        entry_out.grid(row=2, column=1, sticky=tk.W)
        ttk.Button(frm, text="Browse", command=self.browse_out).grid(row=2, column=2)

        ttk.Label(frm, text="Browser").grid(row=3, column=0, sticky=tk.W)
        self.browser_var = tk.StringVar(value="chrome")
        ttk.Combobox(frm, textvariable=self.browser_var, values=["chrome", "firefox"], width=10).grid(row=3, column=1, sticky=tk.W)

        ttk.Label(frm, text="Threads").grid(row=4, column=0, sticky=tk.W)
        self.threads_var = tk.StringVar(value="10")
        ttk.Entry(frm, textvariable=self.threads_var, width=5).grid(row=4, column=1, sticky=tk.W)

        ttk.Label(frm, text="Screenshot delay").grid(row=5, column=0, sticky=tk.W)
        self.sdelay_var = tk.StringVar(value="2")
        ttk.Entry(frm, textvariable=self.sdelay_var, width=5).grid(row=5, column=1, sticky=tk.W)

        self.nmap_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Run nmap", variable=self.nmap_var).grid(row=6, column=0, sticky=tk.W)

        self.recon_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Run dnsrecon", variable=self.recon_var).grid(row=6, column=1, sticky=tk.W)

        self.noss_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="No screenshots", variable=self.noss_var).grid(row=7, column=0, sticky=tk.W)

        self.generate_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Generate only", variable=self.generate_var).grid(row=7, column=1, sticky=tk.W)

        self.debug_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(frm, text="Debug", variable=self.debug_var).grid(row=8, column=0, sticky=tk.W)

        ttk.Button(frm, text="Run", command=self.run_dnsrazzle).grid(row=9, column=0, pady=5)

        self.output_text = ScrolledText(self, height=15)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    def browse_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            self.file_var.set(filename)

    def browse_out(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.out_var.set(dirname)

    def run_dnsrazzle(self):
        args = [sys.executable, os.path.join(os.path.dirname(__file__), "DNSrazzle.py")]
        if self.domain_var.get():
            args += ["-d", self.domain_var.get()]
        if self.file_var.get():
            args += ["-f", self.file_var.get()]
        if self.out_var.get():
            args += ["-o", self.out_var.get()]
        if self.browser_var.get() and self.browser_var.get() != "chrome":
            args += ["--browser", self.browser_var.get()]
        if self.threads_var.get():
            args += ["-t", self.threads_var.get()]
        if self.sdelay_var.get():
            args += ["--screenshot-delay", self.sdelay_var.get()]
        if self.nmap_var.get():
            args += ["-n"]
        if self.recon_var.get():
            args += ["-r"]
        if self.noss_var.get():
            args += ["--noss"]
        if self.generate_var.get():
            args += ["-g"]
        if self.debug_var.get():
            args += ["--debug"]

        if not self.domain_var.get() and not self.file_var.get():
            messagebox.showerror("Error", "Please enter a domain or select a file")
            return

        self.output_text.delete(1.0, tk.END)

        def _append_output(line):
            self.output_text.insert(tk.END, line)
            self.output_text.see(tk.END)

        def read_output(proc):
            for line in proc.stdout:
                # Tkinter is not thread safe; queue UI updates on the main thread
                self.output_text.after(0, _append_output, line)
            proc.wait()

        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        threading.Thread(target=read_output, args=(proc,), daemon=True).start()


def main():
    app = DNSRazzleGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
