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

    class ToolTip(object):
        def __init__(self, widget, text='widget info'):
            self.wait_time = 500
            self.wrap_length = 180
            self.widget = widget
            self.text = text
            self.widget.bind("<Enter>", self.enter)
            self.widget.bind("<Leave>", self.leave)
            self.widget.bind("<ButtonPress>", self.leave)
            self.id = None
            self.tw = None

        def enter(self, event=None):
            self.schedule()

        def leave(self, event=None):
            self.unschedule()
            self.hidetip()

        def schedule(self):
            self.unschedule()
            self.id = self.widget.after(self.wait_time, self.showtip)

        def unschedule(self):
            id = self.id
            self.id = None
            if id:
                self.widget.after_cancel(id)

        def showtip(self, event=None):
            x = y = 0
            x, y, cx, cy = self.widget.bbox("insert")
            x += self.widget.winfo_rootx() + 25
            y += self.widget.winfo_rooty() + 20
            self.tw = tk.Toplevel(self.widget)
            self.tw.wm_overrideredirect(True)
            self.tw.wm_geometry("+%d+%d" % (x, y))
            label = tk.Label(self.tw, text=self.text, justify='left',
                           background="#ffffe0", relief='solid', borderwidth=1,
                           wraplength = self.wrap_length)
            label.pack(ipadx=1)

        def hidetip(self):
            tw = self.tw
            self.tw= None
            if tw:
                tw.destroy()

    def create_widgets(self):
        # Input Section
        input_group = tk.LabelFrame(self.root, text="Input", padx=10, pady=10)
        input_group.pack(fill="x", padx=10, pady=5)
        
        tk.Label(input_group, text="Folder (PNG Sequence):").pack(anchor="w")
        input_frame = tk.Frame(input_group)
        input_frame.pack(fill="x", pady=5)
        
        tk.Entry(input_frame, textvariable=self.input_folder, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(input_frame, text="Browse", command=self.browse_input).pack(side="right", padx=5)

        # Settings Section
        settings_group = tk.LabelFrame(self.root, text="Settings", padx=10, pady=10)
        settings_group.pack(fill="both", expand=True, padx=10, pady=5)

        # Shared Settings
        shared_frame = tk.Frame(settings_group)
        shared_frame.pack(fill="x", pady=5)
        
        # FPS
        tk.Label(shared_frame, text="FPS:").grid(row=0, column=0, sticky="w", padx=5)
        fps_scale = tk.Scale(shared_frame, from_=1, to=120, orient="horizontal", variable=self.fps)
        fps_scale.grid(row=0, column=1, sticky="we", padx=5)
        self.ToolTip(fps_scale, "Frames per second for video/animation.")

        # Width
        tk.Label(shared_frame, text="Width (px):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.width_scale = tk.Scale(shared_frame, from_=1, to=100, orient="horizontal", variable=self.width, state="disabled")
        self.width_scale.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        self.ToolTip(self.width_scale, "Width of the output. Disabled until input folder is selected.")
        
        shared_frame.columnconfigure(1, weight=1)

        # Tabs
        self.notebook = ttk.Notebook(settings_group)
        self.notebook.pack(pady=10, fill="both", expand=True)

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
        
        # Populate Tabs
        self.create_avif_settings(self.avif_tab)
        tk.Label(self.webm_tab, text="Use Shared Settings (VP9).\nQuality slider maps to CRF.").pack(pady=20)
        tk.Label(self.safari_tab, text="Use Shared Settings (HEVC + Alpha).\nQuality slider maps to CRF.").pack(pady=20)
        tk.Label(self.gif_tab, text="Use Shared Settings.").pack(pady=20)
        tk.Label(self.png_tab, text="Use Shared Settings.").pack(pady=20)

        # Bind tab change
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # Output Section
        output_group = tk.LabelFrame(self.root, text="Output", padx=10, pady=10)
        output_group.pack(fill="x", padx=10, pady=5)

        tk.Label(output_group, text="Destination File:").pack(anchor="w")
        output_frame_inner = tk.Frame(output_group)
        output_frame_inner.pack(fill="x", pady=5)
        
        tk.Entry(output_frame_inner, textvariable=self.output_file, state="readonly").pack(side="left", fill="x", expand=True)
        tk.Button(output_frame_inner, text="Browse", command=self.browse_output).pack(side="right", padx=5)

        # Actions
        action_frame = tk.Frame(self.root)
        action_frame.pack(fill="x", padx=20, pady=10)

        self.convert_btn = tk.Button(action_frame, text="Convert", command=self.start_conversion, height=2, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.convert_btn.pack(side="left", fill="x", expand=True)
        
        self.open_btn = tk.Button(action_frame, text="Open Folder", command=self.open_output_folder, state="disabled", height=2)
        self.open_btn.pack(side="right", padx=(10, 0))

        # Status
        tk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w").pack(side="bottom", fill="x")

    def create_avif_settings(self, parent):
        frame = tk.Frame(parent)
        frame.pack(fill="x", pady=10)
        
        # Quality
        tk.Label(frame, text="Quality (0-100):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        q_scale = tk.Scale(frame, from_=0, to=100, orient="horizontal", variable=self.quality)
        q_scale.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        self.ToolTip(q_scale, "0=Low, 100=High. For WebM/Safari, this maps to CRF.")
        
        frame.columnconfigure(1, weight=1)

    # ... (other create_*_settings methods remain empty/pass) ...

    def open_output_folder(self):
        output_file = self.output_file.get()
        if output_file and os.path.exists(output_file):
             folder = os.path.dirname(output_file)
             os.startfile(folder)
        elif output_file:
             # Try opening folder even if file doesn't exist yet (unlikely here but safety)
             folder = os.path.dirname(output_file)
             if os.path.exists(folder):
                 os.startfile(folder)

    # ... (rest of methods) ...

    def conversion_success(self):
        self.status_var.set("Conversion Complete!")
        self.convert_btn.config(state="normal", text="Convert")
        self.open_btn.config(state="normal") # Enable open button
        messagebox.showinfo("Success", "Conversion completed successfully!")

    def conversion_error(self, message):
        self.status_var.set("Error occurred")
        self.convert_btn.config(state="normal", text="Convert")
        messagebox.showerror("Error", message)


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
        self.open_btn.config(state="normal") # Enable open button
        messagebox.showinfo("Success", "Conversion completed successfully!")

    def conversion_error(self, message):
        self.status_var.set("Error occurred")
        self.convert_btn.config(state="normal", text="Convert")
        messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = AVIFConverterGUI(root)
    root.mainloop()
