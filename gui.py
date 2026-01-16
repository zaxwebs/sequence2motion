import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from PIL import Image
from convert import convert_images_to_avif

class AVIFConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG Sequence to AVIF Converter")
        self.root.geometry("500x350")

        # Variables
        self.input_folder = tk.StringVar()
        self.output_file = tk.StringVar()
        self.fps = tk.IntVar(value=24)
        self.quality = tk.IntVar(value=85)
        self.width = tk.IntVar(value=0)
        self.status_var = tk.StringVar(value="Ready")

        self.create_widgets()

    def create_widgets(self):
        # Input Folder
        tk.Label(self.root, text="Input Folder (PNG Sequence):").pack(pady=5, anchor="w", padx=10)
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill="x", padx=10)
        tk.Entry(input_frame, textvariable=self.input_folder, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(input_frame, text="Browse", command=self.browse_input).pack(side="right", padx=5)

        # Output File
        tk.Label(self.root, text="Output File (AVIF):").pack(pady=5, anchor="w", padx=10)
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill="x", padx=10)
        tk.Entry(output_frame, textvariable=self.output_file, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(output_frame, text="Browse", command=self.browse_output).pack(side="right", padx=5)

        # Settings Frame
        settings_frame = tk.Frame(self.root)
        settings_frame.pack(pady=15, padx=10, fill="x")

        # FPS
        tk.Label(settings_frame, text="FPS:").grid(row=0, column=0, sticky="w", padx=5)
        tk.Scale(settings_frame, from_=1, to=120, orient="horizontal", variable=self.fps).grid(row=0, column=1, sticky="we", padx=5)
        
        # Quality
        tk.Label(settings_frame, text="Quality (0-100):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Scale(settings_frame, from_=0, to=100, orient="horizontal", variable=self.quality).grid(row=1, column=1, sticky="we", padx=5, pady=5)

        # Width
        tk.Label(settings_frame, text="Width (px):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.width_scale = tk.Scale(settings_frame, from_=1, to=100, orient="horizontal", variable=self.width, state="disabled")
        self.width_scale.grid(row=2, column=1, sticky="we", padx=5, pady=5)

        settings_frame.columnconfigure(1, weight=1)

        # Convert Button
        self.convert_btn = tk.Button(self.root, text="Convert to AVIF", command=self.start_conversion, height=2, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.convert_btn.pack(pady=10, fill="x", padx=20)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=100, mode="determinate")
        self.progress.pack(pady=5, fill="x", padx=20)

        # Status
        tk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w").pack(side="bottom", fill="x")

    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)
            self.scan_folder_for_width(folder)

    def scan_folder_for_width(self, folder):
        try:
            files = [f for f in os.listdir(folder) if f.lower().endswith('.png')]
            files.sort()
            if files:
                first_img_path = os.path.join(folder, files[0])
                img = Image.open(first_img_path)
                width = img.width
                
                self.width_scale.config(from_=1, to=width, state="normal")
                self.width.set(width)
            else:
                self.width_scale.config(state="disabled")
        except Exception as e:
            print(f"Error scanning folder: {e}")
            self.width_scale.config(state="disabled")

    def browse_output(self):
        file = filedialog.asksaveasfilename(defaultextension=".avif", filetypes=[("AVIF files", "*.avif")])
        if file:
            self.output_file.set(file)

    def start_conversion(self):
        input_folder = self.input_folder.get()
        output_file = self.output_file.get()
        
        if not input_folder:
            messagebox.showerror("Error", "Please select an input folder.")
            return
        if not output_file:
            messagebox.showerror("Error", "Please select an output file.")
            return

        self.convert_btn.config(state="disabled", text="Converting...")
        self.status_var.set("Converting...")
        
        # Run in separate thread
        self.progress["value"] = 0
        thread = threading.Thread(target=self.run_conversion, args=(input_folder, output_file))
        thread.start()

    def update_progress(self, current, total, message):
        # Schedule GUI updates on the main thread
        self.root.after(0, lambda: self._update_progress_gui(current, total, message))

    def _update_progress_gui(self, current, total, message):
        self.status_var.set(message)
        if total > 0:
            percentage = (current / total) * 100
            self.progress["value"] = percentage
            if message.startswith("Encoding"):
                self.progress.config(mode="indeterminate")
                self.progress.start(10)
            else:
                 self.progress.config(mode="determinate")

    def run_conversion(self, input_folder, output_file):
        try:
            fps = self.fps.get()
            quality = self.quality.get()
            width = self.width.get()
            
            # If width is same as max (original), pass None to avoid resizing
            if self.width_scale.cget("state") == "normal":
                 original_width = self.width_scale.cget("to")
                 if width == original_width:
                     width = None
            else:
                width = None

            success = convert_images_to_avif(
                input_folder, 
                output_file, 
                fps, 
                quality, 
                width=width,
                progress_callback=self.update_progress
            )
            
            if success:
                self.root.after(0, self.conversion_success)
            else:
                self.root.after(0, lambda: self.conversion_error("Conversion failed. Check console for details."))
        except Exception as e:
            self.root.after(0, lambda: self.conversion_error(str(e)))

    def conversion_success(self):
        self.status_var.set("Conversion Complete!")
        self.progress.stop()
        self.progress["value"] = 100
        self.progress.config(mode="determinate")
        self.convert_btn.config(state="normal", text="Convert to AVIF")
        messagebox.showinfo("Success", "Conversion completed successfully!")

    def conversion_error(self, message):
        self.status_var.set("Error occurred")
        self.progress.stop()
        self.progress.config(mode="determinate")
        self.convert_btn.config(state="normal", text="Convert to AVIF")
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = AVIFConverterGUI(root)
    root.mainloop()
