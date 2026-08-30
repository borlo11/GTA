#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "TimerManager.h"
#include "OWGameCharacter.generated.h"

class UCameraComponent;
class UOWHealthComponent;
class USceneComponent;
class USpringArmComponent;
class UStaticMeshComponent;
class UInputAction;
class UInputMappingContext;

UCLASS()
class OWGAME_API AOWGameCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AOWGameCharacter();

    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintPure, Category="Interaction")
    float GetInteractionRange() const { return InteractionRange; }

    UFUNCTION(BlueprintPure, Category="Interaction")
    float GetInteractionAssistRadius() const { return InteractionAssistRadius; }

    UFUNCTION(BlueprintPure, Category="Interaction")
    FText GetInteractionPrompt() const { return InteractionPrompt; }

    UFUNCTION(BlueprintPure, Category="Movement")
    float GetWalkSpeed() const { return WalkSpeed; }

    UFUNCTION(BlueprintPure, Category="Movement")
    float GetSprintSpeed() const { return SprintSpeed; }

    UFUNCTION(BlueprintPure, Category="Visual")
    bool IsUsingTemplateSkeletalCharacter() const;

    UFUNCTION(BlueprintPure, Category="Combat")
    UOWHealthComponent* GetHealthComponent() const { return HealthComponent; }

    UFUNCTION(BlueprintPure, Category="Combat")
    float GetRangedDamage() const { return RangedDamage; }

    UFUNCTION(BlueprintPure, Category="Combat")
    float GetMeleeDamage() const { return MeleeDamage; }

    UFUNCTION(BlueprintPure, Category="Combat")
    float GetRangedRange() const { return RangedRange; }

    UFUNCTION(BlueprintPure, Category="Combat")
    float GetMeleeRange() const { return MeleeRange; }

    void ActivateOnFootInput();

protected:
    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
    void StartJump();
    void StopJump();
    void StartSprint();
    void StopSprint();
    void TryInteract();
    void FirePrototypeWeapon();
    void PerformMeleeAttack();
    AActor* FindCombatTarget(
        const FVector& Start,
        const FVector& End,
        float SweepRadius,
        FVector& OutImpactPoint) const;
    void ReportCombatCrime(AActor* HitActor, bool bMelee);
    void ApplyCombatHit(AActor* HitActor, float DamageAmount, bool bMelee);

    UFUNCTION()
    void HandlePlayerDeath(AActor* DeadActor);

    void ResolveInputAssets();
    void BuildRuntimeMappingContext();
    void ApplyDefaultMappingContext();
    bool TryApplyTemplateSkeletalCharacter();
    void UsePrototypeVisualFallback();

    void UpdateInteractionFocus();
    AActor* FindInteractableInView();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Visual")
    TObjectPtr<USceneComponent> VisualRoot;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Visual")
    TObjectPtr<UStaticMeshComponent> TorsoMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Visual")
    TObjectPtr<UStaticMeshComponent> HeadMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Visual")
    TObjectPtr<UStaticMeshComponent> LeftArmMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Visual")
    TObjectPtr<UStaticMeshComponent> RightArmMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Visual")
    TObjectPtr<UStaticMeshComponent> LeftLegMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Visual")
    TObjectPtr<UStaticMeshComponent> RightLegMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera")
    TObjectPtr<USpringArmComponent> CameraBoom;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera")
    TObjectPtr<UCameraComponent> FollowCamera;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Combat")
    TObjectPtr<UOWHealthComponent> HealthComponent;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputMappingContext> DefaultMappingContext;

    UPROPERTY(Transient)
    TObjectPtr<UInputMappingContext> RuntimeDefaultMappingContext;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputAction> MoveAction;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputAction> LookAction;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputAction> JumpAction;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputAction> InteractAction;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement", meta=(ClampMin="100.0", ClampMax="1200.0"))
    float WalkSpeed = 500.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Movement", meta=(ClampMin="100.0", ClampMax="1600.0"))
    float SprintSpeed = 760.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Camera", meta=(ClampMin="100.0", ClampMax="1000.0"))
    float CameraDistance = 420.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Camera", meta=(ClampMin="0.1", ClampMax="5.0"))
    float LookSensitivity = 1.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction", meta=(ClampMin="100.0", ClampMax="2000.0"))
    float InteractionRange = 800.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction", meta=(ClampMin="1.0", ClampMax="250.0"))
    float InteractionAssistRadius = 70.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Interaction", meta=(ClampMin="0.05", ClampMax="1.0"))
    float InteractionFocusInterval = 0.12f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Combat", meta=(ClampMin="1.0", ClampMax="500.0"))
    float RangedDamage = 40.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Combat", meta=(ClampMin="100.0", ClampMax="20000.0"))
    float RangedRange = 6000.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Combat", meta=(ClampMin="1.0", ClampMax="200.0"))
    float RangedSweepRadius = 28.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Combat", meta=(ClampMin="1.0", ClampMax="500.0"))
    float MeleeDamage = 55.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Combat", meta=(ClampMin="50.0", ClampMax="500.0"))
    float MeleeRange = 190.0f;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Combat", meta=(ClampMin="20.0", ClampMax="250.0"))
    float MeleeSweepRadius = 85.0f;

    UPROPERTY(Transient)
    FText InteractionPrompt;

    TWeakObjectPtr<AActor> FocusedInteractable;
    FTimerHandle InteractionFocusTimer;

    UPROPERTY(EditAnywhere, Category="Debug")
    bool bDrawInteractionTrace = false;
};
