import os
import tkinter as tk
from PIL import Image, ImageTk

class ImageBrowser:
    def __init__(self, root, folder_path):
        self.root = root
        self.folder_path = folder_path
        self.images = [file for file in os.listdir(folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        self.current_image_index = 0

        # Cropping box dimensions
        self.crop_box_width = 2880
        self.crop_box_height = 1800

        self.canvas = tk.Canvas(root, borderwidth=0)
        self.frame = tk.Frame(self.canvas)
        self.vsb = tk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.hsb = tk.Scrollbar(root, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4,4), window=self.frame, anchor="nw", tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.ok_button = tk.Button(root, text='OK', command=self.show_next_image)
        self.ok_button.pack(side='left')

        self.crop_button = tk.Button(root, text='Crop', command=self.crop_image)
        self.crop_button.pack(side='right')

        # Bind the Enter key to crop_image_event
        self.root.bind('<Return>', self.crop_image_event)

        self.crop_rect = None
        self.dragging = False
        self.start_x = None
        self.start_y = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.show_image()

    def on_button_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        if not self.crop_rect:
            box_width = self.crop_box_width * self.scale_factor
            box_height = self.crop_box_height * self.scale_factor
            self.crop_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, 
                self.start_x + box_width, self.start_y + box_height, 
                outline='red'
            )
        else:
            x1, y1, x2, y2 = self.canvas.coords(self.crop_rect)
            if x1 <= self.start_x <= x2 and y1 <= self.start_y <= y2:
                self.dragging = True

    def on_move_press(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)

        if self.dragging:
            # Calculate the difference
            dx = curX - self.start_x
            dy = curY - self.start_y
            self.canvas.move(self.crop_rect, dx, dy)
            self.start_x = curX
            self.start_y = curY
        elif self.crop_rect:
            box_width = self.crop_box_width * self.scale_factor
            box_height = self.crop_box_height * self.scale_factor
            self.canvas.coords(self.crop_rect, self.start_x, self.start_y, self.start_x + box_width, self.start_y + box_height)

    def on_button_release(self, event):
        self.dragging = False  # Stop dragging

    def resize_image(self, image):
        max_width = self.root.winfo_screenwidth()
        max_height = self.root.winfo_screenheight()
        
        self.scale_factor = 1  # Default scale factor

        if image.width > max_width or image.height > max_height:
            ratio = min(max_width / image.width, max_height / image.height)
            new_size = (int(image.width * ratio), int(image.height * ratio))
            self.scale_factor = ratio
            return image.resize(new_size, Image.Resampling.LANCZOS)
        else:
            return image

    def show_image(self):
        while self.current_image_index < len(self.images):
            image_path = os.path.join(self.folder_path, self.images[self.current_image_index])
            self.original_img = Image.open(image_path)

            # Check if the image is smaller than the specified dimensions
            if self.original_img.width < self.crop_box_width or self.original_img.height < self.crop_box_height:
                print(f"Ignored file (too small): {self.images[self.current_image_index]}")
                self.current_image_index += 1
                if self.current_image_index >= len(self.images):
                    print("No more images to display.")
                    return
            else:
                break

        self.canvas.delete("all")  # Clear previous image and rectangle
        self.crop_rect = None
        self.dragging = False

        pil_img = self.resize_image(self.original_img)
        self.img = ImageTk.PhotoImage(pil_img)
        self.canvas.create_image(0, 0, anchor='nw', image=self.img)

    def show_next_image(self):
        if self.current_image_index < len(self.images) - 1:
            self.current_image_index += 1
            self.show_image()

    def crop_image(self):
        save_path = 'C:/Users/sanve/Downloads/sw'
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        if self.crop_rect and self.original_img:
            x1, y1, x2, y2 = self.canvas.coords(self.crop_rect)
            real_x1, real_y1 = int(x1 / self.scale_factor), int(y1 / self.scale_factor)
            real_x2, real_y2 = real_x1 + self.crop_box_width, real_y1 + self.crop_box_height
            cropped_img = self.original_img.crop((real_x1, real_y1, real_x2, real_y2))

            base_filename = os.path.basename(self.images[self.current_image_index])
            cropped_filename = f"cropped_{base_filename}"
            cropped_img.save(os.path.join(save_path, cropped_filename))

            print(f"Image saved: {os.path.join(save_path, cropped_filename)}")
            self.show_next_image()


    def onFrameConfigure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def crop_image_event(self, event):
        self.crop_image()

def main():
    root = tk.Tk()
    root.title("Image Browser")
    root.state('zoomed')  # Maximize the window

    folder_path = 'C:/Users/sanve/Downloads/ew'
    app = ImageBrowser(root, folder_path)

    root.mainloop()

if __name__ == "__main__":
    main()
