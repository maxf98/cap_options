# import tkinter as tk
# from tkinter import scrolledtext


# def send_message():
#     user_message = entry.get()
#     if user_message.strip():
#         chat_window.insert(tk.END, f"You: {user_message}\n")
#         entry.delete(0, tk.END)


# def on_listbox_select(event):
#     selected_index = listbox.curselection()
#     if selected_index:
#         selected_item = listbox.get(selected_index[0])
#         chat_window.insert(tk.END, f"Selected: {selected_item}\n")


# # Create the main window
# root = tk.Tk()
# root.title("Chat Interface")
# root.geometry("400x400")

# # Create chat display
# chat_window = scrolledtext.ScrolledText(
#     root, wrap=tk.WORD, width=50, height=10, state="normal"
# )
# chat_window.pack(pady=10)

# # Create Listbox
# listbox = tk.Listbox(root, height=5)
# listbox.pack(pady=5)
# listbox.insert(tk.END, "Item 1", "Item 2", "Item 3", "Item 4")  # Add items

# # Bind click event
# listbox.bind("<<ListboxSelect>>", on_listbox_select)

# # Create entry field
# entry = tk.Entry(root, width=40)
# entry.pack(pady=5)

# # Create send button
# button = tk.Button(root, text="Send", command=send_message)
# button.pack(pady=5)

# # Run the application
# root.mainloop()


def get_letter_pixels(letter):
    """maps a given letter to a (10, 10) array of pixel values,
    where a 1 represents a letter pixel"""
    from PIL import Image, ImageDraw, ImageFont

    img_size = (50, 10)  # Adjust as needed
    img = Image.new("1", img_size, color=0)  # 1-bit image (black & white)
    draw = ImageDraw.Draw(img)

    # Load a font (you can use a different TTF file)
    font = ImageFont.load_default()

    # Draw letter
    draw.text((0, 0), letter, font=font, fill=1)

    # Convert to pixel matrix
    pixels = list(img.getdata())
    width, height = img.size
    pixel_matrix = [pixels[i * width : (i + 1) * width] for i in range(height)]
    return pixel_matrix


import matplotlib.pyplot as plt

pixels = get_letter_pixels("hello")
plt.imshow(pixels)
plt.show()
