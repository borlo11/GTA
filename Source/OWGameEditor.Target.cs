using UnrealBuildTool;
using System.Collections.Generic;

public class OWGameEditorTarget : TargetRules
{
    public OWGameEditorTarget(TargetInfo Target) : base(Target)
    {
        Type = TargetType.Editor;
        DefaultBuildSettings = BuildSettingsVersion.Latest;
        ExtraModuleNames.Add("OWGame");
    }
}
