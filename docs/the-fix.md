# The fix: stop what no longer flows, pair with every open window

Part of [Resource Transfer Fix](../README.md). The two patches, what each changes, and what they leave
as stock has it. Why they are needed is in [The culprit](the-culprit.md).

## Two patches, two switches

Each patch has its own switch in `PluginData/settings.cfg`, both `True` by default, read once when KSP
starts. A patch turned off is not installed: that half of the transfer behaves exactly as on stock. Neither
patch saves anything: removing the mod gives the stock behaviour back at once.

## `stopIdleTransfers`: stop what no longer flows

A Harmony postfix of `UIPartActionResourceTransfer.UpdateItem` (`Src/IdleTransferStop.cs`). After stock has
updated a transfer control, and if the control is still sending or taking, the mod looks at its shown
targets:

- a control that sends (`Out`) stops when none of them takes (`In`);
- a control that takes (`In`) stops when none of them sends (`Out`).

"Shown" means a target whose window is open: stock moves resources only between shown controls, and the
controls of a closed window are kept, hidden, until it opens again.

With it, the tank that filled another one stops on the frame after the full tank stops; and two tanks
filled from a third stop on the frame after the third runs dry. A transfer that still flows is never
stopped: a control taking from at least one control sending, or the other way round, is left to stock.

At `Debug`, the mod writes one line for each control it stops:

```
[KSPFixResourceTransfer] [DEBUG] Stopped the LiquidFuel transfer out of fuelTank 1223746542: no tank takes from it any more
```

## `linkAllTransfers`: pair with every open window

A Harmony prefix of `UIPartActionController.SetupResourceTransfer` (`Src/TransferLinks.cs`). Before stock
pairs a new or refreshed control with the controls listed since the start of the frame, the mod pairs it,
both ways, with every transfer control of the same resource, on another part, that an open window shows.
Stock then runs as usual; a pair already made is not made twice.

The mod pairs with what the player sees, whatever the frame the control was created on. A control on a
closed window is not paired with: as on stock, opening that window pairs it.

While it pairs, the mod also drops, from the pairs of each control it pairs the new one with, the controls
that have been destroyed. Stock judges a control with a destroyed pair invalid
(`UIPartActionResourceTransfer.IsItemValid`), and its window builds it again; a window destroys an invalid
control before building the new one. When a window is built again, its old controls are left in the pairs of
the other windows' controls; on stock, the controls built again in turn are paired with nothing, and that
ends there. Since the mod pairs the new ones, a destroyed pair left in place would have the other window's
control built again, whose new control would leave a destroyed pair in turn, and so on, on every frame. A
window built again while paired is what
[Checked: a tank's contents switched in flight](checking-in-flight-switch.md) plays.

At `Debug`, the mod writes one line for each control it pairs with tanks that stock does not pair it with
at that point:

```
[KSPFixResourceTransfer] [DEBUG] Linked the Oxidizer transfer of fuelTank 1223746542 with 1 tank(s) stock does not link it with here, 1 in all
```

and one line for each control it drops destroyed controls from:

```
[KSPFixResourceTransfer] [DEBUG] Dropped 1 destroyed control(s) from the LiquidFuel transfer of fuelTankSmall 649418999
```

## What it leaves alone

- How much moves, and how fast: the share each tank takes, and the order of the windows, are stock's.
- When a transfer control shows, and which buttons it shows in each state.
- The In, Out and Stop buttons themselves, and the input locks they obey.
- Pairs that stock makes: the mod only adds pairs, and removes none but the pairs with destroyed controls.
