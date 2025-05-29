from PIL import Image, ImageTk, ImageDraw
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, colorchooser
import os

# --- KONSTANTA GLOBAL ---
DEFAULT_STROKE_THICKNESS = 5
DEFAULT_STROKE_COLOR_RGB = (255, 255, 255) # Default putih (RGB)
DEFAULT_STROKE_COLOR_HEX = "#FFFFFF" # Default putih (Hex)

# --- BAGIAN 1: Fungsi-fungsi Pemrosesan Gambar (Backend) ---

def proses_gambar_bulat_berstroke(foto_tumpang_path, target_pixel_size, warna_stroke_rgb, ketebalan_stroke):
    """
    Memproses gambar kecil: crop tengah (untuk menghindari gepeng), bulatkan, dan tambahkan stroke.
    target_pixel_size: (width, height) yang diinginkan untuk watermark FINAL dalam piksel.
    warna_stroke_rgb: Tuple (R, G, B) untuk warna stroke.
    ketebalan_stroke: Ketebalan garis tepi dalam piksel.
    Mengembalikan objek Image PIL yang sudah siap untuk ditempelkan.
    """
    try:
        foto_tumpang_asli = Image.open(foto_tumpang_path).convert("RGBA")

        # Pastikan ukuran target bulat adalah persegi
        if target_pixel_size[0] != target_pixel_size[1]:
            target_pixel_size = (target_pixel_size[0], target_pixel_size[0])

        if target_pixel_size[0] < 1 or target_pixel_size[1] < 1:
            raise ValueError("Ukuran target watermark terlalu kecil. Minimum 1x1 piksel.")

        lebar_asli, tinggi_asli = foto_tumpang_asli.size
        sisi_crop = min(lebar_asli, tinggi_asli)

        kiri = (lebar_asli - sisi_crop) / 2
        atas = (tinggi_asli - sisi_crop) / 2
        kanan = (lebar_asli + sisi_crop) / 2
        bawah = (tinggi_asli + sisi_crop) / 2

        foto_tumpang_cropped = foto_tumpang_asli.crop((kiri, atas, kanan, bawah))
        foto_tumpang_final_size = foto_tumpang_cropped.resize(target_pixel_size, Image.Resampling.LANCZOS)

        mask_gambar_utama = Image.new("L", target_pixel_size, 0)
        draw_gambar_utama = ImageDraw.Draw(mask_gambar_utama)
        draw_gambar_utama.ellipse((0, 0, target_pixel_size[0], target_pixel_size[1]), fill=255)

        foto_tumpang_bulat = Image.new("RGBA", target_pixel_size)
        foto_tumpang_bulat.paste(foto_tumpang_final_size, (0, 0), mask_gambar_utama)

        # Buat gambar stroke
        ukuran_stroke_kanvas = (target_pixel_size[0] + 2 * ketebalan_stroke,
                                target_pixel_size[1] + 2 * ketebalan_stroke)
        gambar_stroke = Image.new("RGBA", ukuran_stroke_kanvas, (0, 0, 0, 0)) # Latar belakang transparan
        draw_stroke = ImageDraw.Draw(gambar_stroke)

        # Ubah warna_stroke_rgb menjadi RGBA dengan alpha penuh (255)
        # PERBAIKAN DI SINI: Ubah (255,) menjadi [255] agar menjadi list
        warna_stroke_rgba = list(warna_stroke_rgb) + [255] # Ensure it's a list being concatenated with a list
        draw_stroke.ellipse((0, 0, ukuran_stroke_kanvas[0], ukuran_stroke_kanvas[1]), fill=tuple(warna_stroke_rgba)) # Fill needs tuple

        final_image_with_stroke = Image.new("RGBA", ukuran_stroke_kanvas) # Gunakan ukuran_stroke_kanvas di sini
        final_image_with_stroke.paste(gambar_stroke, (0, 0), gambar_stroke)
        final_image_with_stroke.paste(foto_tumpang_bulat, (ketebalan_stroke, ketebalan_stroke), foto_tumpang_bulat)

        return final_image_with_stroke

    except Exception as e:
        messagebox.showerror("Error Pemrosesan Watermark", f"Gagal memproses gambar watermark: {e}")
        return None

def aplikasikan_watermark_ke_gambar(gambar_dasar_path, watermark_pil_obj, posisi_x, posisi_y, output_folder):
    """
    Membuka gambar dasar, menempelkan watermark, dan menyimpannya ke folder output.
    """
    try:
        gambar_dasar = Image.open(gambar_dasar_path).convert("RGBA")

        if watermark_pil_obj is None:
            raise ValueError("Objek watermark tidak valid.")

        x_paste = posisi_x
        y_paste = posisi_y

        wm_width = watermark_pil_obj.width
        wm_height = watermark_pil_obj.height
        
        x_paste = max(0, min(x_paste, gambar_dasar.width - wm_width))
        y_paste = max(0, min(y_paste, gambar_dasar.height - wm_height))

        gambar_dasar.paste(watermark_pil_obj, (x_paste, y_paste), watermark_pil_obj)

        nama_file = os.path.basename(gambar_dasar_path)
        nama_tanpa_ekstensi, ekstensi = os.path.splitext(nama_file)
        output_path = os.path.join(output_folder, f"{nama_tanpa_ekstensi}_wm.png")

        gambar_dasar.save(output_path)
        return True
    except Exception as e:
        print(f"Gagal mengaplikasikan watermark ke {os.path.basename(gambar_dasar_path)}: {e}")
        return False

# --- BAGIAN 2: Kelas GUI Preview/Editor Watermark (Pop-up Window) ---

class WatermarkPreviewEditor:
    def __init__(self, master, app_instance, foto_dasar_example_path, foto_tumpang_path,
                 initial_posisi_original_coords, initial_wm_width_original_px,
                 initial_stroke_color_rgb, initial_stroke_thickness):
        self.master = master
        self.app_instance = app_instance
        self.foto_dasar_example_path = foto_dasar_example_path
        self.foto_tumpang_path = foto_tumpang_path

        self.initial_posisi_original_coords = initial_posisi_original_coords
        self.initial_wm_width_original_px = initial_wm_width_original_px
        
        # Pastikan ini adalah list untuk mutability dan konsistensi dengan concatenation
        self.current_stroke_color_rgb = list(initial_stroke_color_rgb) 
        self.current_stroke_color_hex = '#%02x%02x%02x' % tuple(initial_stroke_color_rgb) # Convert tuple to hex

        self.current_stroke_thickness = tk.IntVar(value=initial_stroke_thickness)

        self.top = tk.Toplevel(master)
        self.top.title("Preview & Edit Watermark")
        self.top.resizable(False, False)

        self.foto_dasar_pil = Image.open(foto_dasar_example_path).convert("RGBA")

        max_preview_width = 750
        max_preview_height = 550
        self.preview_scale_x = 1.0
        self.preview_scale_y = 1.0

        self.display_foto_dasar_pil = self.foto_dasar_pil.copy()
        if self.foto_dasar_pil.width > max_preview_width or self.foto_dasar_pil.height > max_preview_height:
            self.display_foto_dasar_pil.thumbnail((max_preview_width, max_preview_height), Image.Resampling.LANCZOS)
            self.preview_scale_x = self.foto_dasar_pil.width / self.display_foto_dasar_pil.width
            self.preview_scale_y = self.foto_dasar_pil.height / self.display_foto_dasar_pil.height
        
        self.foto_dasar_tk = ImageTk.PhotoImage(self.display_foto_dasar_pil)

        self.current_wm_width_original_px = tk.IntVar(value=initial_wm_width_original_px)
        
        initial_display_x = int(initial_posisi_original_coords[0] / self.preview_scale_x)
        initial_display_y = int(initial_posisi_original_coords[1] / self.preview_scale_y)

        self.current_pos_x_canvas = tk.IntVar(value=initial_display_x)
        self.current_pos_y_canvas = tk.IntVar(value=initial_display_y)

        self.canvas = tk.Canvas(self.top, width=self.display_foto_dasar_pil.width, height=self.display_foto_dasar_pil.height, bg="lightgray")
        self.canvas.pack(pady=5)
        self.canvas_bg_image = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.foto_dasar_tk)

        self.load_and_display_watermark()

        # Frame untuk kontrol
        control_frame = tk.Frame(self.top)
        control_frame.pack(pady=5)

        # Slider untuk Resize (Ukuran Watermark)
        tk.Label(control_frame, text="Ukuran Watermark (px):").grid(row=0, column=0, sticky="w", pady=2)
        max_wm_size_slider = min(self.foto_dasar_pil.width, self.foto_dasar_pil.height, 500)
        self.size_slider = ttk.Scale(control_frame, from_=20, to_=max_wm_size_slider, orient="horizontal",
                                     variable=self.current_wm_width_original_px, command=self.update_watermark_display, length=200)
        self.size_slider.grid(row=0, column=1, padx=5, sticky="ew")
        self.size_label = tk.Label(control_frame, text=f"{self.current_wm_width_original_px.get()}px")
        self.size_label.grid(row=0, column=2, padx=5, sticky="w")

        # Kontrol Warna Stroke
        tk.Label(control_frame, text="Warna Stroke:").grid(row=1, column=0, sticky="w", pady=2)
        self.color_display_frame = tk.Frame(control_frame, bg=self.current_stroke_color_hex, width=20, height=20, relief="solid", borderwidth=1)
        self.color_display_frame.grid(row=1, column=1, sticky="w", padx=5)
        tk.Button(control_frame, text="Pilih Warna", command=self.choose_stroke_color).grid(row=1, column=2, padx=5, sticky="w")

        # Kontrol Ketebalan Stroke
        tk.Label(control_frame, text="Ketebalan Stroke (px):").grid(row=2, column=0, sticky="w", pady=2)
        self.thickness_slider = ttk.Scale(control_frame, from_=0, to_=10, orient="horizontal",
                                         variable=self.current_stroke_thickness, command=self.update_watermark_display, length=200)
        self.thickness_slider.grid(row=2, column=1, padx=5, sticky="ew")
        self.thickness_label = tk.Label(control_frame, text=f"{self.current_stroke_thickness.get()}px")
        self.thickness_label.grid(row=2, column=2, padx=5, sticky="w")


        # Label Koordinat (menampilkan koordinat pada gambar asli)
        self.coords_label = tk.Label(self.top, text=f"Posisi: ({int(self.current_pos_x_canvas.get() * self.preview_scale_x)}, {int(self.current_pos_y_canvas.get() * self.preview_scale_y)})")
        self.coords_label.pack(pady=5)

        # Tombol Save Preset dan Cancel
        button_frame = tk.Frame(self.top)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Save Preset", command=self.save_preset).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancel", command=self.cancel_preview).pack(side=tk.LEFT, padx=10)

        # Binding event drag-and-drop
        self.canvas.tag_bind(self.draggable_watermark_id, "<ButtonPress-1>", self.on_drag_start)
        self.canvas.tag_bind(self.draggable_watermark_id, "<B1-Motion>", self.on_drag_motion)
        self.canvas.tag_bind(self.draggable_watermark_id, "<ButtonRelease-1>", self.on_drag_release)

        # Pastikan jendela berada di tengah master
        self.top.update_idletasks()
        x = master.winfo_x() + (master.winfo_width() // 2) - (self.top.winfo_width() // 2)
        y = master.winfo_y() + (master.winfo_height() // 2) - (self.top.winfo_height() // 2)
        self.top.geometry(f"+{x}+{y}")


    def load_and_display_watermark(self):
        """Memuat, memproses, dan menampilkan watermark di kanvas."""
        target_wm_size_original_px = (self.current_wm_width_original_px.get(), self.current_wm_width_original_px.get())
        
        if target_wm_size_original_px[0] < 10: target_wm_size_original_px = (10, 10) # Minimum size

        self.watermark_pil_actual_size = proses_gambar_bulat_berstroke(
            self.foto_tumpang_path,
            target_wm_size_original_px,
            tuple(self.current_stroke_color_rgb), # Pastikan ini tuple saat dipass ke fungsi
            self.current_stroke_thickness.get()
        )

        if self.watermark_pil_actual_size:
            display_wm_width = int(self.watermark_pil_actual_size.width / self.preview_scale_x)
            display_wm_height = int(self.watermark_pil_actual_size.height / self.preview_scale_y)

            if display_wm_width < 10: display_wm_width = 10
            if display_wm_height < 10: display_wm_height = 10

            self.watermark_pil_display_for_canvas = self.watermark_pil_actual_size.resize(
                (display_wm_width, display_wm_height), Image.Resampling.LANCZOS
            )
            self.watermark_tk = ImageTk.PhotoImage(self.watermark_pil_display_for_canvas)
            
            if hasattr(self, 'draggable_watermark_id') and self.draggable_watermark_id is not None:
                self.canvas.delete(self.draggable_watermark_id)

            self.draggable_watermark_id = self.canvas.create_image(
                self.current_pos_x_canvas.get(), self.current_pos_y_canvas.get(), anchor=tk.NW, image=self.watermark_tk
            )
            self.canvas.tag_bind(self.draggable_watermark_id, "<ButtonPress-1>", self.on_drag_start)
            self.canvas.tag_bind(self.draggable_watermark_id, "<B1-Motion>", self.on_drag_motion)
            self.canvas.tag_bind(self.draggable_watermark_id, "<ButtonRelease-1>", self.on_drag_release)
        else:
            messagebox.showerror("Error", "Gagal memuat watermark untuk preview.")
            self.top.destroy()

    def update_watermark_display(self, *args):
        """Dipanggil saat slider ukuran watermark digeser atau warna/ketebalan stroke berubah."""
        self.size_label.config(text=f"{self.current_wm_width_original_px.get()}px")
        self.thickness_label.config(text=f"{self.current_stroke_thickness.get()}px")
        self.load_and_display_watermark()
        self.constrain_watermark_position()
        
        x_orig = int(self.current_pos_x_canvas.get() * self.preview_scale_x)
        y_orig = int(self.current_pos_y_canvas.get() * self.preview_scale_y)
        self.coords_label.config(text=f"Posisi: ({x_orig}, {y_orig})")

    def choose_stroke_color(self):
        color_code = colorchooser.askcolor(title="Pilih Warna Stroke", initialcolor=self.current_stroke_color_hex)
        if color_code[1]:
            self.current_stroke_color_hex = color_code[1]
            self.current_stroke_color_rgb = list(color_code[0][:3])
            self.color_display_frame.config(bg=self.current_stroke_color_hex)
            self.update_watermark_display()

    def on_drag_start(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

        coords = self.canvas.coords(self.draggable_watermark_id)
        self.item_start_x_canvas = coords[0]
        self.item_start_y_canvas = coords[1]

    def on_drag_motion(self, event):
        dx = event.x - self.drag_start_x
        dy = event.y - self.drag_start_y

        new_x_canvas = self.item_start_x_canvas + dx
        new_y_canvas = self.item_start_y_canvas + dy

        wm_width_display = self.watermark_tk.width()
        wm_height_display = self.watermark_tk.height()
        
        new_x_canvas = max(0, min(new_x_canvas, self.canvas.winfo_width() - wm_width_display))
        new_y_canvas = max(0, min(new_y_canvas, self.canvas.winfo_height() - wm_height_display))

        self.canvas.coords(self.draggable_watermark_id, new_x_canvas, new_y_canvas)

        self.current_pos_x_canvas.set(int(new_x_canvas))
        self.current_pos_y_canvas.set(int(new_y_canvas))
        
        x_orig = int(new_x_canvas * self.preview_scale_x)
        y_orig = int(new_y_canvas * self.preview_scale_y)
        self.coords_label.config(text=f"Posisi: ({x_orig}, {y_orig})")

    def on_drag_release(self, event):
        coords = self.canvas.coords(self.draggable_watermark_id)
        self.current_pos_x_canvas.set(int(coords[0]))
        self.current_pos_y_canvas.set(int(coords[1]))
        
        x_orig = int(self.current_pos_x_canvas.get() * self.preview_scale_x)
        y_orig = int(self.current_pos_y_canvas.get() * self.preview_scale_y)
        self.coords_label.config(text=f"Posisi: ({x_orig}, {y_orig})")


    def constrain_watermark_position(self):
        """Memastikan watermark tetap berada di dalam batas kanvas setelah resize."""
        wm_width_display = self.watermark_tk.width()
        wm_height_display = self.watermark_tk.height()

        current_x_canvas = self.canvas.coords(self.draggable_watermark_id)[0] if self.draggable_watermark_id else 0
        current_y_canvas = self.canvas.coords(self.draggable_watermark_id)[1] if self.draggable_watermark_id else 0

        # Batasi posisi x
        if current_x_canvas + wm_width_display > self.canvas.winfo_width():
            current_x_canvas = self.canvas.winfo_width() - wm_width_display
        if current_x_canvas < 0:
            current_x_canvas = 0

        # Batasi posisi y
        if current_y_canvas + wm_height_display > self.canvas.winfo_height():
            current_y_canvas = self.canvas.winfo_height() - wm_height_display
        if current_y_canvas < 0:
            current_y_canvas = 0
        
        self.canvas.coords(self.draggable_watermark_id, current_x_canvas, current_y_canvas)
        self.current_pos_x_canvas.set(int(current_x_canvas))
        self.current_pos_y_canvas.set(int(current_y_canvas))


    def save_preset(self):
        """Menyimpan pengaturan watermark dan menutup jendela preview."""
        self.app_instance.watermark_preset = {
            "posisi_x": int(self.current_pos_x_canvas.get() * self.preview_scale_x),
            "posisi_y": int(self.current_pos_y_canvas.get() * self.preview_scale_y),
            "watermark_width_px": self.current_wm_width_original_px.get(),
            "stroke_color_rgb": tuple(self.current_stroke_color_rgb), # Pastikan disimpan sebagai tuple
            "stroke_thickness": self.current_stroke_thickness.get()
        }
        messagebox.showinfo("Preset Tersimpan", "Pengaturan watermark telah disimpan.")
        self.top.destroy()

    def cancel_preview(self):
        """Membatalkan dan menutup jendela preview tanpa menyimpan preset."""
        self.top.destroy()

# --- BAGIAN 3: Kelas GUI Utama ---

class WatermarkApp:
    def __init__(self, master):
        self.master = master
        master.title("Batch Image Watermarker")
        master.geometry("500x400")
        master.resizable(False, False)

        # Default preset values (will be used if no preset is saved yet)
        self.watermark_preset = {
            "posisi_x": 20,
            "posisi_y": 20,
            "watermark_width_px": 150,
            "stroke_color_rgb": DEFAULT_STROKE_COLOR_RGB,
            "stroke_thickness": DEFAULT_STROKE_THICKNESS
        }

        self.input_folder_path = tk.StringVar()
        self.watermark_file_path = tk.StringVar()
        self.output_folder_path = tk.StringVar()

        self.output_folder_path.set(os.path.join(os.path.expanduser("~"), "Desktop", "Watermarked_Images"))

        # --- Frame Input ---
        input_frame = tk.LabelFrame(master, text="Pengaturan Input", padx=10, pady=10)
        input_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(input_frame, text="Folder Gambar Utama:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_input_folder = tk.Entry(input_frame, textvariable=self.input_folder_path, width=40)
        self.entry_input_folder.grid(row=0, column=1, padx=5)
        tk.Button(input_frame, text="Browse", command=self.browse_input_folder).grid(row=0, column=2)

        tk.Label(input_frame, text="File Watermark (PNG):").grid(row=1, column=0, sticky="w", pady=5)
        self.entry_watermark_file = tk.Entry(input_frame, textvariable=self.watermark_file_path, width=40)
        self.entry_watermark_file.grid(row=1, column=1, padx=5)
        tk.Button(input_frame, text="Browse", command=self.browse_watermark_file).grid(row=1, column=2)

        # --- Frame Output ---
        output_frame = tk.LabelFrame(master, text="Pengaturan Output", padx=10, pady=10)
        output_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(output_frame, text="Folder Output:").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_output_folder = tk.Entry(output_frame, textvariable=self.output_folder_path, width=40)
        self.entry_output_folder.grid(row=0, column=1, padx=5)
        tk.Button(output_frame, text="Browse", command=self.browse_output_folder).grid(row=0, column=2)

        # --- Tombol Aksi ---
        action_frame = tk.Frame(master, padx=10, pady=10)
        action_frame.pack(pady=10)

        self.preview_button = tk.Button(action_frame, text="Preview Watermark", command=self.open_preview, bg="lightblue", fg="white")
        self.preview_button.pack(side=tk.LEFT, padx=5)

        self.generate_button = tk.Button(action_frame, text="Generate Images", command=self.generate_images, bg="green", fg="white")
        self.generate_button.pack(side=tk.LEFT, padx=5)

        self.reset_button = tk.Button(action_frame, text="Reset", command=self.reset_inputs, bg="orange", fg="white")
        self.reset_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(action_frame, text="Exit", command=master.quit, bg="red", fg="white")
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        # Status Label
        self.status_label = tk.Label(master, text="Siap.", fg="blue")
        self.status_label.pack(pady=5)

    def browse_input_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.input_folder_path.set(folder_selected)

    def browse_watermark_file(self):
        file_selected = filedialog.askopenfilename(filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_selected:
            self.watermark_file_path.set(file_selected)

    def browse_output_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.output_folder_path.set(folder_selected)
            if not os.path.exists(folder_selected):
                os.makedirs(folder_selected)

    def open_preview(self):
        input_folder = self.input_folder_path.get()
        watermark_file = self.watermark_file_path.get()

        if not input_folder or not os.path.isdir(input_folder):
            messagebox.showwarning("Input Error", "Silakan pilih folder gambar utama yang valid.")
            return
        if not watermark_file or not os.path.isfile(watermark_file):
            messagebox.showwarning("Input Error", "Silakan pilih file watermark yang valid.")
            return

        list_gambar = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        if not list_gambar:
            messagebox.showwarning("Tidak Ada Gambar", "Tidak ada gambar yang ditemukan di folder input yang dipilih.")
            return

        example_image_path = os.path.join(input_folder, list_gambar[0])

        initial_pos_orig = (self.watermark_preset["posisi_x"], self.watermark_preset["posisi_y"])
        initial_wm_width_orig_px = self.watermark_preset["watermark_width_px"]
        initial_stroke_color = self.watermark_preset["stroke_color_rgb"]
        initial_stroke_thickness = self.watermark_preset["stroke_thickness"]

        WatermarkPreviewEditor(self.master, self, example_image_path, watermark_file,
                               initial_posisi_original_coords=initial_pos_orig,
                               initial_wm_width_original_px=initial_wm_width_orig_px,
                               initial_stroke_color_rgb=initial_stroke_color,
                               initial_stroke_thickness=initial_stroke_thickness)


    def generate_images(self):
        input_folder = self.input_folder_path.get()
        watermark_file = self.watermark_file_path.get()
        output_folder = self.output_folder_path.get()

        if not input_folder or not os.path.isdir(input_folder):
            messagebox.showwarning("Input Error", "Silakan pilih folder gambar utama yang valid.")
            return
        if not watermark_file or not os.path.isfile(watermark_file):
            messagebox.showwarning("Input Error", "Silakan pilih file watermark yang valid.")
            return
        if not output_folder or not os.path.isdir(output_folder):
            messagebox.showwarning("Input Error", "Silakan pilih folder output yang valid.")
            return
        if not self.watermark_preset:
            messagebox.showwarning("Preset Belum Disimpan", "Harap gunakan 'Preview Watermark' dan 'Save Preset' terlebih dahulu.")
            return

        self.status_label.config(text="Memulai generasi gambar...", fg="blue")
        self.master.update_idletasks()

        posisi_x = self.watermark_preset["posisi_x"]
        posisi_y = self.watermark_preset["posisi_y"]
        target_wm_width_final = self.watermark_preset["watermark_width_px"]
        stroke_color_final = self.watermark_preset["stroke_color_rgb"]
        stroke_thickness_final = self.watermark_preset["stroke_thickness"]
        
        processed_watermark_obj = proses_gambar_bulat_berstroke(
            watermark_file, (target_wm_width_final, target_wm_width_final),
            warna_stroke_rgb=stroke_color_final, ketebalan_stroke=stroke_thickness_final
        )

        if not processed_watermark_obj:
            messagebox.showerror("Error", "Gagal memproses watermark. Tidak dapat melanjutkan.")
            self.status_label.config(text="Gagal.", fg="red")
            return

        list_gambar = [f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
        if not list_gambar:
            messagebox.showwarning("Tidak Ada Gambar", "Tidak ada gambar yang ditemukan di folder input yang dipilih.")
            self.status_label.config(text="Selesai (Tidak ada gambar diproses).", fg="orange")
            return

        processed_count = 0
        for i, gambar_file in enumerate(list_gambar):
            gambar_path = os.path.join(input_folder, gambar_file)
            self.status_label.config(text=f"Memproses: {gambar_file} ({i+1}/{len(list_gambar)})...", fg="blue")
            self.master.update_idletasks()
            
            if aplikasikan_watermark_ke_gambar(gambar_path, processed_watermark_obj, posisi_x, posisi_y, output_folder):
                processed_count += 1
        
        messagebox.showinfo("Selesai", f"{processed_count} gambar berhasil diberi watermark dan disimpan di '{output_folder}'.")
        self.status_label.config(text="Selesai.", fg="green")

    def reset_inputs(self):
        self.input_folder_path.set("")
        self.watermark_file_path.set("")
        self.output_folder_path.set(os.path.join(os.path.expanduser("~"), "Desktop", "Watermarked_Images"))
        self.watermark_preset = {
            "posisi_x": 20,
            "posisi_y": 20,
            "watermark_width_px": 150,
            "stroke_color_rgb": DEFAULT_STROKE_COLOR_RGB,
            "stroke_thickness": DEFAULT_STROKE_THICKNESS
        }
        self.status_label.config(text="Siap.", fg="blue")
        messagebox.showinfo("Reset", "Semua input telah direset.")


# --- Jalankan Aplikasi ---
if __name__ == "__main__":
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()
