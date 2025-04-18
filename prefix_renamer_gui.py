import json
import os
import threading
import tkinter as tk
import webbrowser
from datetime import datetime
from tkinter import filedialog, ttk
from tkinter import messagebox
from tkinter import PhotoImage
from PIL import Image, ImageTk

class PrefixRenamerApp:
    def __init__(self, root):
        self.logo_image = None
        self.root = root
        self.root.title("Prefix File Renamer")
        self.root.geometry("900x650")
        self.root.resizable(True, True)

        # Màu sắc và phong cách
        self.bg_color = "#f5f5f5"
        self.accent_color = "#3498db"
        self.button_color = "#2980b9"
        self.success_color = "#2ecc71"
        self.warning_color = "#f39c12"
        self.error_color = "#e74c3c"

        # Thiết lập style cho ttk
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background=self.bg_color)
        self.style.configure('TLabelframe', background=self.bg_color)
        self.style.configure('TLabelframe.Label', background=self.bg_color, font=('Arial', 10, 'bold'))
        self.style.configure('TButton', background=self.button_color, foreground='white', font=('Arial', 10))
        self.style.configure('Success.TButton', background=self.success_color)
        self.style.map('TButton', background=[('active', '#3498db')])
        self.style.configure('TLabel', background=self.bg_color, font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))

        # Biến để lưu trữ đường dẫn và prefix
        self.folder_path = tk.StringVar()
        self.prefix = tk.StringVar()
        self.status = tk.StringVar()
        self.status.set("Sẵn sàng")
        self.total_files = 0
        self.processed_files = 0

        # Tải các prefix đã lưu
        self.recent_prefixes = self.load_recent_prefixes()

        # Biến cho chế độ xem trước
        self.preview_mode = tk.BooleanVar(value=True)

        # Icons (sử dụng mã Unicode cho các biểu tượng cơ bản)
        self.icons = {
            'folder': "📁",
            'file': "📄",
            'edit': "✏️",
            'start': "▶️",
            'settings': "⚙️",
            'preview': "👁️",
            'save': "💾",
            'history': "🕒",
            'help': "❓",
            'github': "🔗",
            'success': "✅",
            'error': "❌",
            'warning': "⚠️",
            'info': "ℹ️"
        }

        # Thiết lập giao diện
        self.setup_ui()

    def setup_ui(self):
        self.root.configure(bg=self.bg_color)

        # Frame chính
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill="both", expand=True)

        # Header với logo và tiêu đề
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill="x", pady=(0, 10))

        # Load và resize logo
        original_logo = Image.open("assets/logo.png")
        resized_logo = original_logo.resize((40, 40), Image.Resampling.LANCZOS)  # dùng LANCZOS để thay cho ANTIALIAS
        self.logo_image = ImageTk.PhotoImage(resized_logo)

        # Hiển thị
        logo_label = tk.Label(header_frame, image=self.logo_image, background=self.bg_color)
        logo_label.pack(side="left", padx=(0, 10))

        # Tiêu đề
        title_label = ttk.Label(header_frame, text="Prefix File Renamer", style="Header.TLabel",
                                font=('Arial', 16, 'bold'))
        title_label.pack(side="left")

        github_button = ttk.Button(header_frame, text=f"{self.icons['github']} GitHub", command=self.open_github)
        github_button.pack(side="right", padx=5)

        help_button = ttk.Button(header_frame, text=f"{self.icons['help']} Trợ giúp", command=self.show_help)
        help_button.pack(side="right", padx=5)

        # Input frame
        input_frame = ttk.LabelFrame(main_frame, text="Thông tin đầu vào")
        input_frame.pack(fill="x", pady=10)

        # Chọn thư mục
        folder_frame = ttk.Frame(input_frame)
        folder_frame.pack(fill="x", padx=10, pady=5)

        folder_label = ttk.Label(folder_frame, text=f"{self.icons['folder']} Thư mục:")
        folder_label.pack(side="left", padx=(0, 5))

        folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=60)
        folder_entry.pack(side="left", fill="x", expand=True, padx=5)

        browse_button = ttk.Button(folder_frame, text="Duyệt...", command=self.browse_folder)
        browse_button.pack(side="left", padx=5)

        # Nhập prefix
        prefix_frame = ttk.Frame(input_frame)
        prefix_frame.pack(fill="x", padx=10, pady=5)

        prefix_label = ttk.Label(prefix_frame, text=f"{self.icons['edit']} Prefix:")
        prefix_label.pack(side="left", padx=(0, 5))

        self.prefix_combobox = ttk.Combobox(prefix_frame, textvariable=self.prefix, width=40)
        self.prefix_combobox['values'] = self.recent_prefixes
        self.prefix_combobox.pack(side="left", fill="x", expand=True, padx=5)

        save_prefix_button = ttk.Button(prefix_frame, text=f"{self.icons['save']} Lưu prefix", command=self.save_prefix)
        save_prefix_button.pack(side="left", padx=5)

        # Frame chứa các tuỳ chọn
        options_frame = ttk.Frame(input_frame)
        options_frame.pack(fill="x", padx=10, pady=5)

        preview_check = ttk.Checkbutton(options_frame, text=f"{self.icons['preview']} Xem trước",
                                        variable=self.preview_mode)
        preview_check.pack(side="left", padx=5)

        # Nút thực hiện
        action_frame = ttk.Frame(input_frame)
        action_frame.pack(fill="x", padx=10, pady=10)

        self.rename_button = ttk.Button(action_frame, text=f"{self.icons['start']} Bắt đầu đổi tên",
                                        command=self.start_process, style='Success.TButton')
        self.rename_button.pack(side="right", padx=5)

        # Progress bar và status
        progress_frame = ttk.LabelFrame(main_frame, text="Tiến trình")
        progress_frame.pack(fill="x", pady=10)

        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", length=100, mode="determinate")
        self.progress_bar.pack(fill="x", padx=10, pady=5)

        status_frame = ttk.Frame(progress_frame)
        status_frame.pack(fill="x", padx=10, pady=2)

        status_icon = ttk.Label(status_frame, text=f"{self.icons['info']}")
        status_icon.pack(side="left")

        status_label = ttk.Label(status_frame, textvariable=self.status)
        status_label.pack(side="left", padx=5)

        # Khu vực hiển thị kết quả dạng bảng
        results_frame = ttk.LabelFrame(main_frame, text="Kết quả")
        results_frame.pack(fill="both", expand=True, pady=10)

        # Tạo Treeview để hiển thị dữ liệu dạng bảng
        columns = ('status', 'original_name', 'new_name')
        self.result_table = ttk.Treeview(results_frame, columns=columns, show='headings')

        # Định nghĩa các cột
        self.result_table.heading('status', text='Trạng thái')
        self.result_table.heading('original_name', text='Tên gốc')
        self.result_table.heading('new_name', text='Tên mới')

        self.result_table.column('status', width=100, anchor='center')
        self.result_table.column('original_name', width=300)
        self.result_table.column('new_name', width=300)

        # Tạo scrollbar
        table_scroll_y = ttk.Scrollbar(results_frame, orient="vertical", command=self.result_table.yview)
        table_scroll_x = ttk.Scrollbar(results_frame, orient="horizontal", command=self.result_table.xview)
        self.result_table.configure(yscrollcommand=table_scroll_y.set, xscrollcommand=table_scroll_x.set)

        # Đặt vị trí các thành phần
        table_scroll_y.pack(side="right", fill="y")
        table_scroll_x.pack(side="bottom", fill="x")
        self.result_table.pack(fill="both", expand=True)

        # Footer với thông tin bản quyền
        footer_frame = ttk.Frame(main_frame)
        footer_frame.pack(fill="x", pady=5)

        footer_label = ttk.Label(footer_frame, text="© 2025 vulct174 | Prefix File Renamer", foreground="#777")
        footer_label.pack(side="left")

        # Tag cho hiển thị màu trong bảng
        self.result_table.tag_configure('success', background='#e8f8f5')
        self.result_table.tag_configure('warning', background='#fef9e7')
        self.result_table.tag_configure('error', background='#fadbd8')

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            # Nếu ở chế độ xem trước, tự động hiển thị xem trước khi chọn thư mục mới
            if self.preview_mode.get() and self.prefix.get().strip():
                self.preview_renaming()

    def load_recent_prefixes(self):
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prefix_history.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    data = json.load(f)
                    return data.get("prefixes", [])
        except Exception:
            pass
        return []

    def save_prefix(self):
        prefix = self.prefix.get().strip()
        if not prefix:
            return

        # Thêm prefix mới vào đầu danh sách và giữ lại tối đa 10 prefix
        if prefix in self.recent_prefixes:
            self.recent_prefixes.remove(prefix)
        self.recent_prefixes.insert(0, prefix)
        self.recent_prefixes = self.recent_prefixes[:10]  # Giữ lại 10 prefix gần nhất

        # Cập nhật combobox
        self.prefix_combobox['values'] = self.recent_prefixes

        # Lưu vào file
        try:
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prefix_history.json")
            with open(config_path, "w") as f:
                json.dump({"prefixes": self.recent_prefixes}, f)

            self.status.set(f"Đã lưu prefix '{prefix}' vào danh sách")
        except Exception as e:
            self.status.set(f"Lỗi khi lưu prefix: {str(e)}")

    def clear_results(self):
        # Xóa tất cả các mục trong bảng kết quả
        for item in self.result_table.get_children():
            self.result_table.delete(item)

    def add_result_row(self, status_icon, status_tag, original_name, new_name):
        # Thêm một dòng vào bảng kết quả
        self.result_table.insert('', 'end', values=(status_icon, original_name, new_name), tags=(status_tag,))

    def open_github(self):
        webbrowser.open("https://github.com/vulct174/python-prefix-file-renamer")

    def show_help(self):
        help_text = """
        Hướng dẫn sử dụng Prefix File Renamer:

        1. Chọn thư mục chứa các file cần đổi tên bằng cách nhấn nút "Duyệt..."
        2. Nhập prefix (tiền tố) mà bạn muốn thêm vào đầu tên file
        3. Bạn có thể chọn một prefix đã sử dụng trước đó từ dropdown
        4. Để lưu prefix mới vào danh sách, nhấn nút "Lưu prefix"
        5. Tích vào "Xem trước" để xem kết quả trước khi thực hiện
        6. Nhấn "Bắt đầu đổi tên" để thực hiện việc đổi tên file

        Các tính năng:
        - Các file đã có prefix sẽ tự động được bỏ qua
        - Bảng kết quả hiển thị tên file trước và sau khi đổi
        - Màu xanh: File đã được đổi tên thành công
        - Màu vàng: File được bỏ qua (đã có prefix)
        - Màu đỏ: Lỗi khi đổi tên file

        © 2025 vulct174 | Prefix File Renamer
        """
        messagebox.showinfo("Trợ giúp", help_text)

    def preview_renaming(self):
        """Xem trước kết quả đổi tên mà không thực sự đổi tên file"""
        folder_path = self.folder_path.get().strip()
        prefix = self.prefix.get().strip()

        if not folder_path or not os.path.isdir(folder_path):
            self.status.set("Lỗi: Đường dẫn thư mục không hợp lệ!")
            return

        if not prefix:
            self.status.set("Lỗi: Prefix không được để trống!")
            return

        # Xóa kết quả cũ
        self.clear_results()

        # Đặt tiêu đề cho chế độ xem trước
        self.status.set("Đang xem trước kết quả...")

        try:
            # Lấy danh sách tất cả các file trong thư mục
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]

            if len(files) == 0:
                self.status.set("Không tìm thấy file nào trong thư mục này.")
                return

            # Xử lý từng file trong chế độ xem trước
            for filename in files:
                if not filename.startswith(prefix):
                    new_filename = prefix + filename
                    self.add_result_row(f"{self.icons['success']}", 'success', filename, new_filename)
                else:
                    self.add_result_row(f"{self.icons['warning']}", 'warning', filename, "(không thay đổi)")

            self.status.set(f"Xem trước hoàn tất. Tìm thấy {len(files)} file.")

        except Exception as e:
            self.status.set(f"Lỗi khi xem trước: {str(e)}")

    def start_process(self):
        """Bắt đầu quá trình đổi tên hoặc xem trước"""
        if self.preview_mode.get():
            self.preview_renaming()
            # Hỏi người dùng có muốn tiếp tục không
            if messagebox.askyesno("Xác nhận", "Bạn có muốn tiếp tục đổi tên các file không?"):
                self.preview_mode.set(False)  # Tắt chế độ xem trước
                self.start_renaming()  # Thực hiện đổi tên
        else:
            self.start_renaming()

    def start_renaming(self):
        """Bắt đầu quá trình đổi tên thật sự"""
        # Kiểm tra dữ liệu nhập vào
        folder_path = self.folder_path.get().strip()
        prefix = self.prefix.get().strip()

        if not folder_path or not os.path.isdir(folder_path):
            self.status.set("Lỗi: Đường dẫn thư mục không hợp lệ!")
            return

        if not prefix:
            self.status.set("Lỗi: Prefix không được để trống!")
            return

        # Vô hiệu hóa nút để tránh nhấn nhiều lần
        self.rename_button["state"] = "disabled"

        # Xóa kết quả cũ
        self.clear_results()

        # Bắt đầu tiến trình đổi tên trong một thread riêng
        threading.Thread(target=self.rename_files_with_prefix, args=(folder_path, prefix)).start()

    def rename_files_with_prefix(self, folder_path, prefix):
        try:
            # Lưu prefix vào danh sách gần đây
            if prefix not in self.recent_prefixes:
                self.recent_prefixes.insert(0, prefix)
                self.recent_prefixes = self.recent_prefixes[:10]
                self.prefix_combobox['values'] = self.recent_prefixes
                self.save_prefix()

            # Lấy danh sách tất cả các file trong thư mục
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            self.total_files = len(files)
            self.processed_files = 0

            if self.total_files == 0:
                self.status.set("Không tìm thấy file nào trong thư mục này.")
                self.rename_button["state"] = "normal"
                return

            self.progress_bar["maximum"] = self.total_files
            self.progress_bar["value"] = 0

            self.status.set(f"Đang xử lý {self.total_files} file...")

            renamed_count = 0
            skipped_count = 0
            error_count = 0

            # Tạo file log
            log_folder = os.path.join(folder_path, "prefix_renamer_logs")
            os.makedirs(log_folder, exist_ok=True)
            log_file = os.path.join(log_folder, f"rename_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

            with open(log_file, "w", encoding="utf-8") as log:
                log.write(f"Prefix File Renamer - Log {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                log.write(f"Thư mục: {folder_path}\n")
                log.write(f"Prefix: {prefix}\n")
                log.write("-" * 50 + "\n\n")

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
                            self.add_result_row(f"{self.icons['success']}", 'success', filename, new_filename)
                            log.write(f"Đổi tên: {filename} -> {new_filename}\n")
                            renamed_count += 1
                        except Exception as e:
                            self.add_result_row(f"{self.icons['error']}", 'error', filename, f"Lỗi: {str(e)}")
                            log.write(f"Lỗi khi đổi tên '{filename}': {str(e)}\n")
                            error_count += 1
                    else:
                        self.add_result_row(f"{self.icons['warning']}", 'warning', filename,
                                            "(không thay đổi - đã có prefix)")
                        log.write(f"Bỏ qua: '{filename}' (đã có prefix '{prefix}')\n")
                        skipped_count += 1

                    # Cập nhật tiến trình
                    self.processed_files += 1
                    self.progress_bar["value"] = self.processed_files
                    self.status.set(f"Đã xử lý: {self.processed_files}/{self.total_files}")
                    self.root.update_idletasks()

                # Tổng kết kết quả
                log.write("\n" + "-" * 50 + "\n")
                log.write(f"Tổng số file: {self.total_files}\n")
                log.write(f"Đã đổi tên: {renamed_count}\n")
                log.write(f"Đã bỏ qua: {skipped_count}\n")
                log.write(f"Lỗi: {error_count}\n")

            # Hoàn thành
            self.status.set(
                f"Hoàn thành! Đã đổi tên {renamed_count} file, bỏ qua {skipped_count} file, lỗi {error_count} file.")

            # Hiển thị thông báo hoàn thành
            if renamed_count > 0:
                messagebox.showinfo("Hoàn thành",
                                    f"Đã đổi tên {renamed_count} file thành công!\nFile log được lưu tại:\n{log_file}")
            else:
                messagebox.showinfo("Thông báo",
                                    f"Không có file nào được đổi tên.\nFile log được lưu tại:\n{log_file}")

        except Exception as e:
            self.status.set(f"Đã xảy ra lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Đã xảy ra lỗi trong khi xử lý:\n{str(e)}")
        finally:
            # Kích hoạt lại nút
            self.rename_button["state"] = "normal"


def main():
    root = tk.Tk()
    PrefixRenamerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
