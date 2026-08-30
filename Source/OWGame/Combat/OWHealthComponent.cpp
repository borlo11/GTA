#include "OWHealthComponent.h"

#include "../OWGame.h"

UOWHealthComponent::UOWHealthComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UOWHealthComponent::BeginPlay()
{
    Super::BeginPlay();

    Health = FMath::Max(1.0f, MaxHealth);
    bDead = false;
}

bool UOWHealthComponent::ApplyCombatDamage(float DamageAmount, AActor* DamageCauser)
{
    if (bDead || DamageAmount <= 0.0f)
    {
        return false;
    }

    const float PreviousHealth = Health;
    Health = FMath::Clamp(Health - DamageAmount, 0.0f, MaxHealth);

    if (FMath::IsNearlyEqual(PreviousHealth, Health))
    {
        return false;
    }

    UE_LOG(
        LogOWGame,
        Log,
        TEXT("%s took %.1f combat damage from %s (%.1f / %.1f HP)."),
        *GetNameSafe(GetOwner()),
        PreviousHealth - Health,
        *GetNameSafe(DamageCauser),
        Health,
        MaxHealth);

    OnHealthChanged.Broadcast(this, Health);

    if (Health <= 0.0f && !bDead)
    {
        bDead = true;

        UE_LOG(
            LogOWGame,
            Log,
            TEXT("%s reached zero health."),
            *GetNameSafe(GetOwner()));

        OnDeath.Broadcast(GetOwner());
    }

    return true;
}

void UOWHealthComponent::RestoreFullHealth()
{
    Health = FMath::Max(1.0f, MaxHealth);
    bDead = false;
    OnHealthChanged.Broadcast(this, Health);
}
