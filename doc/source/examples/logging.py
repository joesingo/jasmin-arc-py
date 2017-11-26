# Log to a file
with open("/tmp/jasmin_arc.log", "w") as logfile:
    arc_iface = ArcInterface("/path/to/config", log=logfile)

# Change log level to DEBUG (shows a lot of output!)
arc_iface = ArcInterface("/path/to/config", log_level=LogLevels.DEBUG)

# Disable logging
arc_iface = ArcInterface("/path/to/config", log=None)
