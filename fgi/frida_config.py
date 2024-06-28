_LISTEN = """
{
    "interaction": {
        "type": "listen",
        "address": "0.0.0.0",
        "port": 27042,
        "on_port_conflict": "fail",
        "on_load": "wait"
      }
}
"""

_CONNECT = """
{
    "interaction": {
        "type": "connect",
        "address": "0.0.0.0",
        "port": 27052
    }
}
"""

_SCRIPT = """
{
    "interaction": {
        "type": "script",
        "path": "%s"
    }
}
"""

CONFIG_TYPES = {"listen": _LISTEN, "connect": _CONNECT, "script": _SCRIPT}
