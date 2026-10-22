using System.Collections.Generic;
using HarmonyLib;

namespace com.github.lhervier.ksp.fix.resourcetransfer
{
    /// <summary>
    /// Links every resource transfer control that is set up with the controls of the same resource that the
    /// other open part action windows show, so that its In and Out buttons have tanks to work with.
    ///
    /// Stock links a control only with the controls registered since the start of the frame:
    /// UIPartActionController.UpdateActiveWindows empties that list every frame, and only a control just
    /// created or refreshed by a window that opens is registered. A control built again one frame after the
    /// others is linked with none. Opening the window of a tank that holds only one of the resources of the
    /// others (liquid fuel only, next to tanks of liquid fuel and oxidizer) does it: the oxidizer buttons
    /// leave every window, and come back unlinked, in the window of the next tank and in the ones still open.
    /// </summary>
    internal static class TransferLinks
    {
        /// <summary>The controls stock links a new one with: those registered since the start of the frame.</summary>
        private static readonly AccessTools.FieldRef<UIPartActionController, List<UIPartActionResourceTransfer>> StockTransfers =
            AccessTools.FieldRefAccess<UIPartActionController, List<UIPartActionResourceTransfer>>("transfers");

        /// <summary>Patches UIPartActionController.SetupResourceTransfer with <see cref="Prefix"/>.</summary>
        public static void Install(Harmony harmony)
        {
            var target = AccessTools.Method(typeof(UIPartActionController), "SetupResourceTransfer");
            harmony.Patch(target, prefix: new HarmonyMethod(typeof(TransferLinks), nameof(Prefix)));
        }

        /// <summary>
        /// Links <paramref name="trans"/> both ways with every transfer control of the same resource, on another
        /// part, that an open window of <paramref name="__instance"/> shows. Stock then runs as usual: it only
        /// adds links, and adds none twice.
        /// </summary>
        private static void Prefix(UIPartActionController __instance, UIPartActionResourceTransfer trans)
        {
            if (trans == null || trans.Resource == null || trans.Targets == null || __instance.windows == null)
            {
                return;
            }
            int resourceId = trans.Resource.info.id;
            List<UIPartActionResourceTransfer> stockLinks = StockTransfers(__instance);
            // The links stock would not have made: the log tells them apart.
            int added = 0;
            foreach (UIPartActionWindow window in __instance.windows)
            {
                if (window == null)
                {
                    continue;
                }
                foreach (UIPartActionItem item in window.ListItems)
                {
                    UIPartActionResourceTransfer other = item as UIPartActionResourceTransfer;
                    if (other == null || other == trans || other.Resource == null || other.Targets == null)
                    {
                        continue;
                    }
                    if (other.Resource.info.id != resourceId || other.Part == trans.Part)
                    {
                        continue;
                    }
                    if (!other.Targets.Contains(trans))
                    {
                        other.Targets.Add(trans);
                    }
                    if (!trans.Targets.Contains(other))
                    {
                        trans.Targets.Add(other);
                        if (stockLinks == null || !stockLinks.Contains(other))
                        {
                            added++;
                        }
                    }
                }
            }
            if (added > 0 && Log.IsDebugEnabled)
            {
                Log.Debug($"Linked the {trans.Resource.resourceName} transfer of {IdleTransferStop.PartName(trans.Part)} " +
                    $"with {added} tank(s) stock does not link it with here, {trans.Targets.Count} in all");
            }
        }
    }
}
