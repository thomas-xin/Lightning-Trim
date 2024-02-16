import subprocess, os, sys

def round_min(x):
	y = int(x)
	if x == y:
		return y
	return x

strnum = lambda num: str(round_min(round(num, 6)))

def time_disp(s):
	s = float(s)
	output = strnum(s % 60)
	if len(output) < 2:
		output = "0" + output
	if s >= 60:
		temp = strnum((s // 60) % 60)
		if len(temp) < 2 and s >= 3600:
			temp = "0" + temp
		output = temp + ":" + output
		if s >= 3600:
			temp = strnum((s // 3600) % 24)
			if len(temp) < 2 and s >= 86400:
				temp = "0" + temp
			output = temp + ":" + output
			if s >= 86400:
				output = strnum(s // 86400) + ":" + output
	else:
		output = "0:" + output
	return output

def time_parse(ts):
	if ts == "N/A":
		return inf
	data = ts.split(":")
	if len(data) >= 5: 
		raise TypeError("Too many time arguments.")
	mults = (1, 60, 3600, 86400)
	return round_min(sum(float(count) * mult for count, mult in zip(data, reversed(mults[:len(data)]))))

if len(sys.argv) >= 4:
	fi, start, end = sys.argv[1:4]
	name, fmt = fi.rsplit(".", 1) if "." in fi else (fi, "mp4")
	if len(sys.argv) >= 5:
		fn = sys.argv[4]
	else:
		fn = name + "~t" + "." + fmt
	start, end = time_parse(start), time_parse(end)
	easygui = None
else:
	import easygui
	fi = easygui.fileopenbox("Please select file to trim:")
	if not fi:
		raise SystemExit
	dur = subprocess.check_output(["ffprobe", "-skip_frame", "nokey", "-select_streams", "v:0", "-show_entries", "format=duration", "-of", "default=nokey=1:noprint_wrappers=1", "-i", fi]).strip().decode("ascii")
	if not dur or dur == "N/A":
		dur = subprocess.check_output(["ffprobe", "-skip_frame", "nokey", "-select_streams", "v:0", "-show_entries", "stream=duration", "-of", "default=nokey=1:noprint_wrappers=1", "-i", fi]).strip().decode("ascii")
		if not dur or dur == "N/A":
			dur = 0
	fmts = subprocess.check_output(["ffprobe", "-skip_frame", "nokey", "-select_streams", "v:0", "-show_entries", "format=format_name", "-of", "default=nokey=1:noprint_wrappers=1", "-i", fi]).strip().decode("ascii").replace("matroska", "mkv").split(",")
	name, ext = fi.rsplit(".", 1) if "." in fi else (fi, "mp4")
	if ext in fmts:
		fmt = ext
	else:
		fmt = fmts[0]
	fn = name + "~t" + "." + fmt
	text = easygui.textbox("Please enter start/end, and optionally name:", text=f"START: 0:00\nEND: {time_disp(dur)}\nNAME: {fn}")
	if not text:
		raise SystemExit
	try:
		lines = text.splitlines()
		start = time_parse(lines[0].split(":", 1)[-1])
		end = time_parse(lines[1].split(":", 1)[-1])
		fn = lines[2].split(":", 1)[-1].strip()
		if '"' in fn or "'" in fn:
			import ast
			fn = ast.literal_eval(fn)
	except:
		easygui.exceptionbox()

try:
	proc = subprocess.Popen(["ffprobe", "-skip_frame", "nokey", "-select_streams", "v:0", "-show_entries", "frame=pts_time", "-of", "default=nokey=1:noprint_wrappers=1", "-i", fi], stdout=subprocess.PIPE)

	key = 0
	while key < start:
		key = float(proc.stdout.readline())

	proc.terminate()
	if os.path.exists(fn):
		os.remove(fn)

	if not start:
		subprocess.run(["ffmpeg", "-y", "-hwaccel", "auto", "-ss", str(start), "-to", str(end), "-i", fi, "-c", "copy", fn])
	elif abs(start - key) < 1 / 30:
		subprocess.run(["ffmpeg", "-y", "-hwaccel", "auto", "-i", fi, "-ss", str(start), "-to", str(end), "-c", "copy", fn])
	else:
		fa = name + "~0" + "." + "ts"
		aproc = subprocess.Popen(["ffmpeg", "-y", "-hwaccel", "auto", "-i", fi, "-ss", str(start), "-to", str(end), "-vn", "-c:a", "copy", fa])

		f1 = name + "~1" + "." + "ts"
		f2 = name + "~2" + "." + "ts"
		cdc = subprocess.check_output(["ffprobe", "-skip_frame", "nokey", "-select_streams", "v:0", "-show_entries", "stream=codec_name", "-of", "default=nokey=1:noprint_wrappers=1", "-i", fi]).strip()

		vproc = subprocess.Popen(["ffmpeg", "-y", "-hwaccel", "auto", "-i", fi, "-ss", str(start), "-to", str(key), "-crf", "20", "-c:v", cdc, "-an", f1])
		subprocess.run(["ffmpeg", "-y", "-hwaccel", "auto", "-ss", str(key + 0.001), "-to", str(end), "-i", fi, "-c:v", "copy", "-an", "-avoid_negative_ts", "1", f2])
		aproc.wait()
		vproc.wait()

		fc = name + "~c" + "." + "txt"
		with open(fc, "w", encoding="utf-8") as f:
			f.write("file " + repr(f1) + "\n")
			f.write("file " + repr(f2) + "\n")
		subprocess.run(["ffmpeg", "-y", "-hwaccel", "auto", "-safe", "0", "-f", "concat", "-i", fc, "-i", fa, "-c:v", "copy", "-c:a", "copy", fn])
		if not os.path.exists(fn):
			raise RuntimeError("Unable to save file. Please check log for info.")
		for fd in (fa, f1, f2, fc):
			try:
				os.remove(fd)
			except:
				pass
	if not os.path.exists(fn):
		raise RuntimeError("Unable to save file. Please check log for info.")
except:
	if not easygui:
		raise
	easygui.exceptionbox()