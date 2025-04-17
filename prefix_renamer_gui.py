import os
import threading
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext


class PrefixRenamerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Prefix File Renamer")
        self.root.geometry("700x500")
        self.root.resizable(True, True)

        # Biến để lưu trữ đường dẫn và prefix
        self.folder_path = tk.StringVar()
        self.prefix = tk.StringVar()
        self.status = tk.StringVar()
        self.status.set("Sẵn sàng")
        self.total_files = 0
        self.processed_files = 0

        # Tạo và cấu hình các widget
        self.create_widgets()

    def create_widgets(self):
        # Frame cho phần nhập liệu
        input_frame = ttk.LabelFrame(self.root, text="Thông tin đầu vào")
        input_frame.pack(fill="x", padx=10, pady=10)

        # Chọn thư mục
        ttk.Label(input_frame, text="Đường dẫn thư mục:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.folder_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Duyệt...", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        # Nhập prefix
        ttk.Label(input_frame, text="Prefix:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(input_frame, textvariable=self.prefix, width=50).grid(row=1, column=1, padx=5, pady=5)

        # Nút thực hiện
        ttk.Button(input_frame, text="Đổi tên files", command=self.start_renaming).grid(row=2, column=1, pady=10)

        # Progress bar và status
        progress_frame = ttk.LabelFrame(self.root, text="Tiến trình")
        progress_frame.pack(fill="x", padx=10, pady=5)

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=5)

        ttk.Label(progress_frame, textvariable=self.status).pack(anchor="w", padx=10, pady=2)

        # Khu vực log
        log_frame = ttk.LabelFrame(self.root, text="Kết quả")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, width=80, height=15)
        self.log_area.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_area.config(state=tk.DISABLED)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)

    def log_message(self, message):
        self.log_area.config(state=tk.NORMAL)
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)
        self.log_area.config(state=tk.DISABLED)
        self.root.update_idletasks()

    def start_renaming(self):
        # Kiểm tra dữ liệu nhập vào
        folder_path = self.folder_path.get().strip()
        prefix = self.prefix.get().strip()

        if not folder_path or not os.path.isdir(folder_path):
            self.log_message("Lỗi: Đường dẫn thư mục không hợp lệ!")
            return

        if not prefix:
            self.log_message("Lỗi: Prefix không được để trống!")
            return

        # Xóa nội dung log cũ
        self.log_area.config(state=tk.NORMAL)
        self.log_area.delete(1.0, tk.END)
        self.log_area.config(state=tk.DISABLED)

        # Bắt đầu tiến trình đổi tên trong một thread riêng
        threading.Thread(target=self.rename_files_with_prefix, args=(folder_path, prefix)).start()

    def rename_files_with_prefix(self, folder_path, prefix):
        try:
            # Lấy danh sách tất cả các file trong thư mục
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            self.total_files = len(files)
            self.processed_files = 0

            if self.total_files == 0:
                self.status.set("Không tìm thấy file nào trong thư mục này.")
                self.log_message("Không tìm thấy file nào trong thư mục này.")
                return

            self.progress_bar["maximum"] = self.total_files
            self.progress_bar["value"] = 0

            self.log_message(f"Tìm thấy {self.total_files} file trong thư mục.")
            self.log_message("Bắt đầu quá trình đổi tên...\n")

            renamed_count = 0
            skipped_count = 0

            # Xử lý từng file
            for filename in files:
                file_path = os.path.join(folder_path, filename)

                # Kiểm tra xem prefix đã tồn tại trong tên file chưa
                if not filename.startswith(prefix):
                    # Tạo tên file mới
                    new_filename = prefix + filename
                    new_file_path = os.path.join(folder_path, new_filename)

                    # Đổi tên file
                    try:
                        os.rename(file_path, new_file_path)
                        self.log_message(f"Đã đổi tên: {filename} -> {new_filename}")
                        renamed_count += 1
                    except Exception as e:
                        self.log_message(f"Lỗi khi đổi tên file '{filename}': {str(e)}")
                else:
                    self.log_message(f"Bỏ qua file '{filename}' vì đã có prefix '{prefix}'")
                    skipped_count += 1

                # Cập nhật tiến trình
                self.processed_files += 1
                self.progress_bar["value"] = self.processed_files
                self.status.set(f"Đã xử lý: {self.processed_files}/{self.total_files}")
                self.root.update_idletasks()

            # Hoàn thành
            self.status.set(f"Hoàn thành! Đã đổi tên {renamed_count} file, bỏ qua {skipped_count} file.")
            self.log_message(f"\nĐã hoàn thành! Đã đổi tên {renamed_count} file, bỏ qua {skipped_count} file.")

        except Exception as e:
            self.status.set("Đã xảy ra lỗi!")
            self.log_message(f"Lỗi: {str(e)}")


def main():
    root = tk.Tk()
    app = PrefixRenamerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
