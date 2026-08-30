#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "OWHealthComponent.generated.h"

class UOWHealthComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(
    FOWHealthChangedSignature,
    UOWHealthComponent*, HealthComponent,
    float, NewHealth);

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(
    FOWDeathSignature,
    AActor*, DeadActor);

UCLASS(ClassGroup=(OWGame), meta=(BlueprintSpawnableComponent))
class OWGAME_API UOWHealthComponent : public UActorComponent
{
    GENERATED_BODY()

public:
    UOWHealthComponent();

    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category="Combat")
    bool ApplyCombatDamage(float DamageAmount, AActor* DamageCauser);

    UFUNCTION(BlueprintCallable, Category="Combat")
    void RestoreFullHealth();

    UFUNCTION(BlueprintPure, Category="Combat")
    float GetHealth() const { return Health; }

    UFUNCTION(BlueprintPure, Category="Combat")
    float GetMaxHealth() const { return MaxHealth; }

    UFUNCTION(BlueprintPure, Category="Combat")
    float GetHealthNormalized() const
    {
        return MaxHealth > 0.0f ? FMath::Clamp(Health / MaxHealth, 0.0f, 1.0f) : 0.0f;
    }

    UFUNCTION(BlueprintPure, Category="Combat")
    bool IsDead() const { return bDead; }

    UPROPERTY(BlueprintAssignable, Category="Combat")
    FOWHealthChangedSignature OnHealthChanged;

    UPROPERTY(BlueprintAssignable, Category="Combat")
    FOWDeathSignature OnDeath;

protected:
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Combat", meta=(ClampMin="1.0", ClampMax="10000.0"))
    float MaxHealth = 100.0f;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Combat")
    float Health = 100.0f;

    UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Combat")
    bool bDead = false;
};
