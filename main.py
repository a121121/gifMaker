import tkinter as tk
from tkinter import filedialog
from PIL import Image
import os
import imageio


def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        convert_to_gif(folder_path)


def convert_to_gif(folder_path):
    image_paths = [os.path.join(folder_path, filename) for filename in os.listdir(
        folder_path) if filename.lower().endswith(('.jpg', '.jpeg', '.png'))]

    if not image_paths:
        print("No image files found in the selected folder.")
        return

    image_list = [Image.open(file).convert("RGBA") for file in image_paths]

    # Set the frame rate (adjust as needed)
    frame_rate = 25  # 30 frames per second

    # Create an empty list to hold the final animation frames
    animation_frames = []

    # Calculate the frame duration based on frame rate
    frame_duration = int(1000 / frame_rate)  # milliseconds

    for image in image_list:
        # Append the resized image to the animation_frames list
        animation_frames.append(image)

    # Save the images as an animated GIF without stacking
    first_frame = animation_frames[0]
    animation_frames = animation_frames[1:]

    # Allow user to choose the name and location for saving the GIF
    save_path = filedialog.asksaveasfilename(
        defaultextension=".gif", filetypes=[("GIF files", "*.gif")])

    if save_path:
        # Save the frames as an animated GIF
        first_frame.save(
            save_path,
            save_all=True,
            append_images=animation_frames,
            duration=frame_duration,
            loop=0,
            disposal=2  # Clear previous frame
        )
        print("Animation GIF created successfully!")

    root.destroy()  # Close the GUI


# Create the GUI
root = tk.Tk()
root.title("GIF Maker")

# Set the background color to dark
root.configure(bg="#2C3E50")

# Heading label
heading_label = tk.Label(root, text="GIF Maker", font=(
    "Helvetica", 20, "bold"), fg="#ECF0F1", bg="#2C3E50")
heading_label.pack(pady=20)

# Instructions
instructions = """
Instructions
1. Select the folder with your PNG sequence and see the magic happen.
"""
instructions_label = tk.Label(root, text=instructions, font=(
    "Helvetica", 12), fg="#ECF0F1", bg="#2C3E50", justify="left")
instructions_label.pack()

# Select Folder button
select_button = tk.Button(root, text="Select Folder", command=select_folder, font=(
    "Helvetica", 12), fg="#ECF0F1", bg="#3498DB")
select_button.pack(pady=20)

# Contact information
contact_label = tk.Label(root, text="For queries contact: younas.121.121@gmail.com",
                         font=("Helvetica", 10), fg="#ECF0F1", bg="#2C3E50")
contact_label.pack(pady=10)

root.mainloop()
