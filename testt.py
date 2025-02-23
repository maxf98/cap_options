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


import multiprocessing
import time
def add():
    while True:
        x = input("ello")
        time.sleep(3)

def sud():
     while True:
        print(0)
        time.sleep(3)
if __name__ == '__main__':
    p1 = multiprocessing.Process(name='p1', target=add)
    p = multiprocessing.Process(name='p', target=sud)
    p1.start()
    p.start()
