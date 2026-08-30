#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InputActionValue.h"
#include "TimerManager.h"
#include "OWGameCharacter.generated.h"

class UCameraComponent;
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

    void ActivateOnFootInput();

protected:
    void Move(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
    void StartJump();
    void StopJump();
    void StartSprint();
    void StopSprint();
    void TryInteract();

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

    UPROPERTY(Transient)
    FText InteractionPrompt;

    TWeakObjectPtr<AActor> FocusedInteractable;
    FTimerHandle InteractionFocusTimer;

    UPROPERTY(EditAnywhere, Category="Debug")
    bool bDrawInteractionTrace = false;
};
