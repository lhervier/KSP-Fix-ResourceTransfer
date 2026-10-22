# Measurement files

What the protocols of [Resource Transfer Fix](../README.md) use and produce: their saves, the script that
plays them, and what each series wrote.

## The protocols

Described in [Checking the culprit: filling a tank](../docs/checking-the-culprit-filling.md),
[Checking the culprit: a tank of liquid fuel only](../docs/checking-the-culprit-fuel-only.md) and
[Checking several tanks](../docs/checking-several-tanks.md), on one rocket, and
[Checking other resources](../docs/checking-other-resources.md) and
[Checking transfers that obey crossfeed](../docs/checking-crossfeed.md), on another. One script plays them
all.

- [transfer-kerbin.sfs](transfer-kerbin.sfs): the save of every protocol but *several tanks to one*, and
  [transfer-kerbin-two-full.sfs](transfer-kerbin-two-full.sfs), the same with the fuselage full, for that
  one. Copy them into the folder of a sandbox game, and load the one the protocol names.
- [transfer-resources-kerbin.sfs](transfer-resources-kerbin.sfs): the save of *other resources*, with its
  own rocket, and [transfer-crossfeed-kerbin.sfs](transfer-crossfeed-kerbin.sfs), the same rocket in a game
  whose transfers obey crossfeed, for *crossfeed*.
- [automation/run-transfers.py](automation/run-transfers.py): the script that plays them through
  [KSP-Util-MCPServer](https://github.com/lhervier/KSP-Util-MCPServer). Python 3 only, nothing to install.
- `stock/` and `fix/`: for each series, on stock and with this mod, `runs.json` (what the script printed)
  and `KSP.log`, which also holds the reading of
  [KSP Diag - Resource Transfer](https://github.com/lhervier/KSP-Diag-ResourceTransfer), installed in both.
  The protocols of the first three pages were played in one session per series. The screenshots are in
  [../imgs/checking-the-culprit-filling/](../imgs/checking-the-culprit-filling/),
  [../imgs/checking-the-culprit-fuel-only/](../imgs/checking-the-culprit-fuel-only/) and
  [../imgs/checking-several-tanks/](../imgs/checking-several-tanks/).
- `other-resources/stock/` and `other-resources/fix/`, `crossfeed/stock/` and `crossfeed/fix/`: the same for
  *other resources* and *crossfeed*, each played in sessions of its own; their screenshots are in
  [../imgs/checking-other-resources/](../imgs/checking-other-resources/) and
  [../imgs/checking-crossfeed/](../imgs/checking-crossfeed/).
