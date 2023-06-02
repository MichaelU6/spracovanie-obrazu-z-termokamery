import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
import cv2 as cv
import pytesseract
import math


def processing_video(low, high, capt, outfile):
    def rgbKocka(size):
        dict = {}
        for r in range(size):
            for g in range(size):
                for b in range(size):
                    jednaKoc = 255 / size
                    dict[(r, g, b)] = (
                    (r * jednaKoc) + (jednaKoc / 2), (g * jednaKoc) + (jednaKoc / 2), (b * jednaKoc) + (jednaKoc / 2))
        return dict

    def euclidean_distance(color1, color2):
        r1, g1, b1 = color1
        r2, g2, b2 = color2
        distance = math.sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)
        return distance

    def find_nearest_color(rgb, color_scale):
        nearest_color = None
        min_distance = float('inf')

        for color in color_scale:
            distance = euclidean_distance(rgb, color["color"])
            if distance < min_distance:
                min_distance = distance
                nearest_color = color["value"]

        return nearest_color
    def findTemperaturValuesMinMax():
        height, width, channels = rgb.shape
        # constants for trimming
        w1_1 = width * 0.041
        w1_2 = width * 0.125
        h1 = height * 0.047
        h2_1 = height * 0.95
        crop_img_top = rgb[0:int(h1), int(w1_1):int(w1_2)]
        crop_img_bottom = rgb[int(h2_1) - 20:height - 1, int(w1_1):int(w1_2)]
        # creating a list containing output from tesseract
        options = "outputbase digits"
        zoz = [pytesseract.image_to_string(crop_img_top, config=options),
               pytesseract.image_to_string(crop_img_bottom, config=options)]
        # value management, error correction
        if len(zoz) == 2 and zoz[0][:-1].isnumeric() is True and zoz[1][:-1].isnumeric() is True:
            for i in range(len(zoz)):
                zoz[i] = int(zoz[i])
            return zoz
        else:
            return []

    def returnTemperature(x, y):
        idx = kocka[(rgb[x][y][0]//((255/sizeKocky)+0.1), rgb[x][y][1]//(255/sizeKocky+0.1), rgb[x][y][2]//(255/sizeKocky+0.1))]
        stupen_value = (height - 1) / (maxMin[0] - maxMin[1])
        return (idx // stupen_value) + maxMin[1]

    def process_frame(frame):
        # Creating a matrix of temperatures for each pixel
        x_coords, y_coords = np.meshgrid(np.arange(height), np.arange(width), indexing='ij')
        temperatures = np.vectorize(returnTemperature)(x_coords, y_coords)
        # Creating a color matrix based on temperatures
        colors = np.zeros_like(frame)
        colors[temperatures < stupenNajmensi] = green  # Green for low temperature
        colors[(temperatures >= stupenNajmensi) & (temperatures < stupenNajvecsi)] = yellow  # Yellow for medium temperature
        colors[temperatures >= stupenNajvecsi] = red  # Red for high temperature
        # Combining the original image with colors based on temperatures
        processed_frame = colors
        return processed_frame

    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract'
    # constants color
    green = [0, 255, 0]
    yellow = [0, 255, 255]
    red = [0, 0, 255]

    # optional degrees
    stupenNajmensi = low
    stupenNajvecsi = high

    cap = capt
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fourcc = cv.VideoWriter_fourcc(*'MJPG')
    out = cv.VideoWriter(outfile, fourcc, 10, (frame_width, frame_height))

    color_scale = []

    if not cap.isOpened():
        exit()

    while True:
        print("new frame")
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        maxMin = findTemperaturValuesMinMax()
        if maxMin != []:
            if color_scale == []:
                # Creating a scale
                x = 0
                col = [256, 256, 256]
                for i in reversed(rgb):
                    if col[0] != i[2][0] or col[1] != i[2][1] or col[2] != i[2][2]:
                        col = i[2]
                        color_scale.append({"color": i[2], "value": x})
                    x = x + 1
                    sizeKocky = 5
                kocka = rgbKocka(sizeKocky)
                for prvok in kocka:
                    sused = find_nearest_color(kocka[prvok], color_scale)
                    kocka[prvok] = sused

            height, width, channels = rgb.shape
            processed_frame = process_frame(rgb)
            out.write(processed_frame)
    cap.release()
    out.release()
    cv.destroyAllWindows()

def process_video():
    # Getting values from input fields
    lower_temp = lower_temp_entry.get()
    upper_temp = upper_temp_entry.get()
    output_path = output_path_entry.get()

    if not lower_temp or not upper_temp:
        # Checking the filling in of input values
        error_label.config(text="Teplotné hodnoty sú požadované!")
        return

    try:
        lower_temp = float(lower_temp)
        upper_temp = float(upper_temp)
    except ValueError:
        # Checking the correctness of input values
        error_label.config(text="Nesprávny rozsah teplôt!")
        return

    if lower_temp >= upper_temp:
        # Checking the correctness of input values
        error_label.config(text="Nesprávny rozsah teplôt!")
        return

    if not output_path:
        # Video placement check fill
        error_label.config(text="Vybratie miesta uloženia je požadované!")
        return

    # Selecting a video using the dialog file dialog
    video_file = filedialog.askopenfilename(filetypes=[("Video Files", "*.avi")])

    if video_file:
        # Video processing
        error_label.config(text="Prosím počkajte...")
        window.update()
        processing_video(lower_temp, upper_temp, cv2.VideoCapture(video_file), output_path + "/output.avi")
        # Display a notification that processing is complete
        error_label.config(text="")
        success_label.config(text="Video bolo úspešne dokončené.")

def select_output_path():
    # Selecting a folder to place the output video
    output_path = filedialog.askdirectory()
    output_path_entry.delete(0, tk.END)
    output_path_entry.insert(0, output_path)

def validate_number(value):
    if value.isdigit():
        return True
    elif value == "":
        return True
    else:
        return False

# Creating a GUI
window = tk.Tk()
window.configure(bg="#FFFFFF")

# Setting the name of the window
window.title("Video Processing Application")


# Creating a container for elements
container = tk.Frame(window, bg="#FFFFFF", highlightbackground="#D4AF37", highlightthickness=3)
container.pack(expand=True, pady=50)

# Creating labels for input values
lower_temp_label = tk.Label(container, text="Zadajte dolnú hranicu teploty pre spracovanie:")
lower_temp_label.configure(font=("Helvetica", 14, "bold"), fg="#333333", bg="#FFFFFF", pady=10)
lower_temp_label.pack(padx=10, pady=10)
lower_temp_entry = tk.Entry(container)
lower_temp_entry.configure(validate="key", validatecommand=(container.register(validate_number), "%P"))
lower_temp_entry.configure(font=("Arial", 12), bg="#FFFFFF", fg="#333333", bd=0, highlightthickness=2, highlightbackground="#CCCCCC")
lower_temp_entry.pack(pady=5)

upper_temp_label = tk.Label(container, text="Zadajte hornú hranicu teploty pre spracovanie:")
upper_temp_label.configure(font=("Helvetica", 14, "bold"), fg="#333333", bg="#FFFFFF", pady=10)
upper_temp_label.pack(pady=10)
upper_temp_entry = tk.Entry(container)
upper_temp_entry.configure(validate="key", validatecommand=(container.register(validate_number), "%P"))
upper_temp_entry.configure(font=("Arial", 12), bg="#FFFFFF", fg="#333333", bd=0, highlightthickness=2, highlightbackground="#CCCCCC")
upper_temp_entry.pack(pady=5)

select_output_button = tk.Button(container, text="Vyberte miesto na uloženie výstupu", command=select_output_path,
                                relief=tk.FLAT, bg="#4CAF50", fg="white", font=("Helvetica", 12))
select_output_button.pack(pady=10)
# Creating an input field for selecting an output folder
output_path_entry = tk.Entry(container, width=40)
output_path_entry.configure(font=("Arial", 12), bg="#FFFFFF", fg="#333333", bd=0, highlightthickness=2, highlightbackground="#CCCCCC")
output_path_entry.pack(pady=5)
process_button = tk.Button(container, text="Vyberte video", command=process_video,
                           relief=tk.FLAT, bg="#4CAF50", fg="white", font=("Helvetica", 12))
process_button.pack(pady=10)


# Creating a label for displaying errors
error_label = tk.Label(container, fg="red")
error_label.configure(font=("Helvetica", 14, "bold"), fg="red", bg="#FFFFFF", pady=10)
error_label.pack(pady=10)

# Creating a label to display the successful completion of processing
success_label = tk.Label(container, fg="green")
success_label.configure(font=("Helvetica", 14, "bold"), fg="green", bg="#FFFFFF", pady=10)
success_label.pack(pady=10)

# Getting the screen size
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()

# Calculation of window width and height
window_width = max(screen_width // 2, 500)
window_height = (screen_height // 2) + (screen_height // 4)

# Calculation of the position of the window to the center of the screen
x = (screen_width - window_width) // 2
y = (screen_height - window_height) // 2

# Setting the size and position of the window
window.geometry(f"{window_width}x{window_height}+{x}+{y}")

# Setting the minimum window width
window.minsize(500, window_height)

# Starting the GUI
window.mainloop()
