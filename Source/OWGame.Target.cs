using UnrealBuildTool;
using System.Collections.Generic;

public class OWGameTarget : TargetRules
{
    public OWGameTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Game;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        ExtraModuleNames.Add("OWGame");
    }
}
