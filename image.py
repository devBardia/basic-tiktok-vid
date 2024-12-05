from PIL import Image, ImageDraw, ImageFont
import os

def create_lifestyle_image(
    main_title,
    top_left_title, top_left_image_path,
    top_right_title, top_right_image_path,
    bottom_left_title, bottom_left_image_path,
    bottom_right_title, bottom_right_image_path,
    output_path=None
):
    # Create output directory if it doesn't exist
    os.makedirs("product", exist_ok=True)
    
    # Find the next available number for the output file
    if output_path is None:
        counter = 1
        while True:
            output_path = f"product/output{counter}.jpg"
            if not os.path.exists(output_path):
                break
            counter += 1
    
    # Create base image (1080x1920)
    img = Image.new('RGB', (1080, 1920), 'white')
    draw = ImageDraw.Draw(img)
    
    # Load custom fonts with specific weights
    try:
        # Main title font - Extra Bold (900)
        title_font = ImageFont.truetype("fonts/static/Inter_28pt-SemiBoldItalic.ttf", 60)  # or your specific 900-weight font
        
        # Subtitle font - Bold (800) - Reduced from 40 to 35
        subtitle_font = ImageFont.truetype("fonts/static/Inter_28pt-SemiBoldItalic.ttf", 35)  # Reduced size here
    except Exception as e:
        print(f"Error loading fonts: {e}")
        # Fallback to default font if custom font is not available
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Define grid parameters
    total_height = 1920  # Total image height
    grid_width = 450
    grid_height = 450
    padding = 30
    vertical_gap = 120
    title_spacing = 200
    
    # Calculate vertical centering
    total_grid_height = (2 * grid_height) + vertical_gap
    grid_top = ((total_height - total_grid_height) // 2) + 50  # Lowered by 50 pixels
    
    # Center the entire grid horizontally
    left_margin = (1080 - (2 * grid_width + padding)) // 2
    
    # Define grid positions (centered both horizontally and vertically)
    positions = {
        'top_left': (left_margin, grid_top),
        'top_right': (left_margin + grid_width + padding, grid_top),
        'bottom_left': (left_margin, grid_top + grid_height + vertical_gap),
        'bottom_right': (left_margin + grid_width + padding, grid_top + grid_height + vertical_gap)
    }

    # Calculate maximum width for title with margins
    max_title_width = 800  # Maximum width for title text
    margin = 140  # Margin on each side
    
    # Function to wrap text
    def wrap_text(text, font, max_width):
        words = text.split()
        lines = []
        current_line = []
        current_width = 0
        
        for word in words:
            word_bbox = draw.textbbox((0, 0), word + " ", font=font)
            word_width = word_bbox[2] - word_bbox[0]
            
            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
                current_width = word_width
        
        if current_line:
            lines.append(" ".join(current_line))
        return lines

    # Wrap and draw main title
    wrapped_lines = wrap_text(main_title, title_font, max_title_width)
    line_height = title_font.size + 10
    total_title_height = len(wrapped_lines) * line_height
    
    # Calculate starting Y position for title block
    title_y = grid_top - title_spacing - total_title_height + 50  # Lowered by 50 pixels
    
    # Draw each line of the title
    for i, line in enumerate(wrapped_lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_width = bbox[2] - bbox[0]
        line_x = (1080 - line_width) // 2
        current_y = title_y + (i * line_height)
        draw.text((line_x, current_y), line, font=title_font, fill='black')

    # Function to process and paste images with updated path handling
    def process_and_paste_image(image_path, box):
        try:
            full_image_path = os.path.join("used", image_path)  # Update image path to use 'used' folder
            with Image.open(full_image_path) as section_img:
                # Convert image to RGBA
                section_img = section_img.convert('RGBA')
                
                # Define fixed dimensions for all images
                image_width = grid_width - padding*2
                image_height = grid_height - padding*2
                
                # Create a white background box for the image
                image_box = Image.new('RGBA', (image_width, image_height), (255, 255, 255, 255))
                
                # Resize and maintain aspect ratio
                aspect_ratio = min(image_width / section_img.width, image_height / section_img.height)
                new_size = (
                    int(section_img.width * aspect_ratio),
                    int(section_img.height * aspect_ratio)
                )
                section_img = section_img.resize(new_size, Image.Resampling.LANCZOS)
                
                # Calculate position to center image in box
                x_offset = (image_width - new_size[0]) // 2
                y_offset = (image_height - new_size[1]) // 2
                
                # Paste the resized image onto the white background
                image_box.paste(section_img, (x_offset, y_offset), section_img)
                
                # Calculate position to paste the final image
                x = box[0] + padding
                y = box[1] + padding + 40  # Add space for subtitle
                
                # Paste the final image with white background
                img.paste(image_box, (x, y), image_box)
                
        except Exception as e:
            print(f"Error processing image {full_image_path}: {e}")
            # Create a white placeholder box if image fails to load
            placeholder = Image.new('RGBA', (grid_width - padding*2, grid_height - padding*2), (255, 255, 255, 255))
            img.paste(placeholder, (box[0] + padding, box[1] + padding + 40))

    # Draw sections
    sections = [
        (top_left_title, top_left_image_path, positions['top_left']),
        (top_right_title, top_right_image_path, positions['top_right']),
        (bottom_left_title, bottom_left_image_path, positions['bottom_left']),
        (bottom_right_title, bottom_right_image_path, positions['bottom_right'])
    ]

    # Define constant box dimensions
    box_width = 400  # Fixed width for all boxes
    box_height = 70  # Fixed height for all boxes
    box_padding = 20
    icon_size = 40  # Increased bookmark size

    for title, image_path, pos in sections:
        # Calculate box position (centered)
        box_x = pos[0] + (grid_width - box_width) // 2
        box_y = pos[1] - 40
        
        # Draw the box with a black background
        draw.rectangle(
            [(box_x, box_y), 
             (box_x + box_width, box_y + box_height)],
            fill='black'
        )
        
        # Calculate text size to fit in box
        subtitle_bbox = draw.textbbox((0, 0), title, font=subtitle_font)
        subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]
        
        # Draw the title text in white (aligned to the left)
        subtitle_x = box_x + box_padding
        subtitle_y = box_y + ((box_height - subtitle_height) // 2)  # Vertical center
        draw.text(
            (subtitle_x, subtitle_y),
            title,
            font=subtitle_font,
            fill='white'
        )
        
        # Load and paste the bookmark icon
        try:
            with Image.open("bookmark.png") as bookmark_icon:
                # Convert to RGBA if not already
                bookmark_icon = bookmark_icon.convert('RGBA')
                # Resize the icon while maintaining aspect ratio
                bookmark_icon.thumbnail((icon_size, icon_size))
                # Calculate position for the icon (right-aligned and lowered)
                icon_x = box_x + box_width - bookmark_icon.width - box_padding
                icon_y = box_y + ((box_height - bookmark_icon.height) // 2) + 5  # Added +5 to lower it slightly
                # Create a white version of the icon
                white_icon = Image.new('RGBA', bookmark_icon.size, (0, 0, 0, 0))
                for x in range(bookmark_icon.width):
                    for y in range(bookmark_icon.height):
                        r, g, b, a = bookmark_icon.getpixel((x, y))
                        if a > 0:  # If pixel is not transparent
                            white_icon.putpixel((x, y), (255, 255, 255, a))
                # Paste the white icon onto the main image
                img.paste(white_icon, (icon_x, icon_y), white_icon)
        except Exception as e:
            print(f"Error loading bookmark icon: {e}")

        # Process and paste image
        process_and_paste_image(image_path, pos)

    # Save the final image to the product folder
    img.save(output_path)
    print(f"Image saved as {output_path}")

# Example usage
if __name__ == "__main__":
    create_lifestyle_image(
        main_title="Using this will give you +9999999999999 AURA",
        
        top_left_image_path="trenbolone-injection.jpg",
        top_right_image_path="s-l1200.jpg",
        bottom_left_image_path="download.jpg",
        bottom_right_image_path="unnamed (19).jpg",  # Add your fourth image path here
        
        top_left_title="Tren",
        top_right_title="Dumbell",
        bottom_left_title="Alcohal",
        bottom_right_title="FitMaxAi"
    )