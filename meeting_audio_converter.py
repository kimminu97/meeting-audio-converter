import os
import sys
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None

APP_TITLE = "회의 음성 파일 변환기"
APP_VERSION = "0.1.2"
APP_TEAM = "GALA IT팀"
OUTPUT_BITRATE = "128k"


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def find_ffmpeg():
    local = os.path.join(app_dir(), "ffmpeg.exe")
    if os.path.isfile(local):
        return local
    return shutil.which("ffmpeg")


def convert_webm(src):
    if not src.lower().endswith(".webm"):
        raise ValueError("WebM 파일만 변환할 수 있습니다.")

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        raise FileNotFoundError(
            "ffmpeg.exe를 찾을 수 없습니다.\n\n"
            "프로그램과 같은 폴더에 ffmpeg.exe를 넣어주세요."
        )

    dst = os.path.splitext(src)[0] + ".m4a"

    if os.path.exists(dst):
        raise FileExistsError(
            f"같은 이름의 M4A 파일이 이미 있습니다.\n\n"
            f"{os.path.basename(dst)}"
        )

    result = subprocess.run(
        [
            ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
            "-i", src, "-vn", "-c:a", "aac", "-b:a", OUTPUT_BITRATE, dst
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

    if result.returncode != 0:
        if os.path.exists(dst):
            try:
                os.remove(dst)
            except OSError:
                pass
        raise RuntimeError(result.stderr.strip() or "FFmpeg 변환에 실패했습니다.")

    return dst


class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"{APP_TITLE} v{APP_VERSION}")
        self.root.geometry("620x470")
        self.root.resizable(False, False)

        self.running = False
        self.last_folder = None

        self.status_var = tk.StringVar(value="준비 완료")
        self.result_var = tk.StringVar(value="")

        self.build_ui()

    def build_ui(self):
        # 창을 본문과 footer로 명확하게 분리합니다.
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        content = tk.Frame(self.root, padx=35, pady=22)
        content.grid(row=0, column=0, sticky="nsew")

        tk.Label(
            content,
            text=APP_TITLE,
            font=("맑은 고딕", 20, "bold")
        ).pack(pady=(0, 16))

        tk.Label(
            content,
            text="tl;dv의 WebM 녹음 파일을\n클로바노트에서 사용할 수 있는 M4A로 변환합니다.",
            font=("맑은 고딕", 10),
            justify="center"
        ).pack(pady=(0, 14))

        self.drop_area = tk.Frame(
            content,
            width=520,
            height=120,
            relief="groove",
            borderwidth=2
        )
        self.drop_area.pack_propagate(False)
        self.drop_area.pack(pady=4)

        self.drop_label = tk.Label(
            self.drop_area,
            text="WebM 파일을\n여기로 끌어다 놓으세요",
            font=("맑은 고딕", 13),
            justify="center"
        )
        self.drop_label.pack(expand=True)

        if DND_FILES is not None:
            for widget in (self.drop_area, self.drop_label):
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<Drop>>", self.on_drop)

        tk.Button(
            content,
            text="WebM 파일 선택",
            command=self.select_files,
            font=("맑은 고딕", 11),
            width=20,
            height=2
        ).pack(pady=10)

        tk.Label(
            content,
            text="변환 형식: M4A (AAC 128kbps)",
            font=("맑은 고딕", 9)
        ).pack()

        tk.Label(
            content,
            textvariable=self.status_var,
            font=("맑은 고딕", 10)
        ).pack(pady=(10, 2))

        tk.Label(
            content,
            textvariable=self.result_var,
            font=("맑은 고딕", 9),
            justify="center"
        ).pack()

        self.open_button = tk.Button(
            content,
            text="변환 폴더 열기",
            command=self.open_result_folder,
            state="disabled",
            font=("맑은 고딕", 10),
            width=18
        )
        self.open_button.pack(pady=6)

        # Footer는 본문과 별도의 grid row에 고정합니다.
        footer = tk.Frame(
            self.root,
            height=36,
            relief="sunken",
            borderwidth=1
        )
        footer.grid(row=1, column=0, sticky="ew")
        footer.grid_propagate(False)

        tk.Label(
            footer,
            text=f"{APP_TEAM}  |  Version {APP_VERSION}",
            font=("맑은 고딕", 9)
        ).pack(expand=True)

    def select_files(self):
        paths = filedialog.askopenfilenames(
            title="변환할 WebM 파일 선택",
            filetypes=[("WebM 파일", "*.webm")]
        )
        if paths:
            self.start_conversion(list(paths))

    def on_drop(self, event):
        self.start_conversion(list(self.root.tk.splitlist(event.data)))

    def start_conversion(self, paths):
        if self.running:
            messagebox.showwarning("변환 중", "현재 변환 작업이 진행 중입니다.")
            return

        files = []
        for path in paths:
            path = os.path.abspath(path)
            if os.path.isfile(path) and path.lower().endswith(".webm"):
                if path not in files:
                    files.append(path)

        if not files:
            messagebox.showwarning(
                "파일 확인",
                "WebM 파일을 선택하거나 끌어다 놓아주세요."
            )
            return

        self.running = True
        self.open_button.config(state="disabled")
        self.status_var.set(f"변환 준비 중... ({len(files)}개)")
        self.result_var.set("")

        threading.Thread(
            target=self.convert_files,
            args=(files,),
            daemon=True
        ).start()

    def convert_files(self, files):
        success = []
        failed = []

        for index, src in enumerate(files, 1):
            name = os.path.basename(src)

            self.root.after(
                0,
                lambda i=index, total=len(files), n=name:
                self.status_var.set(f"변환 중... {i}/{total}\n{n}")
            )

            try:
                success.append(convert_webm(src))
            except Exception as exc:
                failed.append(f"{name}\n{exc}")

        self.root.after(
            0,
            lambda: self.finish(success, failed)
        )

    def finish(self, success, failed):
        self.running = False

        if success:
            self.last_folder = os.path.dirname(success[-1])
            self.open_button.config(state="normal")
            self.result_var.set(
                f"변환 완료: {len(success)}개\n"
                "M4A 파일은 원본 WebM과 같은 폴더에 생성되었습니다."
            )

        if failed:
            self.status_var.set(
                f"완료: {len(success)}개 / 실패: {len(failed)}개"
            )
            messagebox.showerror(
                "변환 결과",
                f"성공: {len(success)}개\n"
                f"실패: {len(failed)}개\n\n"
                + "\n\n".join(failed)
            )
        else:
            self.status_var.set(f"변환 완료: {len(success)}개")
            messagebox.showinfo(
                "변환 완료",
                f"{len(success)}개 파일의 변환이 완료되었습니다.\n\n"
                "생성된 M4A 파일을 클로바노트에 업로드하면 됩니다."
            )

    def open_result_folder(self):
        if self.last_folder and os.path.isdir(self.last_folder):
            os.startfile(self.last_folder)
        else:
            messagebox.showinfo(
                "안내",
                "변환된 파일은 원본 WebM 파일과 같은 폴더에 있습니다."
            )


def main():
    if TkinterDnD is None:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "필수 라이브러리 없음",
            "드래그앤드롭 기능을 사용하려면 tkinterdnd2가 필요합니다.\n\n"
            "CMD에서 다음 명령을 실행하세요:\n"
            "python -m pip install tkinterdnd2"
        )
        root.destroy()
        return

    root = TkinterDnD.Tk()
    app = ConverterApp(root)

    if len(sys.argv) > 1:
        root.after(
            300,
            lambda: app.start_conversion(sys.argv[1:])
        )

    root.mainloop()


if __name__ == "__main__":
    main()
