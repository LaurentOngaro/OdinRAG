// Source: https://gist.github.com/laytan/e411288bc622eaf09832e752b31c9bc8
// Raylib logging callback to Odin logger | By laytan
logger: log.Logger
rl_log_buf: []byte
rl_log :: proc "c" (logLevel: rl.TraceLogLevel, text: cstring, args: libc.va_list) {
	context = runtime.default_context()
	context.logger = logger

	level: log.Level
	switch logLevel {
	case .TRACE, .DEBUG:     level = .Debug
	case .ALL, .NONE, .INFO: level = .Info
	case .WARNING:           level = .Warning
	case .ERROR:             level = .Error
	case .FATAL:             level = .Fatal
	}

	if level < logger.lowest_level {
		return
	}

	if rl_log_buf == nil {
		rl_log_buf = make([]byte, 1024)
	}

	defer mem.zero_slice(rl_log_buf)

	n: int
	for {
		va := args
		n = int(libc.vsnprintf(raw_data(rl_log_buf), len(rl_log_buf), text, &va))
		if n < len(rl_log_buf) do break
		log.infof("Resizing raylib log buffer from %m to %m", len(rl_log_buf), len(rl_log_buf)*2)
		rl_log_buf, _ = mem.resize_bytes(rl_log_buf, len(rl_log_buf)*2)
	}

	formatted := string(rl_log_buf[:n])
	log.log(level, formatted)
}
