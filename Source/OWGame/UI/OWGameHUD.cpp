#include "OWGameHUD.h"

#include "../OWGameCharacter.h"
#include "../OWGamePlayerController.h"
#include "../Crime/OWWantedComponent.h"

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

    UFont* Font = GEngine ? GEngine->GetMediumFont() : nullptr;
    if (!Font)
    {
        return;
    }

    if (const AOWGamePlayerController* OWController =
        Cast<AOWGamePlayerController>(PlayerOwner))
    {
        if (const UOWWantedComponent* Wanted = OWController->GetWantedComponent())
        {
            const int32 WantedLevel = Wanted->GetWantedLevel();
            if (WantedLevel > 0)
            {
                FString Stars;
                for (int32 Index = 0; Index < WantedLevel; ++Index)
                {
                    Stars += TEXT("* ");
                }

                const FString WantedLabel =
                    FString::Printf(TEXT("RICERCATO  %s"), *Stars);

                float WantedWidth = 0.0f;
                float WantedHeight = 0.0f;
                GetTextSize(WantedLabel, WantedWidth, WantedHeight, Font, 1.15f);

                DrawText(
                    WantedLabel,
                    FLinearColor(1.0f, 0.72f, 0.15f, 1.0f),
                    Canvas->ClipX - WantedWidth - 40.0f,
                    34.0f,
                    Font,
                    1.15f,
                    false);
            }
        }
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
