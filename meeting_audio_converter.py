import os, sys, subprocess, shutil
import tkinter as tk
from tkinter import filedialog, messagebox

def app_dir():
    return os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))

def get_ffmpeg():
    p = os.path.join(app_dir(), "ffmpeg.exe")
    return p if os.path.exists(p) else shutil.which("ffmpeg")

def convert(src):
    if not src.lower().endswith(".webm"):
        raise ValueError("WebM 파일만 선택할 수 있습니다.")
    ff = get_ffmpeg()
    if not ff:
        raise FileNotFoundError("ffmpeg.exe를 프로그램과 같은 폴더에 넣어주세요.")
    dst = os.path.splitext(src)[0] + ".m4a"
    r = subprocess.run([ff, "-y", "-i", src, "-vn", "-c:a", "aac", "-b:a", "128k", dst],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-2000:])
    return dst

def choose():
    files = filedialog.askopenfilenames(title="변환할 WebM 파일 선택",
        filetypes=[("WebM 파일", "*.webm")])
    if files: process(files)

def process(files):
    ok, fail = [], []
    status.set("변환 중...")
    root.update_idletasks()
    for f in files:
        try: ok.append(convert(f))
        except Exception as e: fail.append(f"{os.path.basename(f)}: {e}")
    if fail:
        status.set("일부 파일 변환 실패")
        messagebox.showerror("변환 결과", f"완료: {len(ok)}개\n실패: {len(fail)}개\n\n" + "\n".join(fail))
    else:
        status.set(f"변환 완료: {len(ok)}개")
        messagebox.showinfo("변환 완료",
            f"{len(ok)}개 파일 변환이 완료되었습니다.\n\nM4A 파일은 원본 WebM과 같은 폴더에 생성되었습니다.")

root = tk.Tk()
root.title("회의 음성 파일 변환")
root.geometry("520x300")
root.resizable(False, False)
frame = tk.Frame(root, padx=30, pady=25); frame.pack(fill="both", expand=True)

tk.Label(frame, text="회의 음성 파일 변환", font=("맑은 고딕",18,"bold")).pack(pady=(0,10))
tk.Label(frame, text="tl;dv WebM 파일을 클로바노트용 M4A 파일로 변환합니다.",
         font=("맑은 고딕",10)).pack(pady=(0,20))
tk.Button(frame, text="WebM 파일 선택", command=choose, font=("맑은 고딕",11), width=20, height=2).pack(pady=15)
tk.Label(frame, text="변환 형식: M4A / AAC 128kbps", font=("맑은 고딕",9)).pack()
status = tk.StringVar(value="준비 완료")
tk.Label(frame, textvariable=status, font=("맑은 고딕",9)).pack(pady=12)

if len(sys.argv) > 1:
    root.after(300, lambda: process(sys.argv[1:]))

root.mainloop()
