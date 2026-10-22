# Checking the culprit: filling a tank

Part of [Resource Transfer Fix](../README.md). A full tank fills an empty one through their part action
windows. Once the empty tank is full, does the full one go back to its In and Out buttons, or keep showing
Stop? Played without this mod, then with it.

## The install

KSP 1.12.5 with [KSP Community Fixes](https://github.com/KSPModdingLibs/KSPCommunityFixes) 1.41.1 (and the
Harmony and ModuleManager it needs), the base most players run, in French. *On stock* below means this
install. *With this mod* means this install with Resource Transfer Fix 0.1.0, both its patches on and its
log level set to `Debug` in `PluginData/settings.cfg`.
[KSP-Util-MCPServer](https://github.com/lhervier/KSP-Util-MCPServer) is installed too, to play the protocol
by script.

The game is in French: in the windows, *Sortie* is Out, *Entrée* is In, *Ergol liquide* is liquid fuel and
*Oxydant* oxidizer.

## The protocol

The save is [transfer-kerbin.sfs](../diag/transfer-kerbin.sfs): a sandbox game with a rocket on the launch
pad. Under its pod, from top to bottom: an FL-T200 tank, empty; a Mk1 Liquid Fuel Fuselage, empty; an
FL-T400 tank, full, which plays the tanker; an engine. Copy the save into the folder of a sandbox game, and
load it.

1. Right-click the FL-T400 to open its part action window, and pin it.
2. Right-click the FL-T200 to open its window.
3. In the FL-T200's window, press In under its liquid fuel.
4. Wait until the FL-T200 holds 90 units of liquid fuel out of 90, then two seconds more, and note the
   buttons under the FL-T400's liquid fuel.
5. Wait ten seconds, and note them again.

**Played by a script.** [run-transfers.py](../diag/automation/run-transfers.py) plays it through
KSP-Util-MCPServer, and drags the FL-T400's window to the left of the screen and the FL-T200's to the
right, so that both show. Python 3 only, nothing to install: start KSP with KSP-Util-MCPServer, copy the
save into a sandbox game, open that game, then run
`python run-transfers.py --folder <your sandbox game> --protocol filling --out out`. It takes a screenshot at
each step: before step 3, one second after it, at step 4 and at step 5.

## On stock

Read off the screenshots below, the liquid fuel of both tanks, and the buttons under it:

| Step | FL-T400 | its buttons | FL-T200 | its buttons |
|---|---|---|---|---|
| Before In | 180 / 180 | In, Out | 0 / 90 | In, Out |
| One second after In | 175 / 180 | Stop | 4.59 / 90 | Stop |
| FL-T200 full | 90 / 180 | **Stop** | 90 / 90 | In, Out |
| Ten seconds later | 90 / 180 | **Stop** | 90 / 90 | In, Out |

The FL-T200 stopped when it was full; the FL-T400 kept showing Stop, with 90 units left and nothing leaving
it.

<p class="thumbs"><a href="../imgs/checking-the-culprit-filling/stock/1-before.jpg"><img src="../imgs/checking-the-culprit-filling/stock/1-before.jpg" width="96"></a> <a href="../imgs/checking-the-culprit-filling/stock/2-filling.jpg"><img src="../imgs/checking-the-culprit-filling/stock/2-filling.jpg" width="96"></a> <a href="../imgs/checking-the-culprit-filling/stock/3-tank-full.jpg"><img src="../imgs/checking-the-culprit-filling/stock/3-tank-full.jpg" width="96"></a> <a href="../imgs/checking-the-culprit-filling/stock/4-ten-seconds-later.jpg"><img src="../imgs/checking-the-culprit-filling/stock/4-ten-seconds-later.jpg" width="96"></a></p>

<details>
<summary>The four screenshots, on stock</summary>

Before In:

![Before In, on stock](../imgs/checking-the-culprit-filling/stock/1-before.jpg)

One second after In:

![One second after In, on stock](../imgs/checking-the-culprit-filling/stock/2-filling.jpg)

The FL-T200 full:

![The FL-T200 full, on stock](../imgs/checking-the-culprit-filling/stock/3-tank-full.jpg)

Ten seconds later:

![Ten seconds later, on stock](../imgs/checking-the-culprit-filling/stock/4-ten-seconds-later.jpg)

</details>

## With this mod

Read off the screenshots below:

| Step | FL-T400 | its buttons | FL-T200 | its buttons |
|---|---|---|---|---|
| Before In | 180 / 180 | In, Out | 0 / 90 | In, Out |
| One second after In | 175 / 180 | Stop | 4.68 / 90 | Stop |
| FL-T200 full | 90 / 180 | **In, Out** | 90 / 90 | In, Out |
| Ten seconds later | 90 / 180 | **In, Out** | 90 / 90 | In, Out |

The transfer ran as on stock, and the FL-T400 went back to In and Out with the FL-T200.

<p class="thumbs"><a href="../imgs/checking-the-culprit-filling/fix/1-before.jpg"><img src="../imgs/checking-the-culprit-filling/fix/1-before.jpg" width="96"></a> <a href="../imgs/checking-the-culprit-filling/fix/2-filling.jpg"><img src="../imgs/checking-the-culprit-filling/fix/2-filling.jpg" width="96"></a> <a href="../imgs/checking-the-culprit-filling/fix/3-tank-full.jpg"><img src="../imgs/checking-the-culprit-filling/fix/3-tank-full.jpg" width="96"></a> <a href="../imgs/checking-the-culprit-filling/fix/4-ten-seconds-later.jpg"><img src="../imgs/checking-the-culprit-filling/fix/4-ten-seconds-later.jpg" width="96"></a></p>

<details>
<summary>The four screenshots, with this mod</summary>

Before In:

![Before In, with this mod](../imgs/checking-the-culprit-filling/fix/1-before.jpg)

One second after In:

![One second after In, with this mod](../imgs/checking-the-culprit-filling/fix/2-filling.jpg)

The FL-T200 full:

![The FL-T200 full, with this mod](../imgs/checking-the-culprit-filling/fix/3-tank-full.jpg)

Ten seconds later:

![Ten seconds later, with this mod](../imgs/checking-the-culprit-filling/fix/4-ten-seconds-later.jpg)

</details>

### What the log says

[`KSP.log`](../diag/fix/KSP.log) holds one line of the mod for this protocol, written when the FL-T200
became full:

```
[KSPFixResourceTransfer] [DEBUG] Stopped the LiquidFuel transfer out of fuelTank 1223746542: no tank takes from it any more
```

The stock log of the same protocol, [`KSP.log`](../diag/stock/KSP.log), has no line of the mod.

## What the measurements say

On stock, a tank that has filled another one keeps showing Stop for as long as it is not empty, here with
half its liquid fuel left. With this mod, it shows In and Out again as soon as the tank it filled is full.
The transfer itself, the amounts moved and the buttons of the tank that was filled are the same in both.
