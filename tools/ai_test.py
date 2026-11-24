import io
import os
import re
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")

ROOT = r"D:\游戏\Insecters War"
TK = os.path.join(ROOT, "服务器", "tools")
GAME = os.path.join(ROOT, "InsectersWar.exe")
DLL_SRC = os.path.join(ROOT, "iw-opensource", "build", "Assembly-CSharp.dll")
DLL_DST = os.path.join(ROOT, "InsectersWar_Data", "Managed", "Assembly-CSharp.dll")
LOG = os.path.join(ROOT, "InsectersWar_Data", "output_log.txt")

WAIT = int(sys.argv[1]) if len(sys.argv) > 1 else 95
TAG = sys.argv[2] if len(sys.argv) > 2 else "it"


def ps(script, *args):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", os.path.join(TK, script)] + [str(a) for a in args]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return (out.stdout or "") + (out.stderr or "")
    except Exception as e:
        return "ERR " + str(e)


def kill_game():
    subprocess.run(["taskkill", "/F", "/IM", "InsectersWar.exe"],
                   capture_output=True)


def get_pid():
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "(Get-Process InsectersWar -EA SilentlyContinue | Sort-Object StartTime -Descending | Select-Object -First 1).Id"],
        capture_output=True, text=True)
    try:
        return int((out.stdout or "").strip())
    except Exception:
        return 0


def rect(pid):
    out = ps("win_rect.ps1", pid)
    m = re.search(r"RECT (\d+) (\d+) (\d+) (\d+)", out)
    if not m:
        return None
    return tuple(int(x) for x in m.groups())


def click_rel(pid, rx, ry):
    r = rect(pid)
    if r is None:
        return
    x = r[0] + int(r[2] * rx)
    y = r[1] + int(r[3] * ry)
    ps("click_at.ps1", "-ProcessId", pid, "-X", x, "-Y", y)
    time.sleep(0.8)


def key(pid, k, ms=130):
    ps("hold_key.ps1", "-ProcessId", pid, "-Key", k, "-HoldMs", ms)
    time.sleep(0.3)


print("== kill old ==")
kill_game()
time.sleep(2)

print("== deploy ==")
os.makedirs(os.path.dirname(DLL_DST), exist_ok=True)
with open(DLL_SRC, "rb") as f:
    data = f.read()
with open(DLL_DST, "wb") as f:
    f.write(data)
try:
    os.remove(LOG)
except Exception:
    pass

print("== start ==")
subprocess.Popen([GAME], cwd=ROOT, close_fds=True)
time.sleep(16)
pid = get_pid()
print("pid =", pid)
if pid == 0:
    print("START_FAILED")
    raise SystemExit(1)
print(rect(pid))

print("== Play ==")
ps("click_button.ps1", pid, "Play!")
time.sleep(25)

print("== lobby -> create room ==")
key(pid, "J")
time.sleep(6)
for _ in range(8):
    click_rel(pid, 0.1424, 0.3642)
time.sleep(3)

key(pid, "J", 160)
time.sleep(8)

print("== ready ==")
for _ in range(10):
    click_rel(pid, 0.8654, 0.8684)

print("== wait", WAIT, "s ==")
time.sleep(WAIT)
print("DONE_TAG", TAG)
