# 🖼️ CircleMark: Batch Watermark Tool with Stroke

CircleMark adalah aplikasi desktop intuitif yang memungkinkan Anda menambahkan watermark gambar berbentuk bulat dengan efek stroke (garis tepi) ke banyak gambar sekaligus. Dibangun dengan Python menggunakan `tkinter` untuk GUI dan `Pillow` (PIL) untuk manipulasi gambar, CircleMark menyediakan pratinjau interaktif untuk penyesuaian watermark yang presisi sebelum proses batch.

---

## ✨ Fitur Utama

* **Watermark Bulat dengan Stroke:** Otomatis mengubah gambar watermark Anda menjadi bentuk bulat dengan garis tepi yang dapat disesuaikan.
* **Pratinjau Interaktif:** Lihat langsung bagaimana watermark akan terlihat pada gambar Anda, lengkap dengan fungsi *drag-and-drop* untuk posisi dan slider untuk ukuran, warna, serta ketebalan stroke.
* **Batch Processing:** Terapkan pengaturan watermark yang sama ke seluruh folder gambar dalam satu kali klik.
* **Fleksibilitas Posisi:** Sesuaikan posisi watermark secara presisi di mana pun pada gambar Anda.
* **Kustomisasi Penuh:** Kontrol ukuran watermark, warna stroke (RGB), dan ketebalan stroke.
* **Antarmuka Pengguna yang Mudah:** Desain GUI yang bersih dan *user-friendly* untuk pengalaman *watermarking* yang lancar.

---

## 🛠️ Instalasi

Pastikan Anda memiliki Python 3 terinstal di sistem Anda.
Kemudian, Anda dapat menginstal dependensi yang diperlukan menggunakan pip:

```bash
pip install Pillow
````

Setelah itu, Anda bisa menjalankan skrip `gui.py` secara langsung.

-----

## 🚀 Cara Menggunakan

1.  **Jalankan Aplikasi:**
    ```bash
    python gui.py
    ```
2.  **Pilih Folder Gambar Utama:** Klik tombol "Browse" di samping "Folder Gambar Utama" dan pilih folder yang berisi gambar-gambar yang ingin Anda beri watermark.
3.  **Pilih File Watermark:** Klik tombol "Browse" di samping "File Watermark (PNG)" dan pilih gambar PNG yang akan digunakan sebagai watermark.
4.  **Tentukan Folder Output:** Secara default, folder output akan diatur ke `~/Desktop/Watermarked_Images`. Anda bisa mengubahnya dengan mengklik "Browse" di samping "Folder Output".
5.  **Pratinjau & Sesuaikan Watermark:**
      * Klik tombol **"Preview Watermark"** untuk membuka jendela pratinjau.
      * Di jendela pratinjau, Anda akan melihat contoh gambar Anda dengan watermark.
      * **Drag & Drop** watermark untuk mengubah posisinya.
      * Gunakan slider **"Ukuran Watermark (px)"** untuk mengubah ukuran watermark.
      * Klik **"Pilih Warna"** untuk memilih warna stroke (garis tepi) watermark.
      * Gunakan slider **"Ketebalan Stroke (px)"** untuk mengubah ketebalan garis tepi.
      * Setelah puas dengan penyesuaian Anda, klik **"Save Preset"** untuk menyimpan pengaturan.
6.  **Buat Gambar dengan Watermark:**
      * Setelah menyimpan preset di jendela pratinjau, kembali ke jendela utama.
      * Klik tombol **"Generate Images"** untuk mulai menerapkan watermark ke semua gambar di folder input dan menyimpannya ke folder output.
7.  **Reset atau Keluar:**
      * Klik **"Reset"** untuk mengosongkan semua input dan mengembalikan preset ke nilai default.
      * Klik **"Exit"** untuk menutup aplikasi.

-----

## 🤝 Kontribusi

Jika Anda ingin berkontribusi pada proyek ini, silakan fork repositori dan ajukan pull request. Setiap saran dan peningkatan sangat kami hargai\!

-----

## 💖 Dukungan

Jika aplikasi ini bermanfaat bagi Anda, pertimbangkan untuk memberikan dukungan:

  * **Ko-fi:** [https://ko-fi.com/muchorio](https://ko-fi.com/muchorio)
  * **Trakteer:** [https://trakteer.id/muchorio/tip](https://trakteer.id/muchorio/tip)

Terima kasih atas dukungan Anda\! 🙏

-----

## 👨‍💻 Tentang MuchoRio

Proyek ini dikembangkan oleh [MuchoRio](https://www.google.com/search?q=https://github.com/MuchoRio).

```
```
