using HarmonyLib;

namespace com.github.lhervier.ksp.fix.resourcetransfer
{
    /// <summary>
    /// Stops a resource transfer control once nothing can flow through it any more: a control sending (Out)
    /// when none of the controls it is linked with takes (In), a control taking when none sends.
    ///
    /// Stock stops a sending control only when its own tank is empty, and keeps a taking control going while
    /// any control it is linked with is not idle, sending or taking alike. A tank that fills up stops, and the
    /// tank that filled it keeps its Stop button although nothing leaves it; two tanks that take from one
    /// that runs dry keep each other going, and their Stop buttons, for good.
    /// </summary>
    internal static class IdleTransferStop
    {
        /// <summary>Patches UIPartActionResourceTransfer.UpdateItem with <see cref="Postfix"/>.</summary>
        public static void Install(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(UIPartActionResourceTransfer), "UpdateItem");
            harmony.Patch(target, postfix: new HarmonyMethod(typeof(IdleTransferStop), nameof(Postfix)));
        }

        /// <summary>
        /// Stops <paramref name="__instance"/> when, after stock has updated it, it still sends or takes but none
        /// of the shown controls it is linked with does the other half of the transfer.
        /// </summary>
        private static void Postfix(UIPartActionResourceTransfer __instance)
        {
            UIPartActionResourceTransfer.FlowState state = __instance.State;
            if (state == UIPartActionResourceTransfer.FlowState.None || __instance.Targets == null)
            {
                return;
            }
            UIPartActionResourceTransfer.FlowState other = state == UIPartActionResourceTransfer.FlowState.Out
                ? UIPartActionResourceTransfer.FlowState.In
                : UIPartActionResourceTransfer.FlowState.Out;
            // Only shown controls take part in a transfer: stock skips the others too.
            foreach (UIPartActionResourceTransfer target in __instance.Targets)
            {
                if (target != null && target.gameObject.activeInHierarchy && target.State == other)
                {
                    return;
                }
            }
            if (Log.IsDebugEnabled)
            {
                Log.Debug($"Stopped the {__instance.Resource?.resourceName} transfer {(state == UIPartActionResourceTransfer.FlowState.Out ? "out of" : "into")} " +
                    $"{PartName(__instance.Part)}: no tank {(state == UIPartActionResourceTransfer.FlowState.Out ? "takes from it" : "sends to it")} any more");
            }
            __instance.FlowStop();
        }

        /// <summary>The name a log line gives a part: its part name and its persistent id.</summary>
        internal static string PartName(Part part)
        {
            return part == null ? "(no part)" : $"{part.partInfo.name} {part.persistentId}";
        }
    }
}
