#include "OWGameHUD.h"

#include "../OWGameCharacter.h"

#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "GameFramework/PlayerController.h"

void AOWGameHUD::DrawHUD()
{
    Super::DrawHUD();

    if (!Canvas || !PlayerOwner)
    {
        return;
    }

    const AOWGameCharacter* Character = Cast<AOWGameCharacter>(PlayerOwner->GetPawn());
    if (!Character)
    {
        return;
    }

    const FText Prompt = Character->GetInteractionPrompt();
    if (Prompt.IsEmpty())
    {
        return;
    }

    UFont* Font = GEngine ? GEngine->GetMediumFont() : nullptr;
    if (!Font)
    {
        return;
    }

    const FString Label = FString::Printf(TEXT("[E]  %s"), *Prompt.ToString());

    float TextWidth = 0.0f;
    float TextHeight = 0.0f;
    GetTextSize(Label, TextWidth, TextHeight, Font, 1.0f);

    const float X = (Canvas->ClipX - TextWidth) * 0.5f;
    const float Y = Canvas->ClipY * 0.82f;

    DrawText(
        Label,
        FLinearColor::White,
        X,
        Y,
        Font,
        1.0f,
        false);
}
