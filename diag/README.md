# Measurement files

What the protocols of [Resource Transfer Fix](../README.md) use and produce: their saves, the script that
plays them, and what each series wrote.

## The protocols

Described in [Checking the culprit: filling a tank](../docs/checking-the-culprit-filling.md),
[Checking the culprit: a tank of liquid fuel only](../docs/checking-the-culprit-fuel-only.md) and
[Checking several tanks](../docs/checking-several-tanks.md). They all use the same rocket and the same
script.

- [transfer-kerbin.sfs](transfer-kerbin.sfs): the save of every protocol but *several tanks to one*, and
  [transfer-kerbin-two-full.sfs](transfer-kerbin-two-full.sfs), the same with the fuselage full, for that
  one. Copy them into the folder of a sandbox game, and load the one the protocol names.
- [automation/run-transfers.py](automation/run-transfers.py): the script that plays them through
  [KSP-Util-MCPServer](https://github.com/lhervier/KSP-Util-MCPServer). Python 3 only, nothing to install.
- `stock/` and `fix/`: for each series, on stock and with this mod, `runs.json` (what the script printed)
  and `KSP.log`, which also holds the reading of
  [KSP Diag - Resource Transfer](https://github.com/lhervier/KSP-Diag-ResourceTransfer), installed in both.
  Every protocol was played in one session per series. The screenshots are in
  [../imgs/checking-the-culprit-filling/](../imgs/checking-the-culprit-filling/),
  [../imgs/checking-the-culprit-fuel-only/](../imgs/checking-the-culprit-fuel-only/) and
  [../imgs/checking-several-tanks/](../imgs/checking-several-tanks/).
