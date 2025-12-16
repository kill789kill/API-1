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
        self.n_frames = 1
        self.current_frame_index = 0
        
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

        # 3D view for multi-page TIFFs
        self.view3d_btn = ctk.CTkButton(
            self.sidebar,
            text="3D View",
            command=self.show_3d_view,
            state="disabled"
        )
        self.view3d_btn.grid(row=9, column=0, padx=20, pady=5)

        self.exportpc_btn = ctk.CTkButton(
            self.sidebar,
            text="Export PC",
            command=self.export_pointcloud,
            state="disabled"
        )
        self.exportpc_btn.grid(row=10, column=0, padx=20, pady=5)
        
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

        # Page controls for multi-page TIFFs (hidden unless needed)
        # Place the page controls under the original image frame
        self.page_controls_frame = ctk.CTkFrame(self.original_frame)
        self.page_label = ctk.CTkLabel(self.page_controls_frame, text="Page: 1/1")
        self.page_label.pack(side="left", padx=8)
        self.page_slider = ctk.CTkSlider(
            self.page_controls_frame,
            from_=1,
            to=1,
            number_of_steps=0,
            command=self.change_frame
        )
        self.page_slider.pack(side="left", fill="x", expand=True, padx=8, pady=6)
        self.page_controls_frame.pack_forget()
        
        # File info
        self.info_label = ctk.CTkLabel(self.main_frame, text="No image loaded")
        self.info_label.grid(row=2, column=0, sticky="sw")
    
    def load_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.file_path = file_path
                self.original_image = Image.open(file_path)

                # Detect multi-frame images (TIFF pages)
                try:
                    self.n_frames = getattr(self.original_image, "n_frames", 1)
                except Exception:
                    self.n_frames = 1

                self.current_frame_index = 0

                # Set current image to the first frame
                self.current_image = self.get_frame_image(self.original_image, self.current_frame_index)
                
                # Update UI
                self.update_page_controls()
                self.update_image_displays()
                self.save_btn.configure(state="normal")
                self.reset_btn.configure(state="normal")
                self.grayscale_btn.configure(state="normal")
                self.edge_btn.configure(state="normal")
                self.blur_btn.configure(state="normal")
                # enable 3D view for multi-frame images
                try:
                    if getattr(self, 'n_frames', 1) > 1:
                        self.view3d_btn.configure(state='normal')
                        self.exportpc_btn.configure(state='normal')
                    else:
                        self.view3d_btn.configure(state='disabled')
                        self.exportpc_btn.configure(state='disabled')
                except Exception:
                    pass
                
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
            
            # For multi-frame images, get the selected original frame for display
            orig_base = self.get_frame_image(self.original_image, self.current_frame_index)

            # Resize images to fit frames while maintaining aspect ratio
            orig_display = self.resize_for_display(orig_base, (frame_width, frame_height))
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
            
            # Apply adjustments using the selected original frame as base
            base = self.get_frame_image(self.original_image, self.current_frame_index)
            self.current_image = base.copy()

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

    def get_frame_image(self, image, index):
        """Return a copy of the requested frame (page) from a possibly multi-frame image."""
        if not image:
            return None

        # Default single-frame
        try:
            n = getattr(image, "n_frames", 1)
        except Exception:
            n = 1

        if n <= 1:
            return image.copy()

        # Clamp index
        if index < 0:
            index = 0
        if index >= n:
            index = n - 1

        try:
            image.seek(index)
            frame = image.copy()
            # Optionally reset to first frame
            image.seek(0)
            return frame
        except Exception:
            # Fallback to returning a copy of the original
            try:
                image.seek(0)
            except Exception:
                pass
            return image.copy()

    def update_page_controls(self):
        """Show or hide page slider depending on number of frames."""
        if self.n_frames and self.n_frames > 1:
            # configure slider range and steps
            self.page_label.configure(text=f"Page: {self.current_frame_index+1}/{self.n_frames}")
            self.page_slider.configure(from_=1, to=self.n_frames, number_of_steps=max(0, self.n_frames-1))
            self.page_slider.set(self.current_frame_index + 1)
            self.page_controls_frame.pack(side="bottom", fill="x")
        else:
            self.page_controls_frame.pack_forget()

    def change_frame(self, val):
        """Callback when the page slider is moved."""
        try:
            page = int(round(float(val))) - 1
        except Exception:
            page = 0

        if page < 0:
            page = 0
        if page >= self.n_frames:
            page = self.n_frames - 1

        self.current_frame_index = page
        # Load the selected frame and reapply sliders
        base = self.get_frame_image(self.original_image, self.current_frame_index)
        self.current_image = base.copy()
        # Reapply brightness/contrast currently set
        self.update_image_sliders()
        # Update page label
        self.page_label.configure(text=f"Page: {self.current_frame_index+1}/{self.n_frames}")

    def _extract_tiff_spacings(self, image):
        """Try to read X/Y/Z spacings from TIFF tags or image info. Returns (dx,dy,dz)."""
        dx = dy = dz = 1.0
        try:
            tag = getattr(image, 'tag_v2', None)
            if tag is not None:
                xr = tag.get(282)
                yr = tag.get(283)
                if xr:
                    try:
                        dx = 1.0 / (xr[0] / xr[1]) if isinstance(xr, tuple) and xr[1] else 1.0 / float(xr)
                    except Exception:
                        pass
                if yr:
                    try:
                        dy = 1.0 / (yr[0] / yr[1]) if isinstance(yr, tuple) and yr[1] else 1.0 / float(yr)
                    except Exception:
                        pass
                desc = tag.get(270) or image.info.get('ImageDescription') or image.info.get('description')
                if desc:
                    try:
                        import re
                        m = re.search(r"z[_-]?spacing\s*[:=]\s*([0-9.+-eE]+)", str(desc))
                        if m:
                            dz = float(m.group(1))
                    except Exception:
                        pass
            if 'resolution' in image.info and (dx == 1.0 and dy == 1.0):
                try:
                    r = image.info.get('resolution')
                    if isinstance(r, tuple) and r[0]:
                        dx = dy = 1.0 / float(r[0])
                except Exception:
                    pass
        except Exception:
            pass
        return dx, dy, dz
    def build_pointcloud(self, max_points=50000, threshold_factor=0.15):
        """Build point cloud arrays (xs, ys, zs, colors) from the loaded TIFF.

        Returns (xs, ys, zs, cols) as numpy arrays, or (None, None, None, None) on failure.
        """
        try:
            import numpy as np
        except Exception:
            messagebox.showerror('Missing deps', 'Install numpy to use export/view features (pip install numpy)')
            return None, None, None, None

        if not self.original_image:
            messagebox.showinfo('No image', 'Load a multi-page TIFF first')
            return None, None, None, None

        n_frames = getattr(self.original_image, 'n_frames', 1)
        if not n_frames or n_frames <= 0:
            return None, None, None, None

        first = self.get_frame_image(self.original_image, 0)
        arr0 = np.array(first)
        channel_count = 1
        per_frame_has_channels = False
        if arr0.ndim == 3 and arr0.shape[2] >= 3:
            channel_count = arr0.shape[2]
            per_frame_has_channels = True
        else:
            try:
                tag = getattr(self.original_image, 'tag_v2', None)
                s = None
                if tag is not None:
                    s = tag.get(277)
                if s:
                    try:
                        channel_count = int(s)
                    except Exception:
                        pass
            except Exception:
                pass

        if channel_count == 1 and n_frames % 3 == 0:
            channel_count = 3
        elif channel_count == 1 and n_frames % 2 == 0:
            channel_count = 2

        stacks = []
        if per_frame_has_channels:
            for c in range(channel_count):
                stacks.append([])
            for i in range(n_frames):
                fr = self.get_frame_image(self.original_image, i)
                arr = np.array(fr)
                if arr.ndim == 2:
                    stacks[0].append(arr)
                else:
                    for c in range(channel_count):
                        if c < arr.shape[2]:
                            stacks[c].append(arr[:, :, c])
                        else:
                            stacks[c].append(np.zeros(arr.shape[:2], dtype=arr.dtype))
        else:
            if n_frames % channel_count != 0:
                stacks = [[np.array(self.get_frame_image(self.original_image, i).convert('L')) for i in range(n_frames)]]
                channel_count = 1
            else:
                z_count = n_frames // channel_count
                for c in range(channel_count):
                    stacks.append([])
                for z in range(z_count):
                    for c in range(channel_count):
                        idx = z * channel_count + c
                        fr = self.get_frame_image(self.original_image, idx)
                        arr = np.array(fr)
                        if arr.ndim == 3:
                            stacks[c].append(arr[:, :, 0])
                        else:
                            stacks[c].append(arr)

        for i in range(len(stacks)):
            try:
                stacks[i] = np.stack(stacks[i], axis=0)
            except Exception:
                stacks[i] = np.zeros((1, 1, 1), dtype=np.uint8)

        dx, dy, dz = self._extract_tiff_spacings(self.original_image)

        base_colors = [(1,0,0), (0,1,0), (0,0,1), (1,0,1), (1,0.5,0), (0,1,1)]

        xs_all = []
        ys_all = []
        zs_all = []
        cols_all = []
        for c, stack in enumerate(stacks):
            if stack.size == 0:
                continue
            thr = max(stack.max() * threshold_factor, 1)
            zs, ys, xs = np.where(stack > thr)
            if zs.size == 0:
                continue
            # downsample channel points if too many
            if zs.size > max_points:
                idx = np.random.choice(np.arange(zs.size), size=max_points, replace=False)
                zs = zs[idx]; ys = ys[idx]; xs = xs[idx]
            xs_all.append(xs * dx)
            ys_all.append(ys * dy)
            zs_all.append(zs * dz)
            if c < len(base_colors):
                color = np.array(base_colors[c])
                cols_all.append(np.tile(color, (xs.size,1)))
            else:
                import matplotlib.cm as cm
                cmap = cm.get_cmap('tab10')
                color = cmap(c % 10)[:3]
                cols_all.append(np.tile(color, (xs.size,1)))

        if not xs_all:
            return None, None, None, None

        import numpy as _np
        xs_all = _np.concatenate(xs_all)
        ys_all = _np.concatenate(ys_all)
        zs_all = _np.concatenate(zs_all)
        cols_all = _np.vstack(cols_all)
        return xs_all, ys_all, zs_all, cols_all

    def show_3d_view(self):
        # Prefer a fast OpenGL viewer via vispy, fallback to matplotlib
        xs, ys, zs, cols = self.build_pointcloud()
        if xs is None:
            messagebox.showinfo('Empty', 'No significant points found to render')
            return

        # Try vispy first (fast GPU-backed rendering)
        try:
            from vispy import scene, app
            from vispy.scene import visuals
            import numpy as _np
        except Exception:
            # Fall back to matplotlib embedded in Tk
            try:
                import matplotlib.pyplot as plt
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            except Exception:
                messagebox.showerror('Missing deps', 'Install vispy or matplotlib to use 3D view (pip install vispy matplotlib)')
                return

            try:
                win = tk.Toplevel(self)
                win.title('3D View')
                fig = plt.Figure(figsize=(7,6))
                ax = fig.add_subplot(111, projection='3d')
                ax.scatter(xs, ys, zs, c=cols, s=1)
                ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
                canvas = FigureCanvasTkAgg(fig, master=win)
                canvas.draw()
                canvas.get_tk_widget().pack(expand=True, fill='both')
            except Exception as e:
                messagebox.showerror('3D error', f'Failed to show 3D view: {e}')
            return

        # Use vispy for interactive OpenGL rendering
        try:
            pts = _np.vstack((xs, ys, zs)).T.astype(_np.float32)
            colors = cols.astype(_np.float32)

            canvas = scene.SceneCanvas(keys='interactive', show=True, bgcolor='white', size=(800, 600))
            view = canvas.central_widget.add_view()
            scatter = visuals.Markers()
            scatter.set_data(pts, face_color=colors, size=2, edge_color=None)
            view.add(scatter)
            # compute bounds and center for camera and helpers
            xmin, xmax = float(_np.min(xs)), float(_np.max(xs))
            ymin, ymax = float(_np.min(ys)), float(_np.max(ys))
            zmin, zmax = float(_np.min(zs)), float(_np.max(zs))
            cx = (xmin + xmax) / 2.0
            cy = (ymin + ymax) / 2.0
            cz = (zmin + zmax) / 2.0
            max_range = max(xmax - xmin, ymax - ymin, zmax - zmin)

            # use a TurntableCamera centered on the cloud
            view.camera = scene.cameras.TurntableCamera(fov=45, center=(cx, cy, cz), up='+y')

            # add an XYZ axis widget placed at the cloud center
            try:
                axis = visuals.XYZAxis(parent=view.scene)
                axis.transform = scene.transforms.MatrixTransform()
                axis.transform.translate((cx, cy, cz))
            except Exception:
                pass

            # grid in XY plane at zmin for reference
            try:
                grid = visuals.GridLines(color=(0.6, 0.6, 0.6, 0.4), parent=view.scene)
                grid.transform = scene.transforms.MatrixTransform()
                grid.transform.translate((cx, cy, zmin))
            except Exception:
                pass

            # axis labels at ends
            try:
                tx = visuals.Text('X', color='red', pos=(xmax, cy, cz), parent=view.scene, font_size=12)
                ty = visuals.Text('Y', color='green', pos=(cx, ymax, cz), parent=view.scene, font_size=12)
                tz = visuals.Text('Z', color='blue', pos=(cx, cy, zmax), parent=view.scene, font_size=12)
            except Exception:
                pass

            canvas.app.process_events()
        except Exception as e:
            messagebox.showerror('3D error', f'Vispy failed to render point cloud: {e}')

    def export_pointcloud(self):
        """Export the built point cloud to a PLY (ASCII) file with per-vertex RGB."""
        try:
            import numpy as np
        except Exception:
            messagebox.showerror('Missing deps', 'Install numpy to export point clouds (pip install numpy)')
            return

        xs, ys, zs, cols = self.build_pointcloud(max_points=200000)
        if xs is None:
            messagebox.showinfo('Empty', 'No significant points found to export')
            return

        save_path = filedialog.asksaveasfilename(defaultextension='.ply', filetypes=[('PLY files', '*.ply'), ('All files','*.*')])
        if not save_path:
            return

        try:
            # ensure cols in 0-255 integers
            cols_int = (np.clip(cols, 0.0, 1.0) * 255).astype(np.uint8)
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write('ply\n')
                f.write('format ascii 1.0\n')
                f.write(f'element vertex {xs.size}\n')
                f.write('property float x\n')
                f.write('property float y\n')
                f.write('property float z\n')
                f.write('property uchar red\n')
                f.write('property uchar green\n')
                f.write('property uchar blue\n')
                f.write('end_header\n')
                for xi, yi, zi, col in zip(xs, ys, zs, cols_int):
                    f.write(f'{float(xi)} {float(yi)} {float(zi)} {int(col[0])} {int(col[1])} {int(col[2])}\n')
            messagebox.showinfo('Exported', f'Point cloud exported to:\n{save_path}')
        except Exception as e:
            messagebox.showerror('Export error', f'Failed to export point cloud: {e}')

if __name__ == "__main__":
    app = ImageProcessor()
    app.mainloop()