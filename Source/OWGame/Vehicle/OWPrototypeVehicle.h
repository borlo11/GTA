#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "Interaction/OWInteractable.h"
#include "OWPrototypeVehicle.generated.h"

class AOWGameCharacter;
class UCameraComponent;
class UInputAction;
class UInputMappingContext;
class UFloatingPawnMovement;
class UPawnMovementComponent;
class USpringArmComponent;
class UStaticMeshComponent;
struct FInputActionValue;

UCLASS()
class OWGAME_API AOWPrototypeVehicle : public APawn, public IOWInteractable
{
    GENERATED_BODY()

public:
    AOWPrototypeVehicle();

    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual void PossessedBy(AController* NewController) override;
    virtual void UnPossessed() override;
    virtual UPawnMovementComponent* GetMovementComponent() const override;

    virtual bool CanInteract_Implementation(AActor* Interactor) const override;
    virtual void Interact_Implementation(AActor* Interactor) override;

    UFUNCTION(BlueprintPure, Category="Vehicle")
    bool IsOccupied() const;

    UFUNCTION(BlueprintPure, Category="Vehicle")
    float GetConfiguredMaxSpeed() const;

protected:
    void Throttle(const FInputActionValue& Value);
    void Steer(const FInputActionValue& Value);
    void Look(const FInputActionValue& Value);
    void Brake();
    void ExitVehicle();

    void ResolveInputAssets();
    void AddVehicleMappingContext(AController* InController);
    void RemoveVehicleMappingContext(AController* InController);
    void RestoreDriverCharacter();

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Vehicle")
    TObjectPtr<UStaticMeshComponent> VehicleMesh;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Vehicle")
    TObjectPtr<UFloatingPawnMovement> VehicleMovement;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera")
    TObjectPtr<USpringArmComponent> CameraBoom;

    UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Camera")
    TObjectPtr<UCameraComponent> FollowCamera;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputMappingContext> VehicleMappingContext;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputAction> ThrottleAction;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputAction> SteerAction;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputAction> BrakeAction;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputAction> ExitAction;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Input")
    TObjectPtr<UInputAction> LookAction;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Vehicle", meta=(ClampMin="10.0", ClampMax="180.0"))
    float SteeringRateDegreesPerSecond = 75.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Vehicle")
    FVector ExitOffset = FVector(0.0f, 220.0f, 100.0f);

    UPROPERTY(Transient)
    TObjectPtr<AOWGameCharacter> DriverCharacter;
};
