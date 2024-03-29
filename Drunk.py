import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import json
import time

# Constants for local storage
IMAGE_DIR = 'DrunkImage'
METADATA_FILE = os.path.join(IMAGE_DIR, 'metadata.json')

# Ensure the image directory exists
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Function to load saved images and names
def load_saved_data():
    if os.path.exists(METADATA_FILE):
        with open(METADATA_FILE, 'r') as file:
            metadata = json.load(file)
    else:
        metadata = []

    images, names = [], []
    for item in metadata:
        img_path = os.path.join(IMAGE_DIR, item['filename'])
        if os.path.exists(img_path):
            image = Image.open(img_path)
            images.append(image)
            names.append(item['name'])

    return images, names

# Function to resize an image

def resize_image(image, max_size=(250, 250)):

    original_width, original_height = image.size
    max_width, max_height = max_size

    # Determine the scale factor while maintaining the aspect ratio
    width_ratio = min(max_width / original_width, 1)
    height_ratio = min(max_height / original_height, 1)
    scale_ratio = min(width_ratio, height_ratio)

    # Calculate the new image dimensions
    new_width = int(original_width * scale_ratio)
    new_height = int(original_height * scale_ratio)

    # Resize the image
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)  # Use LANCZOS for high-quality downsampling

    return resized_image

# Function to create collage
def create_collage(images, names, image_size=(250, 250), max_images_per_row=3, spacing=10):
    if not images:
        return None
    
    resized_images = [resize_image(image, image_size) for image in images]  # Ensure images are resized

    num_rows = (len(resized_images) + max_images_per_row - 1) // max_images_per_row
    collage_width = max_images_per_row * (image_size[0] + spacing) - spacing
    collage_height = num_rows * (image_size[1] + spacing) - spacing

    collage = Image.new('RGB', (collage_width, collage_height), "white")
    draw = ImageDraw.Draw(collage)
    font = ImageFont.load_default()

    for i, image in enumerate(resized_images):
        row = i // max_images_per_row
        col = i % max_images_per_row
        x = col * (image_size[0] + spacing)
        y = row * (image_size[1] + spacing)
        collage.paste(image, (x, y))
        text_x = x
        text_y = y + image_size[1] + 5
        draw.text((text_x, text_y), names[i], fill="black", font=font)

    return collage


# Function to save images and names to disk
def save_data(names):
    metadata = [{'name': name, 'filename': f"{name}.jpg"} for name in names]
    with open(METADATA_FILE, 'w') as file:
        json.dump(metadata, file)



images, names = load_saved_data()

if 'images' not in st.session_state:
    st.session_state['images'] = images
if 'names' not in st.session_state:
    st.session_state['names'] = names

# App title and navigation
st.markdown("""
    <style>
    .title {
        font-size: 70px;
        font-weight: bold;
        color: #FF4B4B; /* Customize the color of the title */
        text-align: center;
    }
    .tagline {
        font-size: 30px; /* Adjust the size of the tagline */
        color: #00008B; /* Customize the color of the tagline */
        text-align: center;
        margin-top: 10px; /* Space between title and tagline */
    }
    </style>
    <div class="title">BHAND-o-METER</div>
    <div class="tagline">Unofficial 'Drunk' Ambassador's of CK</div>
    """, unsafe_allow_html=True)

st.markdown(
    """
    <style>
        /* This CSS selector targets the sidebar div and minimizes it */
        .css-1d391kg {width: 0px;}
    </style>
    """,
    unsafe_allow_html=True
)

# Using radio buttons for navigation
page = st.sidebar.radio("Navigation", ['View Collage', 'Upload Image'], index=0)

if page == 'Upload Image':
    # Upload logic
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg"])
    name = st.text_input("Enter the person's name:")
    if st.button('Submit') and uploaded_file and name:
        image = Image.open(uploaded_file)
        resized_image = resize_image(image)  # Resize the image here
        # Save the resized image
        filename = f"{name}.jpg"
        filepath = os.path.join(IMAGE_DIR, filename)
        resized_image.save(filepath)
        # Prepend to metadata and session state to make the latest image appear first
        st.session_state.images.insert(0, resized_image)
        st.session_state.names.insert(0, name)
        save_data(st.session_state['names'])
        st.success("Image and details added!")

elif page == 'View Collage':
    # Display the collage
    if st.session_state['images']:
        collage = create_collage(st.session_state['images'], st.session_state['names'])
        st.image(collage, caption="Unofficial 'Drunk' Ambassador's of CK", use_column_width=True)
    else:
        st.write("No images to display. Please upload images on the 'Upload Image' page.")
