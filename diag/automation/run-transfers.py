"""Plays the protocols of Resource Transfer Fix: filling a tank, a tank of liquid fuel only, one tank to
several, several tanks to one, other resources, crossfeed, docking, a tank's contents switched in flight.

It drives KSP through KSP-Util-MCPServer, a mod that answers HTTP requests on 127.0.0.1, and needs nothing but
Python 3: no AI, no package to install. Start KSP with KSP-Util-MCPServer installed, copy transfer-kerbin.sfs and
transfer-kerbin-two-full.sfs into a sandbox game, wait for the main menu, open that game, then run:

    python run-transfers.py --folder <your sandbox game> --out out

transfer-kerbin.sfs holds one rocket on the launch pad: an FL-T400 tank, full, plays the tanker; an FL-T200
tank and a Mk1 Liquid Fuel Fuselage, both empty, are the tanks to fill. transfer-kerbin-two-full.sfs is the
same, with the fuselage full.

Filling a tank: the tanker's part action window is opened and pinned, then the FL-T200's; In is pressed for
the liquid fuel of the FL-T200, and the script waits until it is full, then ten seconds more.

A tank of liquid fuel only: the tanker's window is opened and pinned, then the fuselage's, then the
FL-T200's, which closes the fuselage's; In is pressed for the oxidizer of the FL-T200, and the script waits
five seconds.

One tank to several: the tanker's window and the FL-T200's are opened and pinned, then the fuselage's; Out
is pressed for the liquid fuel of the tanker, and the script waits until the tanker is empty, then ten
seconds more.

Several tanks to one (transfer-kerbin-two-full.sfs): the tanker's window and the fuselage's are opened and
pinned, then the FL-T200's; In is pressed for the liquid fuel of the FL-T200, and the script waits until it
is full, then ten seconds more.

Other resources (transfer-resources-kerbin.sfs, its own rocket): the "ship" above two docking ports holds
a Mk1 pod with no monopropellant, an empty FL-T200, a PB-X150 half full of xenon and a Small Holding Tank
half full of ore; the "tanker" below the ports, an FL-R120, a PB-X150, a Small Holding Tank and an FL-T400,
all full. For each resource in turn, liquid fuel, monopropellant, xenon and ore: the tanker's tank's window
is opened and pinned, then the ship's tank's; In is pressed for the resource in the ship's tank, the script
waits until it is full, then five seconds more, and the windows are closed.

Crossfeed (transfer-crossfeed-kerbin.sfs: the rocket of other resources, in a game whose transfers obey
crossfeed): the windows of the tanker's FL-T400 and of the ship's FL-T200 are opened and pinned; the window
of the tanker's docking port is opened, Disable Crossfeed pressed, and the window closed; then the same with
Enable Crossfeed; In is pressed for the liquid fuel of the FL-T200, and the script waits until it is full,
then five seconds more. The buttons are pressed by the names of their events, the same in every language
of the game.

Docking (transfer-docking-kerbin.sfs: two small rovers on the runway, joined nose to nose by their docking
ports; the first, the tanker, with its two FL-T200 full, the second, the ship, with its front FL-T200 half
full of liquid fuel and the rest empty): the ports
are undocked, the tanker backs away three metres, then drives back at 0.2 m/s until the ports dock. The
windows of the tanker's front FL-T200 and of the ship's front FL-T200 are then opened, In is pressed for the
liquid fuel of the ship's, and the script waits until it is full, then five seconds more. Here the windows
leave the middle of the screen to the rovers: the part action windows side by side at the top left, the one
of KSP Diag - Resource Transfer to the right.

A tank's contents switched in flight (transfer-kerbin.sfs, in a game with B9PartSwitch and the test patch
of in-flight-switch/ResourceTransferB9Test installed, which gives the FL-T200 a B9PartSwitch switch that
works in flight, between liquid fuel and oxidizer and liquid fuel only): the tanker's window is opened and
pinned, then the FL-T200's; the FL-T200 is switched to liquid fuel only, by calling what the button of
B9PartSwitch's in-flight dialog calls; In is pressed for its liquid fuel, the script waits five seconds,
then until the tanker runs dry, thirty seconds at most. "all" leaves this protocol out.

Each protocol loads its save first. The windows are dragged apart, the pinned ones to the left, one under the
other, and the last one to the right, and a screenshot is taken at every step. The script prints what the windows show and writes it to
runs.json. KSP is left running at the end.

With KSP Diag - Resource Transfer installed as well, its window is moved between the two part action windows,
its journal is cleared when the save is loaded, and its Log button is pressed at the end of each protocol:
its reading goes to KSP.log, and its badges show on the screenshots.
"""
import argparse
import json
import os
import time
import urllib.request

URL = None

# Where the windows are dragged, in pixels from the top left corner of the game's window (1280 x 720).
LEFT = (40, 120)
LEFT_BELOW = (40, 330)
RIGHT = (980, 120)
DIAG_WINDOW = (440, 100)
# Docking: the windows leave the middle of the screen to the rovers.
LEFT_BESIDE = (310, 120)
DOCKING_DIAG_WINDOW = (830, 100)

# Whether KSP Diag - Resource Transfer is installed: its tools are then offered by the server.
DIAG = False


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


def tool_names():
    """The names of the tools KSP-Util-MCPServer offers, those of other mods included."""
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}).encode()
    request = urllib.request.Request(URL, body, {"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return [tool["name"] for tool in json.loads(response.read())["result"]["tools"]]


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


def start(options, save=None):
    """Loads the save (the one of the options unless given) and frames the rocket. Returns the ids of its
    tanks."""
    # Right after the game opens, the server may not take the load yet: try again a few seconds later.
    for attempt in range(3):
        try:
            call("load_save", folder=options.folder, save=save or options.save)
            break
        except Exception as e:
            if attempt == 2:
                raise
            log("load_save failed, trying again:", e)
            time.sleep(5)
    # Long enough for the crew portrait to show the kerbal rather than static.
    time.sleep(6)
    call("set_camera", distance=14, heading=20, pitch=5, fov=60)
    if DIAG:
        call("resourcetransfer_move_window", x=DIAG_WINDOW[0], y=DIAG_WINDOW[1])
        call("resourcetransfer_clear_journal")
    return parts_by_name()


def finish(record):
    """With KSP Diag - Resource Transfer, presses its Log button: its reading goes to KSP.log."""
    if DIAG:
        call("resourcetransfer_log")
    return record


def wait_for(part, resource, done, seconds=60):
    """Waits until done(amount, capacity) holds for a resource of a part, as its window shows it, or for the
    given number of seconds at most."""
    deadline = time.time() + seconds
    while time.time() < deadline:
        value, capacity = amount(call("read_part_menus"), part, resource)
        if value is not None and done(value, capacity):
            return
        time.sleep(0.5)


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
    wait_for(tank, "LiquidFuel", lambda value, capacity: value >= capacity)
    time.sleep(2)
    step(record, out, "3-tank-full")
    time.sleep(10)
    step(record, out, "4-ten-seconds-later")
    return finish(record)


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
    return finish(record)


def one_to_several(options, out):
    record = []
    ids = start(options)
    tanker, tank, fuselage = ids["fuelTank"], ids["fuelTankSmall"], ids["MK1Fuselage"]
    open_at(tanker, LEFT, pin=True)
    open_at(tank, LEFT_BELOW, pin=True)
    open_at(fuselage, RIGHT)
    step(record, out, "1-before")
    call("press_part_button", part=tanker, resource="LiquidFuel", transfer="out")
    time.sleep(1)
    step(record, out, "2-sending")
    wait_for(tanker, "LiquidFuel", lambda value, capacity: value <= 0)
    time.sleep(2)
    step(record, out, "3-tanker-empty")
    time.sleep(10)
    step(record, out, "4-ten-seconds-later")
    return finish(record)


def several_to_one(options, out):
    record = []
    ids = start(options, options.save + "-two-full")
    tanker, tank, fuselage = ids["fuelTank"], ids["fuelTankSmall"], ids["MK1Fuselage"]
    open_at(tanker, LEFT, pin=True)
    open_at(fuselage, LEFT_BELOW, pin=True)
    open_at(tank, RIGHT)
    step(record, out, "1-before")
    call("press_part_button", part=tank, resource="LiquidFuel", transfer="in")
    time.sleep(1)
    step(record, out, "2-taking")
    wait_for(tank, "LiquidFuel", lambda value, capacity: value >= capacity)
    time.sleep(2)
    step(record, out, "3-tank-full")
    time.sleep(10)
    step(record, out, "4-ten-seconds-later")
    return finish(record)


# Other resources: (resource, the ship's tank, the tanker's tank), by part name.
RESOURCES = [
    ("LiquidFuel", "fuelTankSmall", "fuelTank"),
    ("MonoPropellant", "mk1pod.v2", "RCSFuelTank"),
    ("XenonGas", "xenonTank", "xenonTank"),
    ("Ore", "SmallTank", "SmallTank"),
]


def other_resources(options, out):
    record = []
    start(options, "transfer-resources-kerbin")
    # A taller rocket than the other protocols': the camera stands further back.
    call("set_camera", distance=22)
    parts = call("list_parts")
    for i, (resource, ship_name, tanker_name) in enumerate(RESOURCES):
        # The ship's tanks are above the docking ports, the tanker's below: the first and the last part of
        # that name in the vessel's list, which goes from the pod down.
        named = lambda name: [p for p in parts if p["name"] == name]
        ship, tanker = named(ship_name)[0]["id"], named(tanker_name)[-1]["id"]
        open_at(tanker, LEFT, pin=True)
        open_at(ship, RIGHT)
        call("press_part_button", part=ship, resource=resource, transfer="in")
        wait_for(ship, resource, lambda value, capacity: value >= capacity)
        time.sleep(5)
        step(record, out, "%d-%s" % (i + 1, resource))
        # Closes both windows: the tanker's is pinned, so it is unpinned first.
        call("part_menu", action="unpin", part=tanker)
        call("part_menu", action="close")
    return finish(record)


def crossfeed(options, out):
    record = []
    start(options, "transfer-crossfeed-kerbin")
    call("set_camera", distance=22)
    parts = call("list_parts")
    named = lambda name: [p for p in parts if p["name"] == name]
    tanker, ship = named("fuelTank")[-1]["id"], named("fuelTankSmall")[0]["id"]
    # The tanker's docking port: the lower of the two.
    port = named("dockingPort2")[-1]["id"]
    open_at(tanker, LEFT, pin=True)
    open_at(ship, RIGHT, pin=True)
    step(record, out, "1-crossfeed-on")
    for event, name in (("DisableXFeed", "2-crossfeed-off"), ("EnableXFeed", "3-crossfeed-on-again")):
        open_at(port, LEFT_BELOW)
        call("press_part_button", part=port, button=event)
        # A right click on empty space: the port's window, the only one not pinned, closes.
        call("part_menu", action="close")
        time.sleep(1)
        step(record, out, name)
    call("press_part_button", part=ship, resource="LiquidFuel", transfer="in")
    wait_for(ship, "LiquidFuel", lambda value, capacity: value >= capacity)
    time.sleep(5)
    step(record, out, "4-tank-full")
    return finish(record)


def loaded_vessels(prefix):
    """The loaded vessels whose name starts with prefix."""
    return [v for v in call("list_vessels") if v["loaded"] and v["name"].startswith(prefix)]


def docking(options, out):
    record = []
    start(options, "transfer-docking-kerbin")
    state = call("get_state")
    name, heading = state["vessel"]["name"], state["vessel"]["heading"]
    # The rovers show in the middle of the screen, seen from their left side: the windows go around them,
    # KSP Diag - Resource Transfer's to the right, the part action windows side by side at the top.
    frame = lambda: call("set_camera", distance=16, heading=(heading + 90) % 360, pitch=15, aim_heading=0,
                         aim_pitch=0)
    frame()
    if DIAG:
        call("resourcetransfer_move_window", x=DOCKING_DIAG_WINDOW[0], y=DOCKING_DIAG_WINDOW[1])
    parts = call("list_parts")
    named = lambda n: [p for p in parts if p["name"] == n]
    # The tanker is the first rover of the list (its port is the vessel's root), the ship the second.
    port = named("dockingPort2")[0]["id"]
    tanker, ship = named("fuelTankSmall")[0]["id"], named("fuelTankSmall")[2]["id"]
    open_at(port, LEFT)
    call("press_part_button", part=port, button="Undock")
    call("part_menu", action="close")
    time.sleep(2)
    if len(loaded_vessels(name)) != 2:
        raise RuntimeError("the ports did not undock")
    call("drive", heading=heading, reverse=True, speed=0.5, distance=3)
    step(record, out, "1-undocked")
    call("drive", heading=heading, speed=0.2, distance=3.6)
    time.sleep(2)
    if len(loaded_vessels(name)) != 1:
        raise RuntimeError("the ports did not dock again")
    # Docking makes a new vessel, and the camera goes back to its default framing.
    frame()
    open_at(tanker, LEFT, pin=True)
    open_at(ship, LEFT_BESIDE)
    step(record, out, "2-docked-again")
    call("press_part_button", part=ship, resource="LiquidFuel", transfer="in")
    wait_for(ship, "LiquidFuel", lambda value, capacity: value >= capacity)
    time.sleep(5)
    step(record, out, "3-tank-full")
    return finish(record)


def in_flight_switch(options, out):
    record = []
    ids = start(options)
    tanker, tank = ids["fuelTank"], ids["fuelTankSmall"]
    open_at(tanker, LEFT, pin=True)
    open_at(tank, RIGHT)
    step(record, out, "1-before")
    # As the player does: Select Tank in the tank's window (its event, the same in every language), then the
    # LiquidFuel button of the dialog B9PartSwitch opens.
    call("press_part_button", part=tank, button="ShowSubtypesWindow")
    call("press_dialog_button", dialog="B9PartSwitch_SwitchInFlight", button="LiquidFuel")
    time.sleep(1)
    step(record, out, "2-switched")
    call("press_part_button", part=tank, resource="LiquidFuel", transfer="in")
    time.sleep(5)
    step(record, out, "3-five-seconds-later")
    # The tanker holds less liquid fuel than the switched tank takes: it runs dry first, when anything flows.
    wait_for(tanker, "LiquidFuel", lambda value, capacity: value <= 0, seconds=30)
    time.sleep(2)
    step(record, out, "4-end")
    return finish(record)


PROTOCOLS = {"filling": filling, "fuel-only": fuel_only, "one-to-several": one_to_several,
             "several-to-one": several_to_one, "other-resources": other_resources, "crossfeed": crossfeed,
             "docking": docking, "in-flight-switch": in_flight_switch}
# The protocols "all" plays: those that need no other mod than KSP Diag - Resource Transfer.
STOCK_PROTOCOLS = [name for name in PROTOCOLS if name != "in-flight-switch"]


def main():
    global URL, DIAG
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--folder", required=True, help="the sandbox game under saves/ the save was copied into")
    parser.add_argument("--save", default="transfer-kerbin", help="the save, without .sfs")
    parser.add_argument("--protocol", choices=list(PROTOCOLS) + ["all"], default="all")
    parser.add_argument("--out", required=True, help="the folder for runs.json and the screenshots")
    parser.add_argument("--port", type=int, default=8770, help="the port of KSP-Util-MCPServer")
    options = parser.parse_args()
    URL = "http://127.0.0.1:%d/mcp/" % options.port
    DIAG = "resourcetransfer_read" in tool_names()
    log("KSP Diag - Resource Transfer", "installed" if DIAG else "not installed")

    names = STOCK_PROTOCOLS if options.protocol == "all" else [options.protocol]
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
