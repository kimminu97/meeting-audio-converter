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
OUTPUT_BITRATE = "128k"


def app_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def find_ffmpeg():
    # 배포 시 meeting_audio_converter.exe 옆에 ffmpeg.exe를 둡니다.
    local = os.path.join(app_dir(), "ffmpeg.exe")
    if os.path.isfile(local):
        return local

    # 개발 PC에서 PATH에 등록되어 있는 경우도 허용합니다.
    return shutil.which("ffmpeg")


def convert_webm(src):
    if not src.lower().endswith(".webm"):
        raise ValueError("WebM 파일만 변환할 수 있습니다.")

    ffmpeg = find_ffmpeg()
    if not ffmpeg:
        raise FileNotFoundError(
            "ffmpeg.exe를 찾을 수 없습니다.\n\n"
            "개발/테스트 시에는 FFmpeg를 설치하거나 PATH에 등록하고,\n"
            "배포 시에는 프로그램과 같은 폴더에 ffmpeg.exe를 넣어주세요."
        )

    dst = os.path.splitext(src)[0] + ".m4a"

    # 같은 이름의 M4A가 있으면 덮어쓰지 않고 사용자에게 확인합니다.
    if os.path.exists(dst):
        raise FileExistsError(
            f"이미 변환된 파일이 있습니다.\n\n{os.path.basename(dst)}"
        )

    cmd = [
        ffmpeg,
        "-hide_banner",
        "-loglevel", "error",
        "-y",
        "-i", src,
        "-vn",
        "-c:a", "aac",
        "-b:a", OUTPUT_BITRATE,
        dst,
    ]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )

    if result.returncode != 0:
        # 실패 시 불완전한 출력 파일 제거
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
        self.root.title(APP_TITLE)
        self.root.geometry("620x470")
        self.root.resizable(False, False)

        self.files = []
        self.running = False

        self.status_var = tk.StringVar(value="WebM 파일을 끌어다 놓으세요.")
        self.result_var = tk.StringVar(value="")

        self.build_ui()

    def build_ui(self):
        main = tk.Frame(self.root, padx=35, pady=28)
        main.pack(fill="both", expand=True)

        tk.Label(
            main,
            text=APP_TITLE,
            font=("맑은 고딕", 20, "bold"),
        ).pack(pady=(0, 8))

        tk.Label(
            main,
            text="tl;dv의 WebM 녹음 파일을\n클로바노트에서 사용할 수 있는 M4A로 변환합니다.",
            font=("맑은 고딕", 10),
            justify="center",
        ).pack(pady=(0, 20))

        self.drop_area = tk.Frame(
            main,
            width=520,
            height=125,
            relief="groove",
            borderwidth=2,
        )
        self.drop_area.pack_propagate(False)
        self.drop_area.pack(pady=5)

        self.drop_label = tk.Label(
            self.drop_area,
            text="WebM 파일을\n여기로 끌어다 놓으세요",
            font=("맑은 고딕", 13),
            justify="center",
        )
        self.drop_label.pack(expand=True)

        if DND_FILES is not None:
            self.drop_area.drop_target_register(DND_FILES)
            self.drop_area.dnd_bind("<<Drop>>", self.on_drop)
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self.on_drop)

        tk.Button(
            main,
            text="WebM 파일 선택",
            command=self.select_files,
            font=("맑은 고딕", 11),
            width=20,
            height=2,
        ).pack(pady=15)

        tk.Label(
            main,
            text="변환 형식: M4A (AAC 128kbps)",
            font=("맑은 고딕", 9),
        ).pack()

        tk.Label(
            main,
            textvariable=self.status_var,
            font=("맑은 고딕", 10),
        ).pack(pady=(18, 4))

        tk.Label(
            main,
            textvariable=self.result_var,
            font=("맑은 고딕", 9),
            justify="center",
        ).pack()

        self.open_button = tk.Button(
            main,
            text="변환 폴더 열기",
            command=self.open_result_folder,
            state="disabled",
            font=("맑은 고딕", 10),
            width=18,
        )
        self.open_button.pack(pady=14)

    def select_files(self):
        paths = filedialog.askopenfilenames(
            title="변환할 WebM 파일 선택",
            filetypes=[("WebM 파일", "*.webm"), ("모든 파일", "*.*")],
        )
        if paths:
            self.start_conversion(list(paths))

    def on_drop(self, event):
        paths = self.root.tk.splitlist(event.data)
        self.start_conversion(list(paths))

    def start_conversion(self, paths):
        if self.running:
            messagebox.showwarning("변환 중", "현재 변환 작업이 진행 중입니다.")
            return

        webm_files = []
        for path in paths:
            path = os.path.abspath(path)
            if os.path.isfile(path) and path.lower().endswith(".webm"):
                if path not in webm_files:
                    webm_files.append(path)

        if not webm_files:
            messagebox.showwarning("파일 확인", "WebM 파일을 선택하거나 끌어다 놓아주세요.")
            return

        self.running = True
        self.open_button.config(state="disabled")
        self.status_var.set(f"변환 준비 중... ({len(webm_files)}개)")
        self.result_var.set("")

        threading.Thread(
            target=self.convert_files,
            args=(webm_files,),
            daemon=True,
        ).start()

    def convert_files(self, files):
        success = []
        failed = []

        for index, src in enumerate(files, start=1):
            self.root.after(
                0,
                lambda i=index, total=len(files), name=os.path.basename(src):
                self.status_var.set(f"변환 중... {i}/{total}\n{name}")
            )

            try:
                dst = convert_webm(src)
                success.append(dst)
            except Exception as exc:
                failed.append(f"{os.path.basename(src)}\n{exc}")

        self.root.after(0, lambda: self.finish(success, failed))

    def finish(self, success, failed):
        self.running = False

        if success:
            self.open_button.config(state="normal")
            self.result_var.set(
                f"변환 완료: {len(success)}개\n"
                f"M4A 파일은 원본 WebM과 같은 폴더에 생성되었습니다."
            )

        if failed:
            self.status_var.set(f"완료: {len(success)}개 / 실패: {len(failed)}개")
            messagebox.showerror(
                "변환 결과",
                f"성공: {len(success)}개\n실패: {len(failed)}개\n\n"
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
        # 가장 최근 성공 파일의 폴더를 엽니다.
        if not hasattr(self, "_last_folder"):
            # 성공 결과가 여러 폴더일 수 있으므로 첫 성공 폴더를 찾습니다.
            messagebox.showinfo("안내", "변환된 파일은 원본 WebM과 같은 폴더에 있습니다.")
            return

        os.startfile(self._last_folder)

    def set_last_folder(self, folder):
        self._last_folder = folder


def main():
    if TkinterDnD is None:
        # 드래그앤드롭 라이브러리가 없는 개발 환경에서도 파일 선택 기능은 사용할 수 있도록 함.
        root = tk.Tk()
        root.title(APP_TITLE)
        root.geometry("520x280")
        root.resizable(False, False)

        tk.Label(root, text=APP_TITLE, font=("맑은 고딕", 18, "bold")).pack(pady=25)
        tk.Label(
            root,
            text="드래그앤드롭 기능을 사용하려면 tkinterdnd2가 필요합니다.\n"
                 "파일 선택 기능은 아래 버튼으로 사용할 수 있습니다.",
            font=("맑은 고딕", 10),
            justify="center",
        ).pack(pady=10)

        def select():
            paths = filedialog.askopenfilenames(
                title="WebM 파일 선택",
                filetypes=[("WebM 파일", "*.webm")]
            )
            if not paths:
                return
            for p in paths:
                try:
                    convert_webm(p)
                except Exception as e:
                    messagebox.showerror("변환 실패", str(e))
                    return
            messagebox.showinfo("완료", "변환이 완료되었습니다.")

        tk.Button(root, text="WebM 파일 선택", command=select, width=20, height=2).pack(pady=20)
        root.mainloop()
        return

    root = TkinterDnD.Tk()
    app = ConverterApp(root)

    # EXE/스크립트에 파일을 직접 드래그했을 때의 인자도 지원
    if len(sys.argv) > 1:
        root.after(300, lambda: app.start_conversion(sys.argv[1:]))

    root.mainloop()


if __name__ == "__main__":
    main()
