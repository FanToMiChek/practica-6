import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
from PIL import Image, ImageTk


class Processor:
    def __init__(self):
        self._image = None

    def load_image(self, path):
        self._image = cv2.imread(path)
        return self._image is not None

    def get_original(self):
        return self._image

    def get_new_size(self, border):
        if self._image is None:
            return None
        h, w = self._image.shape[:2]
        new_w = w + border * 2
        new_h = h + border * 2
        return w, h, new_w, new_h

    def apply_mirror_border(self, border):
        if self._image is None:
            return None
        return cv2.copyMakeBorder(
            self._image,
            border, border, border, border,
            cv2.BORDER_REFLECT
        )

    def save_image(self, path, image):
        """Записывает готовый файл на диск"""
        cv2.imwrite(path, image)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Вариант 15 — Рамка + Зеркальное отражение")
        self.geometry("900x600")
        self.resizable(False, False)

        self.processor = Processor()
        self.result_image = None

        self._build_notebook()
        self._build_controls()

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.tab_original = tk.Frame(self.notebook, bg="gray")
        self.tab_processed = tk.Frame(self.notebook, bg="gray")

        self.notebook.add(self.tab_original, text="Оригинал")
        self.notebook.add(self.tab_processed, text="Обработка")

        self.label_original = tk.Label(self.tab_original, bg="gray")
        self.label_original.pack(expand=True)

        self.label_processed = tk.Label(self.tab_processed, bg="gray")
        self.label_processed.pack(expand=True)

    def _build_controls(self):
        control_frame = tk.Frame(self, width=220, bg="#f0f0f0")
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        tk.Button(
            control_frame, text="Загрузить изображение",
            command=self._load_image, width=22
        ).pack(pady=10)

        tk.Label(control_frame, text="Толщина полей (пикс.):", bg="#f0f0f0").pack()
        self.border_scale = tk.Scale(
            control_frame, from_=10, to=60,
            orient=tk.HORIZONTAL, length=180,
            command=self._on_scale_change
        )
        self.border_scale.set(20)
        self.border_scale.pack(pady=5)

        self.size_label = tk.Label(
            control_frame, text="Размер: —",
            bg="#f0f0f0", wraplength=200
        )
        self.size_label.pack(pady=5)

        tk.Button(
            control_frame, text="Экспорт",
            command=self._export, width=22
        ).pack(pady=10)

    def _load_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not path:
            return
        if not self.processor.load_image(path):
            messagebox.showerror("Ошибка", "Не удалось загрузить изображение.")
            return
        self._show_image(self.processor.get_original(), self.label_original)
        self._process()

    def _on_scale_change(self, _=None):
        """При изменении ползунка — пересчитываем результат"""
        if self.processor.get_original() is not None:
            self._process()

    def _process(self):
        border = self.border_scale.get()
        sizes = self.processor.get_new_size(border)
        if sizes is None:
            return
        w, h, new_w, new_h = sizes
        self.size_label.config(
            text=f"Оригинал: {w}×{h}\nС рамкой: {new_w}×{new_h}"
        )
        self.result_image = self.processor.apply_mirror_border(border)
        self._show_image(self.result_image, self.label_processed)

    def _show_image(self, cv_img, label):
        rgb = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb)
        pil_img.thumbnail((660, 560))
        tk_img = ImageTk.PhotoImage(pil_img)
        label.config(image=tk_img)
        label.image = tk_img

    def _export(self):
        if self.result_image is None:
            messagebox.showwarning("Внимание", "Нет обработанного изображения.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg")]
        )
        if path:
            self.processor.save_image(path, self.result_image)
            messagebox.showinfo("Готово", f"Файл сохранён:\n{path}")


if __name__ == "__main__":
    app = App()
    app.mainloop()