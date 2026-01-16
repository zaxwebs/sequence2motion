import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from PIL import Image
from convert import convert_images

class AVIFConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PNG Sequence Converter")
        self.root.geometry("500x550")

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

        # Shared Settings Frame
        shared_frame = tk.Frame(self.root)
        shared_frame.pack(pady=5, padx=10, fill="x")

        # FPS (Shared)
        tk.Label(shared_frame, text="FPS:").grid(row=0, column=0, sticky="w", padx=5)
        tk.Scale(shared_frame, from_=1, to=120, orient="horizontal", variable=self.fps).grid(row=0, column=1, sticky="we", padx=5)

        # Width (Shared)
        tk.Label(shared_frame, text="Width (px):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.width_scale = tk.Scale(shared_frame, from_=1, to=100, orient="horizontal", variable=self.width, state="disabled")
        self.width_scale.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        
        shared_frame.columnconfigure(1, weight=1)

        # Tabs for Export Settings
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Create Tab Frames
        self.avif_tab = tk.Frame(self.notebook)
        self.webm_tab = tk.Frame(self.notebook)
        self.safari_tab = tk.Frame(self.notebook)
        self.gif_tab = tk.Frame(self.notebook)
        self.png_tab = tk.Frame(self.notebook)

        self.notebook.add(self.avif_tab, text="AVIF")
        self.notebook.add(self.webm_tab, text="WebM")
        self.notebook.add(self.safari_tab, text="Safari (HEVC)")
        self.notebook.add(self.gif_tab, text="GIF")
        self.notebook.add(self.png_tab, text="APNG")
        
        # Populate Tabs (only format specific settings now)
        self.create_avif_settings(self.avif_tab)
        # WebM, Safari, GIF and APNG tabs are empty/informational for now as settings are shared
        tk.Label(self.webm_tab, text="Settings are shared above (VP9).").pack(pady=20)
        tk.Label(self.safari_tab, text="Settings are shared above (HEVC + Alpha).").pack(pady=20)
        tk.Label(self.gif_tab, text="Settings are shared above.").pack(pady=20)
        tk.Label(self.png_tab, text="Settings are shared above.").pack(pady=20)

        # Bind tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Output File (moved to bottom)
        tk.Label(self.root, text="Output File:").pack(pady=5, anchor="w", padx=10)
        output_frame = tk.Frame(self.root)
        output_frame.pack(fill="x", padx=10)
        tk.Entry(output_frame, textvariable=self.output_file, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(output_frame, text="Browse", command=self.browse_output).pack(side="right", padx=5)

        # Convert Button
        self.convert_btn = tk.Button(self.root, text="Convert", command=self.start_conversion, height=2, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.convert_btn.pack(pady=10, fill="x", padx=20)

        # Status
        tk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w").pack(side="bottom", fill="x")

    def create_avif_settings(self, parent):
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=10)
        
        # Quality
        tk.Label(frame, text="Quality (0-100):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Scale(frame, from_=0, to=100, orient="horizontal", variable=self.quality).grid(row=0, column=1, sticky="we", padx=5, pady=5)
        
        frame.columnconfigure(1, weight=1)

    def create_webm_settings(self, parent):
        pass
        
    def create_safari_settings(self, parent):
        pass

    def create_gif_settings(self, parent):
        pass

    def create_png_settings(self, parent):
        pass

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

    def on_tab_change(self, event):
        current_file = self.output_file.get()
        if not current_file:
            return

        current_tab_index = self.notebook.index(self.notebook.select())
        
        base, _ = os.path.splitext(current_file)
        
        if current_tab_index == 0: # AVIF
            new_ext = ".avif"
        elif current_tab_index == 1: # WebM
            new_ext = ".webm"
        elif current_tab_index == 2: # Safari
            new_ext = ".mov"
        elif current_tab_index == 3: # GIF
            new_ext = ".gif"
        elif current_tab_index == 4: # APNG
            new_ext = ".png"
        else:
            return

        new_file = base + new_ext
        self.output_file.set(new_file)

    def browse_output(self):
        # Determine current tab
        current_tab_index = self.notebook.index(self.notebook.select())
        
        # Default file types based on tab
        if current_tab_index == 0: # AVIF
             filetypes = [("AVIF files", "*.avif")]
             defaultextension = ".avif"
        elif current_tab_index == 1: # WebM
             filetypes = [("WebM files", "*.webm")]
             defaultextension = ".webm"
        elif current_tab_index == 2: # Safari
             filetypes = [("Safari/QuickTime files", "*.mov")]
             defaultextension = ".mov"
        elif current_tab_index == 3: # GIF
             filetypes = [("GIF files", "*.gif")]
             defaultextension = ".gif"
        elif current_tab_index == 4: # APNG
             filetypes = [("APNG files", "*.png")]
             defaultextension = ".png"
        else:
             filetypes = [("All files", "*.*")]
             defaultextension = ""

        # Determine initial directory (parent of input folder)
        initialdir = None
        input_path = self.input_folder.get()
        if input_path and os.path.exists(input_path):
            initialdir = os.path.dirname(input_path)

        # Remove Confirm Overwrite
        file = filedialog.asksaveasfilename(
            defaultextension=defaultextension, 
            filetypes=filetypes,
            initialdir=initialdir,
            confirmoverwrite=False
        )
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
        thread = threading.Thread(target=self.run_conversion, args=(input_folder, output_file))
        thread.start()

    def update_progress(self, current, total, message):
        # Schedule GUI updates on the main thread
        self.root.after(0, lambda: self._update_progress_gui(current, total, message))

    def _update_progress_gui(self, current, total, message):
        self.status_var.set(message)

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

            success = convert_images(
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
        self.convert_btn.config(state="normal", text="Convert")
        messagebox.showinfo("Success", "Conversion completed successfully!")

    def conversion_error(self, message):
        self.status_var.set("Error occurred")
        self.convert_btn.config(state="normal", text="Convert")
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = AVIFConverterGUI(root)
    root.mainloop()
