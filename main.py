import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image
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

        # Center the window
        self.window.geometry("+%d+%d" % (
            parent.winfo_rootx() + parent.winfo_width()/2 - 150,
            parent.winfo_rooty() + parent.winfo_height()/2 - 75))

        # Progress bar
        self.progress = ttk.Progressbar(
            self.window, length=200, mode='determinate')
        self.progress.pack(pady=20)

        # Status label
        self.status = tk.Label(self.window, text="Starting...")
        self.status.pack(pady=10)

        # Log text
        self.log = tk.Text(self.window, height=3, width=35)
        self.log.pack(pady=10)

    def update(self, value, status):
        self.progress['value'] = value
        self.status['text'] = status
        self.log.insert(tk.END, f"{status}\n")
        self.log.see(tk.END)
        self.window.update()


def preserve_alpha(img_array):
    """Preserve full alpha channel range and clean edges"""
    if img_array.shape[2] == 4:  # Ensure we have an alpha channel
        # Get alpha channel
        alpha = img_array[:, :, 3].astype(float) / 255.0

        # Apply alpha to RGB channels
        for i in range(3):
            img_array[:, :, i] = (img_array[:, :, i].astype(
                float) * alpha).astype(np.uint8)

        # Convert alpha back to uint8
        img_array[:, :, 3] = (alpha * 255).astype(np.uint8)

    return img_array


def convert_to_gif(folder_path, root):
    # Create progress window
    progress = ProgressWindow(root)

    try:
        # Get and sort image paths
        progress.update(0, "Finding images...")
        image_paths = sorted([
            os.path.join(folder_path, filename)
            for filename in os.listdir(folder_path)
            if filename.lower().endswith(('.png', '.jpg', '.jpeg'))
        ])

        if not image_paths:
            progress.update(100, "No images found!")
            return

        # Process images
        frames = []
        total_images = len(image_paths)

        for i, file in enumerate(image_paths):
            progress.update(
                (i / total_images) * 100,
                f"Processing image {i+1} of {total_images}"
            )

            # Open and convert image to RGBA
            with Image.open(file) as img:
                # Convert to RGBA while preserving alpha values
                img = img.convert('RGBA')

                # Convert to numpy array for processing
                img_array = np.array(img)

                # Process alpha
                img_array = preserve_alpha(img_array)

                # Convert back to PIL Image
                processed_img = Image.fromarray(img_array)

                # Ensure alpha channel is preserved in quantization
                processed_img = processed_img.quantize(method=2,  # Fast Octree
                                                       colors=255,  # Reserve one color for transparency
                                                       dither=Image.Dither.NONE)

                frames.append(processed_img)

        progress.update(90, "Saving GIF...")

        # Save GIF
        save_path = filedialog.asksaveasfilename(
            defaultextension=".gif",
            filetypes=[("GIF files", "*.gif")]
        )

        if save_path:
            frames[0].save(
                save_path,
                save_all=True,
                append_images=frames[1:],
                duration=40,  # 25 fps
                loop=0,
                disposal=2,  # Clear previous frame
                transparency=0,  # Transparent color index
                optimize=False  # Disable optimization to preserve transparency
            )
            progress.update(100, "GIF created successfully!")
            time.sleep(2)

    except Exception as e:
        progress.update(100, f"Error: {str(e)}")
        time.sleep(3)
    finally:
        progress.window.destroy()
        root.destroy()


def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        Thread(target=convert_to_gif, args=(
            folder_path, root), daemon=True).start()


# Create the GUI
root = tk.Tk()
root.title("GIF Maker with Smooth Transparency")

# Set the background color to dark
root.configure(bg="#2C3E50")

# Heading label
heading_label = tk.Label(
    root,
    text="GIF Maker with Smooth Transparency",
    font=("Helvetica", 20, "bold"),
    fg="#ECF0F1",
    bg="#2C3E50"
)
heading_label.pack(pady=20)

# Instructions
instructions = """
Instructions:
1. Select the folder containing your PNG sequence
2. Alpha values will be preserved (0-255)
3. Progress will be shown during processing
4. Output will be a transparent GIF with smooth edges
"""

instructions_label = tk.Label(
    root,
    text=instructions,
    font=("Helvetica", 12),
    fg="#ECF0F1",
    bg="#2C3E50",
    justify="left"
)
instructions_label.pack()

# Select Folder button
select_button = tk.Button(
    root,
    text="Select Folder",
    command=select_folder,
    font=("Helvetica", 12),
    fg="#ECF0F1",
    bg="#3498DB"
)
select_button.pack(pady=20)

root.mainloop()
