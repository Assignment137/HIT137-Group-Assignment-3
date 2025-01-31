import cv2  # Import the OpenCV library for image processing.
import tkinter as tk  # Import the Tkinter library for GUI development.
from tkinter import filedialog, Scale, messagebox  # Import specific modules from Tkinter for file dialog, slider, and message boxes.
from PIL import Image, ImageTk  # Import the PIL (Pillow) library for image manipulation and Tkinter compatibility.

class ImageProcessingApp:  # Define a class for the image processing application.
    def __init__(self, root):  # Constructor for the class, takes the root window as input.
        self.root = root  # Store the root window in the class.
        self.root.title("Image Processing App")  # Set the title of the window.
        self.set_window_geometry()  # Call a method to set the window size and position.
        self.image = None  # Initialize the image variable to None.
        self.cropped_image = None  # Initialize the cropped image variable to None.
        self.original_cropped = None  # Initialize a copy of the cropped image for resizing.
        self.undo_stack = []  # Initialize an empty list for undo functionality.
        self.redo_stack = []  # Initialize an empty list for redo functionality.
        self.cropping = False  # Initialize a boolean variable to track cropping state.
        self.start_x, self.start_y, self.end_x, self.end_y = None, None, None, None  # Initialize variables for cropping coordinates.

        self.create_widgets()  # Call a method to create the GUI elements.
        self.add_keyboard_shortcuts()  # Call a method to add keyboard shortcuts.
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)  # Set the window close event handler.

    def set_window_geometry(self):  # Method to set the window size and position.
        screen_width = self.root.winfo_screenwidth()  # Get the screen width.
        screen_height = self.root.winfo_screenheight()  # Get the screen height.
        window_width = int(screen_width * 0.75)  # Calculate the window width (75% of screen width).
        window_height = int(screen_height * 0.75)  # Calculate the window height (75% of screen height).
        x_position = (screen_width - window_width) // 2  # Calculate the x position for centering.
        y_position = (screen_height - window_height) // 2  # Calculate the y position for centering.
        self.root.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")  # Set the window geometry.

    def create_widgets(self):  # Method to create the GUI elements.
        self.image_frame = tk.Frame(self.root)  # Create a frame for the original image.
        self.image_frame.pack(side=tk.LEFT, padx=10, pady=10)  # Pack the image frame to the left.
        self.cropped_frame = tk.Frame(self.root)  # Create a frame for the cropped image.
        self.cropped_frame.pack(side=tk.LEFT, padx=10, pady=10)  # Pack the cropped image frame to the left.

        self.canvas = tk.Canvas(self.image_frame, width=400, height=400, bg="gray")  # Create a canvas for the original image.
        self.canvas.pack()  # Pack the canvas.
        self.cropped_canvas = tk.Canvas(self.cropped_frame, width=400, height=400, bg="gray")  # Create a canvas for the cropped image.
        self.cropped_canvas.pack()  # Pack the canvas.

        self.control_frame = tk.Frame(self.root)  # Create a frame for the control buttons.
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10)  # Pack the control frame to the right.

        self.load_button = tk.Button(self.control_frame, text="Load Image", command=self.load_image)  # Create a load image button.
        self.load_button.pack(pady=5)  # Pack the button.

        self.crop_button = tk.Button(self.control_frame, text="Crop Image", command=self.start_crop)  # Create a crop image button.
        self.crop_button.pack(pady=5)  # Pack the button.

        self.resize_slider = Scale(self.control_frame, from_=10, to=200, orient=tk.HORIZONTAL, label="Resize (%)", command=self.resize_image)  # Create a resize slider.
        self.resize_slider.pack(pady=5)  # Pack the slider.

        self.grayscale_button = tk.Button(self.control_frame, text="Grayscale", command=self.convert_to_grayscale)  # Create a grayscale button.
        self.grayscale_button.pack(pady=5)  # Pack the button.

        self.rotate_button = tk.Button(self.control_frame, text="Rotate 90°", command=self.rotate_image)  # Create a rotate button.
        self.rotate_button.pack(pady=5)  # Pack the button.

        self.save_button = tk.Button(self.control_frame, text="Save Image", command=self.save_image)  # Create a save image button.
        self.save_button.pack(pady=5)  # Pack the button.

        self.undo_button = tk.Button(self.control_frame, text="Undo", command=self.undo)  # Create an undo button.
        self.undo_button.pack(pady=5)  # Pack the button.

        self.redo_button = tk.Button(self.control_frame, text="Redo", command=self.redo)  # Create a redo button.
        self.redo_button.pack(pady=5)  # Pack the button.

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)  # Bind mouse button press event to the canvas.
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)  # Bind mouse drag event to the canvas.
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)  # Bind mouse button release event to the canvas.

        self.canvas.config(width=400, height=400)  # Set the canvas size.
        self.cropped_canvas.config(width=400, height=400)  # Set the cropped canvas size.

        self.root.bind("<Configure>", self.on_window_resize)  # Bind window resize event.

    def add_keyboard_shortcuts(self):  # Method to add keyboard shortcuts.
        self.root.bind("<Control-z>", lambda event: self.undo())  # Bind Ctrl+Z to undo.
        self.root.bind("<Control-y>", lambda event: self.redo())  # Bind Ctrl+Y to redo.
        self.root.bind("<Control-s>", lambda event: self.save_image())  # Bind Ctrl+S to save.
        self.root.bind("<Control-o>", lambda event: self.load_image())  # Bind Ctrl+O to load.
        self.root.bind("<Control-g>", lambda event: self.convert_to_grayscale())  # Bind Ctrl+G to grayscale.
        self.root.bind("<Control-r>", lambda event: self.rotate_image())  # Bind Ctrl+R to rotate.

    def load_image(self):  # Method to load an image.
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp")])  # Open a file dialog.
        if file_path:  # If a file path is selected.
            self.image = cv2.imread(file_path)  # Read the image using OpenCV.
            if self.image is not None:  # If the image was loaded successfully.
                self.display_image(self.image, self.canvas)  # Display the image on the canvas.
                self.display_image(None, self.cropped_canvas)  # Clear the cropped image canvas.
                self.undo_stack.append({"original_image": self.image.copy()})  # Add the original image to the undo stack.
                self.redo_stack.clear()  # Clear the redo stack.
            else:  # If the image loading failed.
                messagebox.showerror("Error", "Failed to load image.")  # Show an error
    def display_image(self, image, canvas):  # Method to display an image on a canvas.
        if image is not None:  # If an image is provided.
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convert the image from BGR to RGB.
            pil_image = Image.fromarray(image)  # Convert the image to a PIL Image.

            canvas_width = canvas.winfo_width()  # Get the canvas width.
            canvas_height = canvas.winfo_height()  # Get the canvas height.
            img_width, img_height = pil_image.size  # Get the image width and height.

            if canvas_width == 0 or canvas_height == 0:  # Check if canvas dimensions are valid.
                return  # If canvas dimensions are invalid, exit the function.

            ratio = min(canvas_width / img_width, canvas_height / img_height)  # Calculate the scaling ratio.
            new_width = int(img_width * ratio)  # Calculate the new width.
            new_height = int(img_height * ratio)  # Calculate the new height.
            resized_image = pil_image.resize((new_width, new_height), Image.LANCZOS)  # Resize the image.

            image_tk = ImageTk.PhotoImage(resized_image)  # Convert the image to a Tkinter PhotoImage.
            canvas.image = image_tk  # Store the PhotoImage in the canvas.
            canvas.create_image(canvas_width // 2, canvas_height // 2, anchor=tk.CENTER, image=image_tk)  # Display the image on the canvas.
        else:  # If no image is provided.
            canvas.delete("all")  # Clear the canvas.
            canvas.image = None  # Set the canvas image to None.

    def start_crop(self):  # Method to start cropping.
        if self.image is not None:  # If an image is loaded.
            self.cropping = True  # Set the cropping flag to True.
            messagebox.showinfo("Crop Mode", "Draw a rectangle to crop the image on the ORIGINAL image.")  # Show a message box.
        else:  # If no image is loaded.
            messagebox.showwarning("Warning", "Please load an image first.")  # Show a warning message.

    def on_button_press(self, event):  # Method to handle mouse button press event.
        if self.cropping:  # If cropping is active.
            self.start_x, self.start_y = event.x, event.y  # Store the starting coordinates.

    def on_mouse_drag(self, event):  # Method to handle mouse drag event.
        if self.cropping:  # If cropping is active.
            self.canvas.delete("rect")  # Delete the previous rectangle.
            self.canvas.create_rectangle(self.start_x, self.start_y, event.x, event.y, outline="red", tag="rect")  # Draw a new rectangle.

    def on_button_release(self, event):  # Method to handle mouse button release event.
        if self.cropping:  # If cropping is active.
            self.end_x, self.end_y = event.x, event.y  # Store the ending coordinates.
            self.crop_image()  # Call the crop_image method.
            self.cropping = False  # Set the cropping flag to False.

    def crop_image(self):  # Method to crop the image.
        if self.image is not None:  # If an image is loaded.
            canvas_width = self.canvas.winfo_width()  # Get the canvas width.
            canvas_height = self.canvas.winfo_height()  # Get the canvas height.
            img_width, img_height = self.image.shape[1], self.image.shape[0]  # Get the image width and height.

            ratio_x = img_width / canvas_width  # Calculate the x ratio.
            ratio_y = img_height / canvas_height  # Calculate the y ratio.

            x1 = int(self.start_x * ratio_x)  # Calculate the x1 coordinate.
            y1 = int(self.start_y * ratio_y)  # Calculate the y1 coordinate.
            x2 = int(self.end_x * ratio_x)  # Calculate the x2 coordinate.
            y2 = int(self.end_y * ratio_y)  # Calculate the y2 coordinate.

            x1 = max(0, min(x1, img_width - 1))  # Ensure x1 is within bounds.
            y1 = max(0, min(y1, img_height - 1))  # Ensure y1 is within bounds.
            x2 = max(0, min(x2, img_width - 1))  # Ensure x2 is within bounds.
            y2 = max(0, min(y2, img_height - 1))  # Ensure y2 is within bounds.

            if x1 >= x2 or y1 >= y2:  # Check for invalid cropping area.
                messagebox.showwarning("Warning", "Invalid cropping area. Please try again.")  # Show a warning message.
                return  # Exit the function.

            self.cropped_image = self.image[y1:y2, x1:x2]  # Crop the image.
            self.original_cropped = self.cropped_image.copy()  # Store a copy for resizing.
            self.display_image(self.cropped_image, self.cropped_canvas)  # Display the cropped image.
            self.undo_stack.append({"original_image": self.image.copy(), "cropped_image": self.cropped_image.copy(), "original_cropped": self.original_cropped.copy()})  # Add the state to the undo stack.
            self.redo_stack.clear()  # Clear the redo stack.

    def resize_image(self, value):  # Method to resize the image.
        if self.original_cropped is not None:  # If a cropped image exists.
            scale = int(value) / 100  # Calculate the scaling factor.
            original_height, original_width = self.original_cropped.shape[:2]  # Get the original dimensions.

            new_width = int(original_width * scale)  # Calculate the new width.
            new_height = int(original_height * scale)  # Calculate the new height.

            resized_image = cv2.resize(self.original_cropped, (new_width, new_height), interpolation=cv2.INTER_AREA)  # Resize the image.
            self.cropped_image = resized_image  # Update the cropped image.
            self.display_image(resized_image, self.cropped_canvas)  # Display the resized image.
            self.undo_stack.append({"original_image": self.image.copy(), "cropped_image": self.cropped_image.copy(), "original_cropped": self.original_cropped.copy()})  # Add the state to the undo stack.
            self.redo_stack.clear()  # Clear the redo stack.

    def convert_to_grayscale(self):  # Method to convert to grayscale.
        if self.cropped_image is not None:  # If a cropped image exists.
            self.cropped_image = cv2.cvtColor(self.cropped_image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale.
            self.cropped_image = cv2.cvtColor(self.cropped_image, cv2.COLOR_GRAY2BGR)  # Convert back to BGR (for display).
            self.display_image(self.cropped_image, self.cropped_canvas)  # Display the grayscale image.
            self.undo_stack.append({"original_image": self.image.copy(), "cropped_image": self.cropped_image.copy(), "original_cropped": self.original_cropped.copy()})  # Add the state to the undo stack.
            self.redo_stack.clear()  # Clear the redo stack.


    def rotate_image(self):  # Method to rotate the image.
        if self.cropped_image is not None:  # If a cropped image exists.
            self.cropped_image = cv2.rotate(self.cropped_image, cv2.ROTATE_90_CLOCKWISE)  # Rotate the image.
            self.display_image(self.cropped_image, self.cropped_canvas)  # Display the rotated image.
            self.undo_stack.append({"original_image": self.image.copy(), "cropped_image": self.cropped_image.copy(), "original_cropped": self.original_cropped.copy()})  # Add the state to the undo stack.
            self.redo_stack.clear()  # Clear the redo stack.

    def save_image(self):  # Method to save the image.
        if self.cropped_image is not None:  # If a cropped image exists.
            file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png"), ("JPEG Files", "*.jpg")])  # Open a save file dialog.
            if file_path:  # If a file path is selected.
                cv2.imwrite(file_path, cv2.cvtColor(self.cropped_image, cv2.COLOR_BGR2RGB))  # Save the image.
                messagebox.showinfo("Success", "Image saved successfully.")  # Show a success message.
        else:  # If no cropped image exists.
            messagebox.showwarning("Warning", "No image to save.")  # Show a warning message.

    def undo(self):  # Method to undo an action.
        if len(self.undo_stack) > 1:  # Check for at least 2 elements before popping
            current_state = self.undo_stack.pop()  # Pop the current state
            self.redo_stack.append(current_state)  # Push the popped state into redo stack
            previous_state = self.undo_stack[-1]  # Access the previous state

            self.image = previous_state["original_image"].copy()  # Restore original image
            self.display_image(self.image, self.canvas)  # Display original image

            cropped_image = previous_state.get("cropped_image")  # Retrieve cropped image (if any)
            if cropped_image is not None:  # If there was a cropped image
                self.cropped_image = cropped_image.copy()  # Restore cropped image
                self.original_cropped = previous_state.get("original_cropped").copy() # restore original cropped version
                self.display_image(self.cropped_image, self.cropped_canvas)  # Display cropped image
            else:  # If no cropped image
                self.cropped_image = None  # Set cropped image to None
                self.original_cropped = None # set original cropped to None
                self.display_image(None, self.cropped_canvas)  # Clear cropped canvas

        else:  # Handle the case where there's nothing to undo
            if self.undo_stack:  # If there's still one element, restore to the very initial state
                initial_state = self.undo_stack[0]  # Restore to initial state
                self.image = initial_state["original_image"].copy()  # Restore original image
                self.display_image(self.image, self.canvas)  # Display original image
                self.cropped_image = None  # Set cropped image to None
                self.original_cropped = None # set original cropped to None
                self.display_image(None, self.cropped_canvas)  # Clear cropped canvas

            else:
                messagebox.showinfo("Info", "Nothing to undo.")  # Show a message

    def redo(self):  # Method to redo an action.
        if self.redo_stack:  # If there are actions to redo.
            image_state = self.redo_stack.pop()  # Pop the state from the redo stack.
            self.undo_stack.append(image_state)  # Push it into the undo stack

            self.image = image_state["original_image"].copy()  # Restore original image
            self.display_image(self.image, self.canvas)  # Display original image

            cropped_image = image_state.get("cropped_image")  # Retrieve cropped image (if any)
            if cropped_image is not None:  # If there was a cropped image
                self.cropped_image = cropped_image.copy()  # Restore cropped image
                self.original_cropped = image_state.get("original_cropped").copy() # restore original cropped version
                self.display_image(self.cropped_image, self.cropped_canvas)  # Display cropped image
            else:  # If no cropped image
                self.cropped_image = None  # Set cropped image to None
                self.original_cropped = None # set original cropped to None
                self.display_image(None, self.cropped_canvas)  # Clear cropped canvas
        else:
            messagebox.showinfo("Info", "Nothing to redo.")  # Show a message.

    def on_window_resize(self, event):  # Method to handle window resize event.
        if self.image is not None:  # If an image is loaded.
            self.display_image(self.image, self.canvas)  # Redisplay the image.
        if self.cropped_image is not None:  # If a cropped image is loaded.
            self.display_image(self.cropped_image, self.cropped_canvas)  # Redisplay the cropped image.

    def on_closing(self):  # Method to handle window closing event.
        if messagebox.askokcancel("Quit", "Do you want to quit?"):  # Ask for confirmation.
            self.root.destroy()  # Destroy the window if confirmed.

if __name__ == "__main__":  # Main block of the application.
    root = tk.Tk()  # Create the root window.
    app = ImageProcessingApp(root)  # Create an instance of the ImageProcessingApp class.
    root.mainloop()  # Start the Tkinter event loop.