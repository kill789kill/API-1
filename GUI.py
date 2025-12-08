import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import os

# Set appearance
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ImageProcessor(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Image processor")
        self.geometry("1000x700")
        
        # Variables
        self.original_image = None
        self.current_image = None
        self.file_path = None
        self.orig_photo = None  # Store PhotoImage references
        self.curr_photo = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Left sidebar for controls
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        # Configure sidebar grid rows properly
        for i in range(14):  # At the moment up to 14 rows
            self.sidebar.grid_rowconfigure(i, weight=0)
        
        # Logo/Title 
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="Image Processor", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        # File controls 
        self.file_label = ctk.CTkLabel(self.sidebar, text="File Operations", font=ctk.CTkFont(weight="bold"))
        self.file_label.grid(row=1, column=0, padx=20, pady=(10, 0))
        
        self.load_btn = ctk.CTkButton(
            self.sidebar, 
            text="Load Image", 
            command=self.load_image
        )
        self.load_btn.grid(row=2, column=0, padx=20, pady=5)
        
        self.save_btn = ctk.CTkButton(
            self.sidebar, 
            text="Save Image", 
            command=self.save_image,
            state="disabled"
        )
        self.save_btn.grid(row=3, column=0, padx=20, pady=5)
        
        self.reset_btn = ctk.CTkButton(
            self.sidebar, 
            text="Reset", 
            command=self.reset_image,
            state="disabled"
        )
        self.reset_btn.grid(row=4, column=0, padx=20, pady=5)

        
        
        # Filters 
        self.filter_label = ctk.CTkLabel(self.sidebar, text="Filters", font=ctk.CTkFont(weight="bold"))
        self.filter_label.grid(row=5, column=0, padx=20, pady=(20, 0))
        
        self.grayscale_btn = ctk.CTkButton(
            self.sidebar, 
            text="Grayscale", 
            command=self.apply_grayscale,
            state="disabled"
        )
        self.grayscale_btn.grid(row=6, column=0, padx=20, pady=5)

        
        self.edge_btn = ctk.CTkButton(
            self.sidebar, 
            text="Edge Enhance", 
            command=self.apply_edge,
            state="disabled"
        )
        self.edge_btn.grid(row=7, column=0, padx=20, pady=5)
        
        self.blur_btn = ctk.CTkButton(
            self.sidebar, 
            text="Blur", 
            command=self.apply_blur,
            state="disabled"
        )
        self.blur_btn.grid(row=8, column=0, padx=20, pady=5)  # FIXED: Changed from row 8 to row 8
        
        # Add empty space at bottom
        self.sidebar.grid_rowconfigure(13, weight=1)
        
        # Right panel for images and sliders
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)
        
        # Sliders frame
        self.sliders_frame = ctk.CTkFrame(self.main_frame)
        self.sliders_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        self.sliders_frame.grid_columnconfigure(1, weight=1)
        
        # Brightness slider
        self.brightness_label = ctk.CTkLabel(self.sliders_frame, text="Brightness:")
        self.brightness_label.grid(row=0, column=0, padx=10, pady=5)
        
        self.brightness_slider = ctk.CTkSlider(
            self.sliders_frame,
            from_=0.1,
            to=3.0,
            number_of_steps=30,
            command=self.update_image_sliders
        )
        self.brightness_slider.set(1.0)
        self.brightness_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        self.brightness_value = ctk.CTkLabel(self.sliders_frame, text="1.0")
        self.brightness_value.grid(row=0, column=2, padx=10, pady=5)
        
        # Contrast slider
        self.contrast_label = ctk.CTkLabel(self.sliders_frame, text="Contrast:")
        self.contrast_label.grid(row=1, column=0, padx=10, pady=5)
        
        self.contrast_slider = ctk.CTkSlider(
            self.sliders_frame,
            from_=0.1,
            to=3.0,
            number_of_steps=30,
            command=self.update_image_sliders
        )
        self.contrast_slider.set(1.0)
        self.contrast_slider.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        
        self.contrast_value = ctk.CTkLabel(self.sliders_frame, text="1.0")
        self.contrast_value.grid(row=1, column=2, padx=10, pady=5)
        
        # Images frame
        self.images_frame = ctk.CTkFrame(self.main_frame)
        self.images_frame.grid(row=1, column=0, sticky="nsew", pady=(0, 20))
        self.images_frame.grid_columnconfigure((0, 1), weight=1)
        self.images_frame.grid_rowconfigure(1, weight=1)  # Allow row 1 to expand
        
        # Original image section
        self.original_label = ctk.CTkLabel(self.images_frame, text="Original Image", font=ctk.CTkFont(weight="bold"))
        self.original_label.grid(row=0, column=0, padx=10, pady=5)
        
        # Original image frame
        self.original_frame = ctk.CTkFrame(self.images_frame)
        self.original_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.original_frame.grid_propagate(False)  # Prevent frame from resizing to fit canvas
        
        self.original_canvas = tk.Canvas(self.original_frame, width=400, height=300, bg="#2b2b2b", highlightthickness=0)
        self.original_canvas.pack(expand=True, fill="both")  # Center in frame
        
        # Processed image section
        self.processed_label = ctk.CTkLabel(self.images_frame, text="Processed Image", font=ctk.CTkFont(weight="bold"))
        self.processed_label.grid(row=0, column=1, padx=10, pady=5)
        
        self.processed_frame = ctk.CTkFrame(self.images_frame)
        self.processed_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        self.processed_frame.grid_propagate(False)
        
        self.processed_canvas = tk.Canvas(self.processed_frame, width=400, height=300, bg="#2b2b2b", highlightthickness=0)
        self.processed_canvas.pack(expand=True, fill="both")  # Center in frame
        
        # File info
        self.info_label = ctk.CTkLabel(self.main_frame, text="No image loaded")
        self.info_label.grid(row=2, column=0, sticky="sw")
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.file_path = file_path
                self.original_image = Image.open(file_path)
                self.current_image = self.original_image.copy()
                
                # Update UI
                self.update_image_displays()
                self.save_btn.configure(state="normal")
                self.reset_btn.configure(state="normal")
                self.grayscale_btn.configure(state="normal")
                self.edge_btn.configure(state="normal")
                self.blur_btn.configure(state="normal")
                
                # Update info
                filename = os.path.basename(file_path)
                size = self.original_image.size
                self.info_label.configure(
                    text=f"Loaded: {filename} | Size: {size[0]}x{size[1]}"
                )
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")
    
    def update_image_displays(self):
        if self.original_image and self.current_image:
            # Clear canvases first
            self.original_canvas.delete("all")
            self.processed_canvas.delete("all")
            
            # Get display dimensions from frame (not canvas)
            frame_width = self.original_frame.winfo_width()
            frame_height = self.original_frame.winfo_height()
            
            # Use actual frame size if available, otherwise default
            if frame_width <= 1 or frame_height <= 1:
                frame_width, frame_height = 400, 300
            
            # Resize images to fit frames while maintaining aspect ratio
            orig_display = self.resize_for_display(self.original_image, (frame_width, frame_height))
            curr_display = self.resize_for_display(self.current_image, (frame_width, frame_height))
            
            # Convert to PhotoImage
            self.orig_photo = ImageTk.PhotoImage(orig_display)
            self.curr_photo = ImageTk.PhotoImage(curr_display)
            
            # Calculate center position
            orig_x = (frame_width - orig_display.width) // 2
            orig_y = (frame_height - orig_display.height) // 2
            
            curr_x = (frame_width - curr_display.width) // 2
            curr_y = (frame_height - curr_display.height) // 2
            
            # Update canvases (centered)
            self.original_canvas.create_image(orig_x, orig_y, image=self.orig_photo, anchor="nw")
            self.processed_canvas.create_image(curr_x, curr_y, image=self.curr_photo, anchor="nw")
            
            # Update slider values
            self.brightness_value.configure(text=f"{self.brightness_slider.get():.1f}")
            self.contrast_value.configure(text=f"{self.contrast_slider.get():.1f}")
    
    def resize_for_display(self, image, max_size):
        """Resize image for display maintaining aspect ratio"""
        if not image:
            return None
            
        img = image.copy()
        
        # Calculate aspect ratio
        img_ratio = img.width / img.height
        max_ratio = max_size[0] / max_size[1]
        
        if img_ratio > max_ratio:
            # Image is wider than frame
            new_width = max_size[0]
            new_height = int(max_size[0] / img_ratio)
        else:
            # Image is taller than frame
            new_height = max_size[1]
            new_width = int(max_size[1] * img_ratio)
        
        # Resize if needed
        if new_width < img.width or new_height < img.height:
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
    
    def update_image_sliders(self, *args):
        if self.original_image:
            brightness = self.brightness_slider.get()
            contrast = self.contrast_slider.get()
            
            # Update displayed values
            self.brightness_value.configure(text=f"{brightness:.1f}")
            self.contrast_value.configure(text=f"{contrast:.1f}")
            
            # Apply adjustments
            self.current_image = self.original_image.copy()
            
            enhancer = ImageEnhance.Brightness(self.current_image)
            self.current_image = enhancer.enhance(brightness)
            
            enhancer = ImageEnhance.Contrast(self.current_image)
            self.current_image = enhancer.enhance(contrast)
            
            self.update_image_displays()
    
    def apply_grayscale(self):
        if self.current_image:
            self.current_image = self.current_image.convert('L').convert('RGB')
            self.update_image_displays()
    
    def apply_invert(self):
        if self.current_image:
            # Convert to numpy array, invert, convert back
            import numpy as np
            img_array = np.array(self.current_image)
            inverted = 255 - img_array
            self.current_image = Image.fromarray(inverted)
            self.update_image_displays()
    
    def apply_edge(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.EDGE_ENHANCE)
            self.update_image_displays()
    
    def apply_blur(self):
        if self.current_image:
            self.current_image = self.current_image.filter(ImageFilter.GaussianBlur(2))
            self.update_image_displays()
    
    def reset_image(self):
        if self.original_image:
            self.current_image = self.original_image.copy()
            self.brightness_slider.set(1.0)
            self.contrast_slider.set(1.0)
            self.update_image_displays()
    
    def save_image(self):
        if self.current_image and self.file_path:
            save_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg"),
                    ("All files", "*.*")
                ]
            )
            
            if save_path:
                try:
                    self.current_image.save(save_path)
                    messagebox.showinfo("Success", f"Image saved to:\n{save_path}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {e}")

if __name__ == "__main__":
    app = ImageProcessor()
    app.mainloop()