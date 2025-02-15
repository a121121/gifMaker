import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import numpy as np
import os
from threading import Thread
import time


class ProgressWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel(parent)
        self.window.title("Processing...")
        self.window.geometry("300x150")
        self.window.transient(parent)
        self.window.grab_set()  # Make window modal

        # Set background color to match main window
        self.window.configure(bg="#2C3E50")

        # Center the window
        self.window.geometry("+%d+%d" % (
            parent.winfo_rootx() + parent.winfo_width() // 2 - 150,
            parent.winfo_rooty() + parent.winfo_height() // 2 - 75))

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(
            self.window,
            length=200,
            mode='determinate',
            variable=self.progress_var
        )
        self.progress.pack(pady=20)

        # Status label
        self.status_label = tk.Label(
            self.window,
            text="Starting...",
            bg="#2C3E50",
            fg="#ECF0F1"
        )
        self.status_label.pack(pady=10)

        # Log text
        self.log = tk.Text(
            self.window,
            height=3,
            width=35,
            bg="#34495E",
            fg="#ECF0F1",
            relief="flat"
        )
        self.log.pack(pady=10)

    def update_progress(self, value, status):
        self.progress_var.set(value)
        self.status_label.config(text=status)
        self.log.insert(tk.END, f"{status}\n")
        self.log.see(tk.END)
        self.window.update()


class GIFMaker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GIF Maker with Smooth Transparency")
        self.root.configure(bg="#2C3E50")
        self.setup_styles()
        self.create_gui()
        self.center_window(800, 700)  # Increased height

    def setup_styles(self):
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('default')

        # Configure common elements
        self.style.configure('TFrame', background='#2C3E50')
        self.style.configure('TLabel',
                             background='#2C3E50',
                             foreground='#ECF0F1')
        self.style.configure('TButton',
                             padding=10,
                             background='#3498DB',
                             foreground='#ECF0F1')
        self.style.configure('TEntry',
                             fieldbackground='#34495E',
                             foreground='#ECF0F1',
                             padding=5)
        self.style.configure('TRadiobutton',
                             background='#2C3E50',
                             foreground='#ECF0F1')
        self.style.configure('TCheckbutton',
                             background='#2C3E50',
                             foreground='#ECF0F1')

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Heading
        heading_label = tk.Label(
            main_frame,
            text="GIF Maker with Smooth Transparency",
            font=("Helvetica", 20, "bold"),
            bg="#2C3E50",
            fg="#ECF0F1"
        )
        heading_label.pack(pady=20)

        # Input frame
        input_frame = ttk.Frame(main_frame)
        input_frame.pack(fill=tk.X, pady=10)

        # Frame Rate
        self.frame_rate = tk.StringVar(value="40")
        self.create_labeled_entry(
            input_frame, "Frame Rate (ms):", self.frame_rate, 0)

        # Colors
        self.colors = tk.StringVar(value="256")
        self.create_labeled_entry(
            input_frame, "Number of Colors (2-256):", self.colors, 1)

        # Resize factor
        self.resize_factor = tk.StringVar(value="1.0")
        self.create_labeled_entry(
            input_frame, "Resize Factor (0.1-1.0):", self.resize_factor, 2)

        # Options frame
        options_frame = ttk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=10)

        # Lossy compression
        self.lossy_var = tk.BooleanVar()
        lossy_check = tk.Checkbutton(
            options_frame,
            text="Enable Lossy Compression",
            variable=self.lossy_var,
            bg="#2C3E50",
            fg="#ECF0F1",
            selectcolor="#34495E",
            activebackground="#2C3E50",
            activeforeground="#ECF0F1"
        )
        lossy_check.pack(pady=5)

        # Dithering
        self.dither_var = tk.StringVar(value=Image.Dither.NONE)
        self.create_radio_group(
            options_frame,
            "Dithering Method:",
            [("None", Image.Dither.NONE),
             ("Floyd-Steinberg", Image.Dither.FLOYDSTEINBERG)],
            self.dither_var
        )

        # Disposal
        self.disposal_var = tk.IntVar(value=2)
        self.create_radio_group(
            options_frame,
            "Frame Disposal Method:",
            [("None", 0), ("Keep", 1), ("Clear", 2), ("Previous", 3)],
            self.disposal_var
        )

        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=20)

        # Custom styled buttons
        select_button = tk.Button(
            buttons_frame,
            text="Select Folder",
            command=self.select_folder,
            bg="#3498DB",
            fg="#ECF0F1",
            relief="flat",
            padx=20,
            pady=10,
            font=("Helvetica", 12),
            activebackground="#2980B9",
            activeforeground="#ECF0F1"
        )
        select_button.pack(side=tk.LEFT, padx=5)

        help_button = tk.Button(
            buttons_frame,
            text="Help",
            command=self.show_help,
            bg="#3498DB",
            fg="#ECF0F1",
            relief="flat",
            padx=20,
            pady=10,
            font=("Helvetica", 12),
            activebackground="#2980B9",
            activeforeground="#ECF0F1"
        )
        help_button.pack(side=tk.LEFT, padx=5)

    def create_labeled_entry(self, parent, label_text, variable, row):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        tk.Label(
            frame,
            text=label_text,
            bg="#2C3E50",
            fg="#ECF0F1"
        ).pack(side=tk.LEFT, padx=5)

        entry = tk.Entry(
            frame,
            textvariable=variable,
            bg="#34495E",
            fg="#ECF0F1",
            insertbackground="#ECF0F1",
            relief="flat",
            bd=1
        )
        entry.pack(side=tk.LEFT, padx=5, pady=5)

    def create_radio_group(self, parent, label_text, options, variable):
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        tk.Label(
            frame,
            text=label_text,
            bg="#2C3E50",
            fg="#ECF0F1"
        ).pack(anchor=tk.W)

        for text, value in options:
            radio = tk.Radiobutton(
                frame,
                text=text,
                variable=variable,
                value=value,
                bg="#2C3E50",
                fg="#ECF0F1",
                selectcolor="#34495E",
                activebackground="#2C3E50",
                activeforeground="#ECF0F1"
            )
            radio.pack(anchor=tk.W, padx=20)

    def validate_inputs(self):
        try:
            frame_rate = int(self.frame_rate.get())
            colors = int(self.colors.get())
            resize = float(self.resize_factor.get())

            if not (1 <= frame_rate <= 1000):
                raise ValueError("Frame rate must be between 1 and 1000 ms")
            if not (2 <= colors <= 256):
                raise ValueError("Colors must be between 2 and 256")
            if not (0.1 <= resize <= 1.0):
                raise ValueError("Resize factor must be between 0.1 and 1.0")

            return True
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))
            return False

    def select_folder(self):
        if not self.validate_inputs():
            return

        folder_path = filedialog.askdirectory()
        if folder_path:
            Thread(target=self.convert_to_gif, args=(
                folder_path,), daemon=True).start()

    def convert_to_gif(self, folder_path):
        progress = ProgressWindow(self.root)

        try:
            # Get and sort image paths
            progress.update_progress(0, "Finding images...")
            image_paths = sorted([
                os.path.join(folder_path, filename)
                for filename in os.listdir(folder_path)
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))
            ])

            if not image_paths:
                messagebox.showwarning(
                    "No Images", "No compatible images found in the selected folder.")
                return

            frames = []
            total_images = len(image_paths)

            for i, file in enumerate(image_paths):
                progress.update_progress(
                    (i / total_images) * 100,
                    f"Processing image {i + 1} of {total_images}"
                )

                with Image.open(file) as img:
                    # Process image
                    img = self.process_image(img)
                    frames.append(img)

            progress.update_progress(90, "Saving GIF...")

            # Save dialog
            save_path = filedialog.asksaveasfilename(
                defaultextension=".gif",
                filetypes=[("GIF files", "*.gif")]
            )

            if save_path:
                self.save_gif(frames, save_path)
                messagebox.showinfo("Success", "GIF created successfully!")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            progress.window.destroy()

    def process_image(self, img):
        # Resize if needed
        resize_factor = float(self.resize_factor.get())
        if resize_factor != 1.0:
            img = img.resize(
                (int(img.width * resize_factor),
                 int(img.height * resize_factor)),
                Image.Resampling.LANCZOS
            )

        # Convert to RGBA
        img = img.convert('RGBA')

        # Process transparency
        img_array = np.array(img)
        if img_array.shape[2] == 4:
            alpha = img_array[:, :, 3].astype(float) / 255.0
            for i in range(3):
                img_array[:, :, i] = (img_array[:, :, i].astype(
                    float) * alpha).astype(np.uint8)
            img_array[:, :, 3] = (alpha * 255).astype(np.uint8)

        # Convert back to PIL and quantize
        img = Image.fromarray(img_array)
        return img.quantize(
            colors=int(self.colors.get()),
            method=2,
            dither=self.dither_var.get()
        )

    def save_gif(self, frames, save_path):
        frames[0].save(
            save_path,
            save_all=True,
            append_images=frames[1:],
            duration=int(self.frame_rate.get()),
            loop=0,
            disposal=self.disposal_var.get(),
            transparency=0,
            optimize=True,
            lossy=self.lossy_var.get()
        )

    def show_help(self):
        help_text = """
GIF Maker with Smooth Transparency Help:

1. Select a folder containing image files (PNG, JPG, JPEG, BMP, TIFF)
2. Configure options:
   - Frame Rate: Time between frames (ms)
   - Colors: Number of colors in output (2-256)
   - Resize Factor: Scale images (0.1-1.0)
   - Lossy Compression: Reduce file size
   - Dithering: Improve color transitions
   - Frame Disposal: How frames are replaced

3. Click 'Select Folder' to process
4. Choose where to save the resulting GIF

Tips:
- Use PNG files with transparency for best results
- Lower frame rates mean slower animation
- More colors = better quality but larger file
- Enable dithering for smoother gradients
"""
        messagebox.showinfo("Help", help_text)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = GIFMaker()
    app.run()
