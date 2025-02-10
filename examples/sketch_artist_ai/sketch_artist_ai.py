# Describe a character and generate a picture.
import torch
from diffusers import StableDiffusionPipeline
from PIL import Image

def generate_sketch(prompt):
    # Load the Stable Diffusion model using default settings (CPU, float32)
    pipe = StableDiffusionPipeline.from_pretrained("CompVis/stable-diffusion-v1-4")
    # No need to move the pipeline to GPU (i.e., no .to("cuda") call)
    image = pipe(prompt).images[0]
    return image

def main():
    prompt = input("Enter a description for the sketch: ")
    print("Generating image... (this may take a few minutes on CPU)")
    sketch = generate_sketch(prompt)
    # Display and save the generated image
    sketch.show()
    sketch.save("generated_sketch.png")
    print("Sketch saved as generated_sketch.png")

if __name__ == "__main__":
    main()
