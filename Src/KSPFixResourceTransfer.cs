using System;
using HarmonyLib;
using UnityEngine;

namespace com.github.lhervier.ksp.fix.resourcetransfer
{
    /// <summary>
    /// Installs the fixes the settings turn on, once, when KSP starts: from then on, the In, Out and Stop
    /// buttons of resource transfers in part action windows do what they say.
    /// </summary>
    [KSPAddon(KSPAddon.Startup.Instantly, true)]
    public class KSPFixResourceTransfer : MonoBehaviour
    {
        private const string HarmonyId = "com.github.lhervier.ksp.fix.resourcetransfer";

        private void Start()
        {
            Settings.Load();
            Log.Info($"Version {typeof(KSPFixResourceTransfer).Assembly.GetName().Version}, " +
                $"stopIdleTransfers {Settings.StopIdleTransfers}, linkAllTransfers {Settings.LinkAllTransfers}, " +
                $"log level {Log.Level}");
            Harmony harmony = new Harmony(HarmonyId);
            if (Settings.StopIdleTransfers)
            {
                try
                {
                    IdleTransferStop.Install(harmony);
                    Log.Info("Idle transfers fix installed");
                }
                catch (Exception e)
                {
                    Log.Error($"Could not install the idle transfers fix, transfers stop as stock stops them: {e}");
                }
            }
            if (Settings.LinkAllTransfers)
            {
                try
                {
                    TransferLinks.Install(harmony);
                    Log.Info("Transfer links fix installed");
                }
                catch (Exception e)
                {
                    Log.Error($"Could not install the transfer links fix, transfers are linked as stock links them: {e}");
                }
            }
        }
    }
}
