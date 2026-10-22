"""Plays the protocols of Resource Transfer Fix: "Filling a tank" and "A tank of liquid fuel only".

It drives KSP through KSP-Util-MCPServer, a mod that answers HTTP requests on 127.0.0.1, and needs nothing but
Python 3: no AI, no package to install. Start KSP with KSP-Util-MCPServer installed, copy transfer-kerbin.sfs
into a sandbox game, wait for the main menu, open that game, then run:

    python run-transfers.py --folder <your sandbox game> --out out

The save holds one rocket on the launch pad: an FL-T400 tank, full, plays the tanker; an FL-T200 tank and a
Mk1 Liquid Fuel Fuselage, both empty, are the tanks to fill.

Filling a tank: the tanker's part action window is opened and pinned, then the FL-T200's; In is pressed for
the liquid fuel of the FL-T200, and the script waits until it is full, then ten seconds more.

A tank of liquid fuel only: the tanker's window is opened and pinned, then the fuselage's, then the
FL-T200's, which closes the fuselage's; In is pressed for the oxidizer of the FL-T200, and the script waits
five seconds.

Each protocol loads the save first. The windows are dragged apart, the tanker's to the left and the other one
to the right, and a screenshot is taken at every step. The script prints what the windows show and writes it to
runs.json. KSP is left running at the end.
"""
import argparse
import json
import os
import time
import urllib.request

URL = None

# Where the windows are dragged, in pixels from the top left corner of the game's window (1280 x 720).
LEFT = (40, 120)
RIGHT = (980, 120)


def call(tool, **args):
    """Calls one tool of KSP-Util-MCPServer and returns its answer, decoded from JSON when it is JSON."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                       "params": {"name": tool, "arguments": args}}).encode()
    request = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=900) as response:
        result = json.loads(response.read())["result"]
    text = result["content"][0].get("text", "") if result["content"] else ""
    if result.get("isError"):
        raise RuntimeError(tool + ": " + text)
    try:
        return json.loads(text)
    except ValueError:
        return text


def log(*parts):
    print(time.strftime("%H:%M:%S"), *parts, flush=True)


def parts_by_name():
    """The ids of the rocket's tanks, by part name."""
    return {p["name"]: p["id"] for p in call("list_parts")}


def summary(menus):
    """What the open windows show: for each, its resources with their amount and the transfer buttons shown."""
    shown = []
    for menu in menus:
        resources = {}
        for item in menu["items"]:
            if item["kind"] == "resource":
                resources.setdefault(item["resource"], {})["amount"] = round(item["amount"], 2)
                resources[item["resource"]]["max"] = item["max"]
            elif item["kind"] == "transfer":
                resources.setdefault(item["resource"], {})["buttons"] = item["buttons"]
        shown.append({"part": menu["part"], "pinned": menu["pinned"], "resources": resources})
    return shown


def step(record, out, name, menus=None):
    """Takes a screenshot named after the step, and records what the windows show."""
    if menus is None:
        menus = call("read_part_menus")
    path = os.path.abspath(os.path.join(out, name + ".png"))
    call("screenshot", path=path, return_image=False)
    record.append({"step": name, "windows": summary(menus)})
    log(name, json.dumps(summary(menus)))


def open_at(part, where, pin=False):
    """Opens a part's window as a right click does, pins it if asked, and drags it to where."""
    call("part_menu", action="open", part=part)
    if pin:
        call("part_menu", action="pin", part=part)
    return call("part_menu", action="move", part=part, x=where[0], y=where[1])


def amount(menus, part, resource):
    for menu in menus:
        if menu["part"] == part:
            for item in menu["items"]:
                if item["kind"] == "resource" and item["resource"] == resource:
                    return item["amount"], item["max"]
    return None, None


def start(options):
    """Loads the save and frames the rocket. Returns the ids of its tanks."""
    call("load_save", folder=options.folder, save=options.save)
    # Long enough for the crew portrait to show the kerbal rather than static.
    time.sleep(6)
    call("set_camera", distance=14, heading=20, pitch=5, fov=60)
    return parts_by_name()


def filling(options, out):
    record = []
    ids = start(options)
    tanker, tank = ids["fuelTank"], ids["fuelTankSmall"]
    open_at(tanker, LEFT, pin=True)
    open_at(tank, RIGHT)
    step(record, out, "1-before")
    call("press_part_button", part=tank, resource="LiquidFuel", transfer="in")
    time.sleep(1)
    step(record, out, "2-filling")
    deadline = time.time() + 60
    while time.time() < deadline:
        menus = call("read_part_menus")
        fuel, capacity = amount(menus, tank, "LiquidFuel")
        if fuel is not None and fuel >= capacity:
            break
        time.sleep(0.5)
    time.sleep(2)
    step(record, out, "3-tank-full")
    time.sleep(10)
    step(record, out, "4-ten-seconds-later")
    return record


def fuel_only(options, out):
    record = []
    ids = start(options)
    tanker, tank, fuselage = ids["fuelTank"], ids["fuelTankSmall"], ids["MK1Fuselage"]
    open_at(tanker, LEFT, pin=True)
    open_at(fuselage, RIGHT)
    step(record, out, "1-fuselage")
    # A right click on the FL-T200: the fuselage's window, not pinned, closes.
    open_at(tank, RIGHT)
    step(record, out, "2-tank")
    call("press_part_button", part=tank, resource="Oxidizer", transfer="in")
    time.sleep(5)
    step(record, out, "3-five-seconds-later")
    return record


PROTOCOLS = {"filling": filling, "fuel-only": fuel_only}


def main():
    global URL
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--folder", required=True, help="the sandbox game under saves/ the save was copied into")
    parser.add_argument("--save", default="transfer-kerbin", help="the save, without .sfs")
    parser.add_argument("--protocol", choices=["filling", "fuel-only", "both"], default="both")
    parser.add_argument("--out", required=True, help="the folder for runs.json and the screenshots")
    parser.add_argument("--port", type=int, default=8770, help="the port of KSP-Util-MCPServer")
    options = parser.parse_args()
    URL = "http://127.0.0.1:%d/mcp/" % options.port

    names = list(PROTOCOLS) if options.protocol == "both" else [options.protocol]
    runs = {}
    for name in names:
        out = os.path.join(options.out, name)
        os.makedirs(out, exist_ok=True)
        log("protocol", name)
        runs[name] = PROTOCOLS[name](options, out)
    with open(os.path.join(options.out, "runs.json"), "w", newline="\n") as f:
        json.dump(runs, f, indent=1)
    log("done")


if __name__ == "__main__":
    main()
