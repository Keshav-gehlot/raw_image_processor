from PIL import Image
import rawpy
import imageio
import numpy as np
import cv2
import matplotlib.pyplot as plt
import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from pathlib import Path

def process_raw_image(input_path, output_path, sharpening_strength=1.5, blur_sigma=3, jpeg_quality=95, noise_reduction=0.0, saturation=1.0, contrast=1.0):
    """    Process a RAW image file to reduce blur using unsharp masking technique and enhance image quality.
    
    Args:
        input_path (str): Path to the input RAW image file
        output_path (str): Path to save the processed image
        sharpening_strength (float): Strength of sharpening effect (1.0 = no change)
        blur_sigma (int): Sigma value for Gaussian blur
        jpeg_quality (int): JPEG quality for output image (0-100, higher is better)
        noise_reduction (float): Strength of noise reduction (0 = none, 1.0 = strong)
        saturation (float): Color saturation adjustment (1.0 = no change)
        contrast (float): Contrast adjustment (1.0 = no change)
    
    Returns:
        str: Path to the output image if successful, None otherwise
    """
    try:
        # Check if input file exists
        if not os.path.exists(input_path):
            print(f"Error: Input file '{input_path}' does not exist.")
            return None
        
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Load the RAW image
        print(f"Processing RAW image: {input_path}")
        with rawpy.imread(input_path) as raw:
            # Process the RAW data to RGB
            rgb_image = raw.postprocess()
        
        # Convert to OpenCV format (BGR)
        image_bgr = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
        
        # Apply unsharp masking technique to reduce blur
        # Step 1: Gaussian blur
        blurred = cv2.GaussianBlur(image_bgr, (0, 0), sigmaX=blur_sigma)
        
        # Step 2: Sharpening
        # The formula is: sharpened = original + (original - blurred) * amount
        # which simplifies to: original * (1 + amount) - blurred * amount
        sharpened = cv2.addWeighted(image_bgr, 1.0 + sharpening_strength, 
                                   blurred, -sharpening_strength, 0)
        
        # Step 3: Apply noise reduction if enabled
        if noise_reduction > 0:
            # Apply non-local means denoising
            # h parameter controls filter strength (higher h = more filtering)
            h = noise_reduction * 10  # Scale the user parameter to an appropriate range
            sharpened = cv2.fastNlMeansDenoisingColored(sharpened, None, h, h, 7, 21)
        
        # Step 4: Apply color enhancements
        if saturation != 1.0 or contrast != 1.0:
            # Convert to HSV for saturation adjustment
            hsv = cv2.cvtColor(sharpened, cv2.COLOR_BGR2HSV).astype(np.float32)
            
            # Adjust saturation (S channel)
            if saturation != 1.0:
                hsv[:,:,1] = hsv[:,:,1] * saturation
                hsv[:,:,1] = np.clip(hsv[:,:,1], 0, 255)
            
            # Convert back to BGR
            enhanced = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            
            # Adjust contrast
            if contrast != 1.0:
                # Apply contrast adjustment formula: pixel = (pixel - 127.5) * contrast + 127.5
                enhanced = enhanced.astype(np.float32)
                enhanced = (enhanced - 127.5) * contrast + 127.5
                enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)
        else:
            enhanced = sharpened
            
        # Ensure we're not returning a grayscale image
        if len(enhanced.shape) == 2 or enhanced.shape[2] == 1:
            print("Warning: Image appears to be grayscale, converting to color")
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        
        # Save the enhanced image with specified JPEG quality
        cv2.imwrite(output_path, enhanced, [cv2.IMWRITE_JPEG_QUALITY, jpeg_quality])
        print(f"Processed image saved to: {output_path}")
        
        return output_path
    
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return None

class RawImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RAW Image Processor")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Set application icon and style
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Arial", 10))
        self.style.configure("TLabel", font=("Arial", 10))
        self.style.configure("Header.TLabel", font=("Arial", 12, "bold"))
        
        # Initialize variables
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.sharpening_strength = tk.DoubleVar(value=50)  # 1.5 on 0-3 scale = 50 on 0-100 scale
        self.blur_sigma = tk.IntVar(value=3)
        self.jpeg_quality = tk.IntVar(value=95)
        self.noise_reduction = tk.DoubleVar(value=30)  # 0.3 on 0-1 scale = 30 on 0-100 scale
        self.saturation = tk.DoubleVar(value=55)  # 1.1 on 0-2 scale = 55 on 0-100 scale
        self.contrast = tk.DoubleVar(value=55)  # 1.1 on 0-2 scale = 55 on 0-100 scale
        self.status_text = tk.StringVar(value="Ready")
        self.processing = False
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20 20 20 20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create file selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10 10 10 10")
        file_frame.pack(fill=tk.X, pady=10)
        
        # Input file selection
        ttk.Label(file_frame, text="Input RAW File:").grid(column=0, row=0, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.input_path, width=50).grid(column=1, row=0, sticky=tk.W, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_input_file).grid(column=2, row=0, sticky=tk.W)
        
        # Output file selection
        ttk.Label(file_frame, text="Output JPEG File:").grid(column=0, row=1, sticky=tk.W, pady=5)
        ttk.Entry(file_frame, textvariable=self.output_path, width=50).grid(column=1, row=1, sticky=tk.W, padx=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_output_file).grid(column=2, row=1, sticky=tk.W)
        
        # Create parameters frame
        params_frame = ttk.LabelFrame(main_frame, text="Image Processing Parameters", padding="10 10 10 10")
        params_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Sharpening strength
        ttk.Label(params_frame, text="Sharpening Strength:").grid(column=0, row=0, sticky=tk.W, pady=5)
        ttk.Scale(params_frame, from_=0.0, to=100.0, variable=self.sharpening_strength, length=300).grid(column=1, row=0, sticky=tk.W)
        self.sharpening_label = ttk.Label(params_frame, text=f"{self.sharpening_strength.get():.1f}")
        self.sharpening_label.grid(column=2, row=0, sticky=tk.W)
        
        # Blur sigma
        ttk.Label(params_frame, text="Blur Sigma:").grid(column=0, row=1, sticky=tk.W, pady=5)
        ttk.Scale(params_frame, from_=1, to=100, variable=self.blur_sigma, length=300).grid(column=1, row=1, sticky=tk.W)
        self.blur_label = ttk.Label(params_frame, text=str(self.blur_sigma.get()))
        self.blur_label.grid(column=2, row=1, sticky=tk.W)
        
        # JPEG quality
        ttk.Label(params_frame, text="JPEG Quality:").grid(column=0, row=2, sticky=tk.W, pady=5)
        ttk.Scale(params_frame, from_=50, to=100, variable=self.jpeg_quality, length=300).grid(column=1, row=2, sticky=tk.W)
        self.quality_label = ttk.Label(params_frame, text=str(self.jpeg_quality.get()))
        self.quality_label.grid(column=2, row=2, sticky=tk.W)
        
        # Noise reduction
        ttk.Label(params_frame, text="Noise Reduction:").grid(column=0, row=3, sticky=tk.W, pady=5)
        ttk.Scale(params_frame, from_=0.0, to=100.0, variable=self.noise_reduction, length=300).grid(column=1, row=3, sticky=tk.W)
        self.noise_label = ttk.Label(params_frame, text=f"{self.noise_reduction.get():.1f}")
        self.noise_label.grid(column=2, row=3, sticky=tk.W)
        
        # Saturation
        ttk.Label(params_frame, text="Saturation:").grid(column=0, row=4, sticky=tk.W, pady=5)
        ttk.Scale(params_frame, from_=0.0, to=100.0, variable=self.saturation, length=300).grid(column=1, row=4, sticky=tk.W)
        self.saturation_label = ttk.Label(params_frame, text=f"{self.saturation.get():.1f}")
        self.saturation_label.grid(column=2, row=4, sticky=tk.W)
        
        # Contrast
        ttk.Label(params_frame, text="Contrast:").grid(column=0, row=5, sticky=tk.W, pady=5)
        ttk.Scale(params_frame, from_=0.0, to=100.0, variable=self.contrast, length=300).grid(column=1, row=5, sticky=tk.W)
        self.contrast_label = ttk.Label(params_frame, text=f"{self.contrast.get():.1f}")
        self.contrast_label.grid(column=2, row=5, sticky=tk.W)
        
        # Create buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Process button
        self.process_button = ttk.Button(buttons_frame, text="Process Image", command=self.process_image)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        # Reset button
        ttk.Button(buttons_frame, text="Reset Parameters", command=self.reset_parameters).pack(side=tk.LEFT, padx=5)
        
        # View result button
        self.view_button = ttk.Button(buttons_frame, text="View Result", command=self.view_result, state=tk.DISABLED)
        self.view_button.pack(side=tk.LEFT, padx=5)
        
        # Status bar
        status_frame = ttk.Frame(main_frame, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        ttk.Label(status_frame, textvariable=self.status_text).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, orient=tk.HORIZONTAL, length=200, mode='indeterminate')
        self.progress.pack(side=tk.RIGHT, padx=5)
        
        # Store the last processed image path
        self.last_processed_image = None
        
        # Bind value display updates
        self.sharpening_strength.trace_add("write", self.update_value_labels)
        self.noise_reduction.trace_add("write", self.update_value_labels)
        self.saturation.trace_add("write", self.update_value_labels)
        self.contrast.trace_add("write", self.update_value_labels)
    
    def update_value_labels(self, *args):
        # Update all the value labels with current values
        try:
            self.sharpening_label.config(text=f"{self.sharpening_strength.get():.1f}")
            self.blur_label.config(text=str(self.blur_sigma.get()))
            self.quality_label.config(text=str(self.jpeg_quality.get()))
            self.noise_label.config(text=f"{self.noise_reduction.get():.1f}")
            self.saturation_label.config(text=f"{self.saturation.get():.1f}")
            self.contrast_label.config(text=f"{self.contrast.get():.1f}")
        except Exception as e:
            print(f"Error updating labels: {str(e)}")
            pass
    
    def browse_input_file(self):
        filetypes = [
            ("RAW Files", "*.CR2;*.CR3;*.NEF;*.ARW;*.RAF;*.ORF;*.RW2;*.DNG"),
            ("All Files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select RAW Image File", filetypes=filetypes)
        if filename:
            self.input_path.set(filename)
            # Auto-generate output path
            input_path = Path(filename)
            default_output = str(input_path.parent / f"{input_path.stem}_processed.jpg")
            self.output_path.set(default_output)
    
    def browse_output_file(self):
        filetypes = [("JPEG Files", "*.jpg;*.jpeg"), ("All Files", "*.*")]
        filename = filedialog.asksaveasfilename(title="Save Processed Image As", 
                                              filetypes=filetypes,
                                              defaultextension=".jpg")
        if filename:
            self.output_path.set(filename)
    def reset_parameters(self):
        # Set default values scaled to the 0-100 range
        self.sharpening_strength.set(50)  # 1.5 on 0-3 scale = 50 on 0-100 scale
        self.blur_sigma.set(3)  # Keep as is since it's an integer value
        self.jpeg_quality.set(95)  # Already on 0-100 scale
        self.noise_reduction.set(30)  # 0.3 on 0-1 scale = 30 on 0-100 scale
        self.saturation.set(55)  # 1.1 on 0-2 scale = 55 on 0-100 scale
        self.contrast.set(55)  # 1.1 on 0-2 scale = 55 on 0-100 scale
    
    def process_image(self):
        # Validate inputs
        if not self.input_path.get():
            messagebox.showerror("Error", "Please select an input RAW file.")
            return
        
        if not self.output_path.get():
            messagebox.showerror("Error", "Please specify an output file path.")
            return
        
        # Disable process button and start progress
        self.process_button.config(state=tk.DISABLED)
        self.progress.start(10)
        self.status_text.set("Processing image...")
        self.processing = True
        
        # Process in a separate thread to avoid freezing the UI
        self.root.after(100, self.do_process_image)
    
    def do_process_image(self):
        try:
            # Get parameters from UI
            input_path = self.input_path.get()
            output_path = self.output_path.get()
            
            # Scale parameters from 0-100 range to their appropriate ranges
            sharpening_strength = self.sharpening_strength.get() / 100 * 3.0  # Scale from 0-100 to 0-3.0
            blur_sigma = int(self.blur_sigma.get())  # Keep as integer
            jpeg_quality = int(self.jpeg_quality.get())  # Keep as integer
            noise_reduction = self.noise_reduction.get() / 100  # Scale from 0-100 to 0-1.0
            saturation = self.saturation.get() / 50  # Scale from 0-100 to 0-2.0
            contrast = self.contrast.get() / 50  # Scale from 0-100 to 0-2.0
            
            # Process the image
            result = process_raw_image(
                input_path=input_path,
                output_path=output_path,
                sharpening_strength=sharpening_strength,
                blur_sigma=blur_sigma,
                jpeg_quality=jpeg_quality,
                noise_reduction=noise_reduction,
                saturation=saturation,
                contrast=contrast
            )
            
            # Update UI based on result
            if result:
                self.status_text.set(f"Image processed successfully: {result}")
                self.last_processed_image = result
                self.view_button.config(state=tk.NORMAL)
                messagebox.showinfo("Success", f"Image processed successfully and saved to:\n{result}")
            else:
                self.status_text.set("Image processing failed.")
                messagebox.showerror("Error", "Failed to process the image. Check console for details.")
        
        except Exception as e:
            self.status_text.set(f"Error: {str(e)}")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        
        finally:
            # Re-enable process button and stop progress
            self.process_button.config(state=tk.NORMAL)
            self.progress.stop()
            self.processing = False
    
    def view_result(self):
        if not self.last_processed_image or not os.path.exists(self.last_processed_image):
            messagebox.showerror("Error", "No processed image available to view.")
            return
        
        # Display the image using matplotlib
        try:
            result_img = cv2.imread(self.last_processed_image)
            result_img_rgb = cv2.cvtColor(result_img, cv2.COLOR_BGR2RGB)
            plt.figure(figsize=(10, 8))
            plt.imshow(result_img_rgb)
            plt.axis('off')
            plt.title('Processed Image')
            plt.show()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {str(e)}")

# Example usage
if __name__ == "__main__":
    root = tk.Tk()
    app = RawImageProcessorApp(root)
    root.mainloop()