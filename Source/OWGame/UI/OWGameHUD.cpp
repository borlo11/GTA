#include "OWGameHUD.h"

#include "../OWGameCharacter.h"
#include "../OWGamePlayerController.h"
#include "../Crime/OWWantedComponent.h"
#include "../Combat/OWHealthComponent.h"
#include "../Mission/OWMissionComponent.h"

#include "Engine/Canvas.h"
#include "Engine/Engine.h"
#include "Engine/Font.h"
#include "GameFramework/PlayerController.h"
#include "Misc/App.h"

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
        if (const UOWMissionComponent* Mission = OWController->GetMissionComponent())
        {
            const EOWMissionState MissionState = Mission->GetMissionState();
            if (MissionState != EOWMissionState::Inactive)
            {
                DrawRect(
                    FLinearColor(0.0f, 0.0f, 0.0f, 0.42f),
                    22.0f,
                    22.0f,
                    440.0f,
                    68.0f);

                const FString MissionTitle =
                    FString::Printf(TEXT("MISSIONE: %s"), *Mission->GetMissionTitle().ToString());

                DrawText(
                    MissionTitle,
                    FLinearColor(1.0f, 0.86f, 0.25f, 1.0f),
                    34.0f,
                    34.0f,
                    Font,
                    1.05f,
                    false);

                FString ObjectiveLabel = Mission->GetCurrentObjectiveText().ToString();
                const float DistanceCm = Mission->GetCurrentObjectiveDistance();
                if (MissionState == EOWMissionState::Active && DistanceCm >= 0.0f)
                {
                    ObjectiveLabel += FString::Printf(
                        TEXT("  (%.0f m)"),
                        DistanceCm / 100.0f);
                }

                if (!ObjectiveLabel.IsEmpty())
                {
                    DrawText(
                        ObjectiveLabel,
                        FLinearColor::White,
                        34.0f,
                        62.0f,
                        Font,
                        0.95f,
                        false);
                }
            }
            else
            {
                DrawRect(
                    FLinearColor(0.0f, 0.0f, 0.0f, 0.30f),
                    22.0f,
                    22.0f,
                    390.0f,
                    42.0f);

                DrawText(
                    TEXT("HOT RUN disponibile - cerca il marker verde"),
                    FLinearColor(0.72f, 1.0f, 0.72f, 1.0f),
                    34.0f,
                    34.0f,
                    Font,
                    0.90f,
                    false);
            }

            if (Mission->ShouldShowCompletionBanner())
            {
                const FString CompletionLabel = TEXT("MISSIONE COMPLETATA");
                float BannerWidth = 0.0f;
                float BannerHeight = 0.0f;
                GetTextSize(
                    CompletionLabel,
                    BannerWidth,
                    BannerHeight,
                    Font,
                    1.65f);

                const float BannerX =
                    (Canvas->ClipX - BannerWidth) * 0.5f;
                const float BannerY =
                    Canvas->ClipY * 0.24f;

                DrawRect(
                    FLinearColor(0.0f, 0.0f, 0.0f, 0.62f),
                    BannerX - 28.0f,
                    BannerY - 16.0f,
                    BannerWidth + 56.0f,
                    BannerHeight + 32.0f);

                DrawText(
                    CompletionLabel,
                    FLinearColor(1.0f, 0.86f, 0.25f, 1.0f),
                    BannerX,
                    BannerY,
                    Font,
                    1.65f,
                    false);
            }
        }

        if (OWController->IsPerformanceOverlayVisible())
        {
            const double DeltaSeconds =
                FMath::Max(FApp::GetDeltaTime(), 0.000001);
            const double FrameMs = DeltaSeconds * 1000.0;
            const double FPS = 1.0 / DeltaSeconds;

            const FString PerfLabel = FString::Printf(
                TEXT("PERF  %.0f FPS  |  %.2f ms  |  target 60 / 16.67"),
                FPS,
                FrameMs);

            float PerfWidth = 0.0f;
            float PerfHeight = 0.0f;
            GetTextSize(PerfLabel, PerfWidth, PerfHeight, Font, 0.85f);

            const float PerfX =
                Canvas->ClipX - PerfWidth - 28.0f;
            const float PerfY =
                Canvas->ClipY - 44.0f;

            DrawRect(
                FLinearColor(0.0f, 0.0f, 0.0f, 0.55f),
                PerfX - 12.0f,
                PerfY - 8.0f,
                PerfWidth + 24.0f,
                PerfHeight + 16.0f);

            DrawText(
                PerfLabel,
                FrameMs <= 16.67
                    ? FLinearColor(0.55f, 1.0f, 0.55f, 1.0f)
                    : FLinearColor(1.0f, 0.72f, 0.25f, 1.0f),
                PerfX,
                PerfY,
                Font,
                0.85f,
                false);
        }

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

                DrawRect(
                    FLinearColor(0.0f, 0.0f, 0.0f, 0.42f),
                    Canvas->ClipX - WantedWidth - 54.0f,
                    22.0f,
                    WantedWidth + 28.0f,
                    WantedHeight + 24.0f);

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

    // M6 lightweight combat feedback while the on-foot character is possessed.
    const float CenterX = Canvas->ClipX * 0.5f;
    const float CenterY = Canvas->ClipY * 0.5f;
    const float CrosshairHalfSize = 7.0f;

    DrawLine(
        CenterX - CrosshairHalfSize,
        CenterY,
        CenterX + CrosshairHalfSize,
        CenterY,
        FLinearColor::White,
        1.5f);

    DrawLine(
        CenterX,
        CenterY - CrosshairHalfSize,
        CenterX,
        CenterY + CrosshairHalfSize,
        FLinearColor::White,
        1.5f);

    if (const UOWHealthComponent* Health = Character->GetHealthComponent())
    {
        const FString HealthLabel = FString::Printf(
            TEXT("HP  %.0f / %.0f"),
            Health->GetHealth(),
            Health->GetMaxHealth());

        DrawText(
            HealthLabel,
            Health->GetHealthNormalized() > 0.30f
                ? FLinearColor::White
                : FLinearColor(1.0f, 0.25f, 0.20f, 1.0f),
            34.0f,
            Canvas->ClipY - 54.0f,
            Font,
            1.0f,
            false);
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
