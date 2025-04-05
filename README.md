# RAW Image Processor

This tool processes RAW images (CR3, CR2, NEF, ARW, ORF, RAF, RW2, DNG) to reduce blur using an unsharp masking technique. It provides a simple way to sharpen your RAW photos with customizable parameters through a user-friendly interface.

## Requirements

The script requires several Python libraries to work with RAW images and perform image processing. You can install all dependencies using the provided `requirements.txt` file:

```
pip install -r requirements.txt
```

## Usage

1. Run the script:
   ```
   python raw_image_processor.py
   ```

2. Use the graphical interface to:
   - Click "Browse" to select your input RAW image file
   - Choose where to save the processed output image
   - Adjust the sharpening parameters using the sliders
   - Click "Process Image" to start processing

## Customizing Parameters

You can adjust the image quality by modifying these parameters:

```python
result = process_raw_image(
    input_path=raw_path,
    output_path=output_path,
    sharpening_strength=1.5,  # Higher values = more sharpening
    blur_sigma=3,             # Higher values = more blur in the mask
    jpeg_quality=95,          # Higher values = better quality but larger file size (0-100)
    noise_reduction=0.3,      # Higher values = more noise reduction (0.0-1.0)
    saturation=1.1,           # Values > 1.0 increase saturation, < 1.0 decrease it
    contrast=1.1              # Values > 1.0 increase contrast, < 1.0 decrease it
)
```

- `sharpening_strength`: Controls the intensity of the sharpening effect (1.0 = no change, 2.0 = strong sharpening)
- `blur_sigma`: Controls the radius of the blur used in the unsharp mask
- `jpeg_quality`: Controls the quality of the JPEG compression (0-100, higher values produce better quality but larger files)
- `noise_reduction`: Controls the strength of noise reduction (0.0 = none, 1.0 = maximum)
- `saturation`: Adjusts color saturation (1.0 = no change, >1.0 = more vibrant, <1.0 = less vibrant)
- `contrast`: Adjusts image contrast (1.0 = no change, >1.0 = more contrast, <1.0 = less contrast)

## Troubleshooting

If you encounter issues:

1. Ensure all dependencies are properly installed
2. Verify that the input file path points to a valid RAW image
3. Make sure you have write permissions for the output directory
4. For large RAW files, ensure your system has sufficient memory

## How It Works

The script uses several techniques to enhance image quality:

1. The RAW image is processed into a standard RGB format
2. Unsharp masking is applied to enhance sharpness:
   - A Gaussian blur is applied to create a blurred version of the image
   - The original image is enhanced by subtracting the blurred version, which emphasizes edges and details
3. Optional noise reduction is applied using non-local means denoising
4. Color enhancements are applied:
   - Saturation adjustment to control color vibrancy
   - Contrast adjustment to improve overall image appearance
5. The result is saved as a JPEG file with customizable quality settings