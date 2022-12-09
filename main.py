from ctypes import windll
import os
from tkinter import messagebox, ttk
import tkinter as tk
import sys

windll.shcore.SetProcessDpiAwareness(1)

chrome_paths = [
    "%ProgramFiles%\\Google\\Chrome\\Application\\chrome.exe",
    "%ProgramFiles(x86)%\\Google\\Chrome\\Application\\chrome.exe",
    "%LocalAppData%\\Google\\Chrome\\Application\\chrome.exe"
]

chrome_exists = False

for path in chrome_paths:
    complete_path = os.path.expandvars(path)
    if os.path.isfile(complete_path):
        chrome_exists = True
        break
else:
    messagebox.showerror("Error", "Google Chrome installation not found. Please install Google Chrome and try again.")

if chrome_exists:
    try:
        base_path = sys._MEIPASS
        os.chdir(base_path)
    except AttributeError:
        pass

    root = tk.Tk()

    win_width = 300
    win_height = 100
    win_pos_x = (root.winfo_screenwidth() - win_width) // 2
    win_pos_y = (root.winfo_screenheight() - win_height - 48) // 2
    root.geometry(f"{win_width}x{win_height}+{win_pos_x}+{win_pos_y}")
    root.resizable(0, 0)
    root.protocol("WM_DELETE_WINDOW", lambda: False)
    root.iconbitmap("images/blank.ico")
    root.title("")
    root.configure(bg="#F7F0F0")

    frame = tk.Frame(root, background="#F7F0F0")

    favicon_image = tk.PhotoImage(file="images/favicon.png")
    favicon_label = tk.Label(frame, image=favicon_image, background="#F7F0F0")
    favicon_label.grid(row=0, column=0, rowspan=2)

    loading_image = tk.PhotoImage(file="images/loading.png")
    loading_label = tk.Label(frame, image=loading_image, background="#F7F0F0")
    loading_label.grid(row=0, column=1)

    style = ttk.Style()
    style.theme_use("alt")
    style.configure("Horizontal.TProgressbar", background="#484349", troughcolor="#D4D4D4")

    progress = tk.IntVar(value=0)

    def update_progress(value):
        progress.set(value)
        root.update_idletasks()

    prog_bar = ttk.Progressbar(frame, mode="determinate", length=180, variable=progress)
    prog_bar.grid(row=1, column=1, padx=10)

    frame.pack(expand=True)

    def main():
        import eel
        update_progress(10)
        from tkinter import filedialog
        update_progress(20)
        import cv2
        update_progress(30)
        import numpy as np
        update_progress(40)
        from scipy.fft import rfft
        update_progress(50)
        from matplotlib import pyplot as plt
        update_progress(60)
        import mpld3
        update_progress(70)
        import csv
        update_progress(80)

        def waveform_from_image(path, thresh=45):
            img = cv2.imread(path)
            img_sat = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)[:, :, 1]
            _, mask = cv2.threshold(img_sat, thresh, 255, cv2.THRESH_BINARY)

            mask_transposed = np.transpose(mask)
            y_vals = []
            for row in mask_transposed:
                cand_y_vals = []
                for index, val in enumerate(row):
                    if val == 255:
                        cand_y_vals.append(index)
                if cand_y_vals:
                    y_vals.append(cand_y_vals[len(cand_y_vals)//2])

            waveform = np.array(y_vals)
            waveform -= waveform[0]
            waveform *= -1
            waveform = waveform / waveform.max()

            return waveform

        def fourier_transform(waveform):
            harmonics = np.abs(rfft(waveform))
            harmonics = harmonics / harmonics.max()
            harm_dict = {}
            for harmonic in range(1, harmonics.shape[0], 2):
                amplitude = harmonics[harmonic]
                if amplitude > 0.01:
                    harm_dict[harmonic] = amplitude
            return harm_dict

        def generate_sine_wave(harm, no_of_pts):
            x = np.linspace(0, 2*np.pi, no_of_pts)
            y = np.sin(harm*x)
            return y

        def generate_waveform(harm_dict, no_of_pts):
            waveform = np.zeros((no_of_pts,))
            for harm, amp in harm_dict.items():
                waveform += generate_sine_wave(harm, no_of_pts) * amp
            return waveform

        def distribution_factor(n, alpha, r=1):
            alpha *= np.pi/180
            return np.sin(n*alpha*r/2)/(n*np.sin(alpha*r/2))

        def pitch_factor(rho, r=1):
            rho *= np.pi/180
            return np.cos(rho*r/2)

        def flux_density_to_induced_emf(fd_harm_dict, n, alpha, rho):
            emf_harm_dict = {1: 1.0}
            fd_1 = fd_harm_dict['1']
            k_b1 = distribution_factor(n, alpha)
            k_p1 = pitch_factor(rho)
            for r, fd_r in list(fd_harm_dict.items())[1:]:
                r = int(r)
                k_br = distribution_factor(n, alpha, r)
                k_pr = pitch_factor(rho, r)
                emf_r = (fd_r*k_br*k_pr)/(fd_1*k_b1*k_p1)
                emf_harm_dict[r] = emf_r
            return emf_harm_dict

        def on_close(closed_page, open_websockets):
            sys.exit()

        update_progress(90)

        @eel.expose
        def get_file_path(title, file_flags):
            root = tk.Tk()
            root.attributes("-alpha", 0.0)
            root.iconbitmap("web/images/favicon.ico")
            root.withdraw()
            root.wm_attributes('-topmost', 1)
            file = filedialog.askopenfile(
                initialdir=os.path.expanduser("~/Desktop"),
                title=title,
                filetypes=file_flags,
            )
            if file is not None:
                return file.name

        @eel.expose
        def create_input_plot(path, input_type):
            if input_type == "Image":
                harm_dict = fourier_transform(waveform_from_image(path))
            else:
                harm_dict = fourier_transform(waveform_from_csv(path))
            waveform = generate_waveform(harm_dict, 200)
            x_axis = np.linspace(0, 2*np.pi, len(waveform))
            fig = plt.figure(figsize=(9, 4))
            plt.plot(x_axis, waveform)
            plt.xlabel("Space Angle", color="#484349", fontsize=14)
            plt.ylabel("Flux Density", color="#484349", fontsize=14)
            plt.title("INPUT PLOT", color="#484349", fontsize=24)
            json_data = mpld3.fig_to_dict(fig)
            return harm_dict, json_data

        @eel.expose
        def create_output_plot(harm_dict, n, alpha, rho):
            waveform = generate_waveform(flux_density_to_induced_emf(harm_dict, n, alpha, rho), 200)
            x_axis = np.linspace(0, 2*np.pi, len(waveform))
            fig = plt.figure(figsize=(9, 4))
            plt.plot(x_axis, waveform)
            plt.xlabel("Time Phase Angle", color="#484349", fontsize=14)
            plt.ylabel("Induced EMF", color="#484349", fontsize=14)
            plt.title("OUTPUT PLOT", color="#484349", fontsize=24)
            json_data = mpld3.fig_to_dict(fig)
            return json_data

        def check_num(string):
            try:
                float(string)
            except ValueError:
                return False
            else:
                return True

        @eel.expose
        def waveform_from_csv(path):
            vals = []
            i = 0
            with open(path, newline="") as file:
                csv_reader = csv.reader(file, delimiter=",")
                first_row = next(csv_reader)
                if len(first_row) == 2:
                    i = 1
                if check_num(first_row[i]):
                    vals.append(float(first_row[i]))
                for row in csv_reader:
                    vals.append(float(row[i]))

                waveform = np.array(vals)
                waveform = waveform / waveform.max()
                return waveform

        update_progress(100)

        eel.init("web")
        eel.start(
            "index.htm",
            mode="chrome",
            size=(1050, 750),
            close_callback=on_close,
            disable_cache=True,
            cmdline_args=["--incognito"],
            block=False
        )

        root.destroy()

        while True:
            eel.sleep(1.0)

    root.after(50, main)
    root.mainloop()
