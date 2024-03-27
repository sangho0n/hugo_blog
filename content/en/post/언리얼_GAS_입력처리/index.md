---
title: "Unreal GAS Input Handling"
date: 2024-03-26T22:19:41+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[This post is a summary of lectures by 이득우](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4) and [documents compiled by other developers](https://github.com/tranek/GASDocumentation).

For detailed and accurate information, please refer to the provided links.

Series
- [Unreal GAS Overview](../unreal-gas-overview/)
- [Getting Started with Unreal GAS](../unreal-gas-start/)
- [Unreal GAS Input Handling](../unreal-gas-input-handling/) <- Current Post

---

In this post, we will explore how to trigger abilities (such as jump and attack) based on user input.

## OwnerActor and AvatarActor

In the Gameplay Ability System, OwnerActor refers to the actor that has the AbilitySystemComponent. In contrast, AvatarActor refers to the physical representation of the AbilitySystemComponent.

As seen in the previous post, OwnerActor and AvatarActor can be set to the same actor.
```c++
// For simple cases
AbilitySystemComponent->InitAbilityActorInfo(this, this);
```

Since a character's abilities are usually triggered based on the current state, it is common to set PlayerState as the OwnerActor. In this post, we will attach the ability system to the PlayerState and set the OwnerActor and AvatarActor accordingly.
(Note: Both actors must implement IAbilitySystemInterface even if Owner and Avatar are different.)
```c++
// Owner class
AABGASPlayerState::AABGASPlayerState()
{
    AbilitySystemComponent = CreateDefaultSubobject<UAbilitySystemComponent>(TEXT("AbiltiySystemComponent"));
    // AbilitySystemComponent->SetIsReplicated(true);
}

UAbilitySystemComponent* AABGASPlayerState::GetAbilitySystemComponent() const
{
    return AbilitySystemComponent;
}

// Avatar class
AABGASCharacterPlayer::AABGASCharacterPlayer()
{
    AbilitySystemComponent = nullptr;
    //AbilitySystemComponent->SetIsReplicated(true);
}

UAbilitySystemComponent* AABGASCharacterPlayer::GetAbilitySystemComponent() const
{
    return AbilitySystemComponent;
}

void AABGASCharacterPlayer::PossessedBy(AController* NewController)
{
    Super::PossessedBy(NewController);

    auto _PlayerState = GetPlayerState<AABGASPlayerState>();
    if(_PlayerState->IsValidLowLevelFast())
    {
        // Both the Avatar and PlayerState actors have an Ability System Component, but the Avatar's component is just a reference to the Owner's component.
        AbilitySystemComponent = _PlayerState->GetAbilitySystemComponent();
        AbilitySystemComponent->InitAbilityActorInfo(_PlayerState, this);
        // do sth...
        
// NOTE: In multiplayer games, InitAbilityActorInfo needs to be called in a different position!
// (PossessedBy method is only called on the server)
// For now, this is a single-player example, so when the controller possesses the pawn
// the InitAbilityActorInfo of the ability system is called
```

Furthermore, since PlayerState is a class that easily facilitates pub-sub between the server and clients, it is advisable to set the PlayerState class as the Owner in multiplayer game development.

## FGameplayAbilitySpec and FGameplayAbilitySpecHandle

As seen in the previous post, in order to grant abilities to the AbilitySystemComponent, you need to create and register an instance of the FGameplayAbilitySpec structure. You can register the created instance using the GiveAbility or GiveAbilityAndActivateOnce methods.
```c++
// Grant ability to the ability system component
for (auto Element : Abilities)
{
    FGameplayAbilitySpec Spec(Element);
    AbilitySystemComponent->GiveAbility(Spec);
}
    
// Some of the FGameplayAbilitySpec declaration
USTRUCT(BlueprintType)
struct GAMEPLAYABILITIES_API FGameplayAbilitySpec : public FFastArraySerializerItem
{
    GENERATED_USTRUCT_BODY()
    
    FGameplayAbilitySpec()
    : Ability(nullptr), Level(1), InputID(INDEX_NONE), SourceObject(nullptr), ActiveCount(0), InputPressed(false), RemoveAfterActivation(false), PendingRemove(false), bActivateOnce(false)
    { }
    
    /** Version that takes an ability class */
    FGameplayAbilitySpec(TSubclassOf<UGameplayAbility> InAbilityClass, int32 InLevel = 1, int32 InInputID = INDEX_NONE, UObject* InSourceObject = nullptr);
```

Once registered, you can access the granted abilities through the `FGameplayAbilitySpecContainer ActivatableAbilities` within the component.
```c++
// AbilitySystemComponent.h
UPROPERTY(ReplicatedUsing=OnRep_ActivateAbilities, BlueprintReadOnly, Category = "Abilities")
FGameplayAbilitySpecContainer ActivatableAbilities;
    
/** Returns the list of all activatable abilities. Read-only. */
const TArray<FGameplayAbilitySpec>& GetActivatableAbilities() const
{
    return ActivatableAbilities.Items;
}
    
/** Returns the list of all activatable abilities. */
TArray<FGameplayAbilitySpec>& GetActivatableAbilities()
{
    return ActivatableAbilities.Items;
}
```

In various ability triggering methods, you will notice that a structure called FGameplayAbilitySpecHandle is used as an argument. This is because the GameplayAbility system was designed to handle abilities and related structures as follows:
- **FGameplayAbilitySpec**: A structure that represents the ability itself. It contains information about the ability's state, activation count, etc.
- **FGameplayAbilitySpecHandle**: A structure used to uniquely identify a granted ability. One is created for each type of GameplayAbility.

The handle value increments by 1 automatically when a Spec is created.
```c++
/** Handle that points to a specific granted ability. These are globally unique */
USTRUCT(BlueprintType)
struct FGameplayAbilitySpecHandle
{
    GENERATED_USTRUCT_BODY()

    FGameplayAbilitySpecHandle()
        : Handle(INDEX_NONE)
    {
    }

    /** True if GenerateNewHandle was called on this handle */
    bool IsValid() const
    {
        return Handle != INDEX_NONE;
    }
    
// truncated part

private:

UPROPERTY()
int32 Handle;
};
```

## InputID

Now let's think about how to bind actions for triggering abilities. If using the traditional InputComponent, you would need to create a method for each action and pass it as an argument to BindAction.

When using GAS, however, you need to activate abilities by using tags, specs, and other methods from the AbilitySystemComponent. It is not practical to create a method for each action as before.

Therefore, the FGameplayAbilitySpec structure has an InputID field. By combining it with EnhancedInputComponent::BindAction, we can achieve universal input processing.
```c++
void AABGASCharacterPlayer::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    SetupGASInputComponent();
}

void AABGASCharacterPlayer::SetupGASInputComponent()
{
    if(IsValid(AbilitySystemComponent) && IsValid(InputComponent))
    {
        auto EnhancedInputComponent = CastChecked<UEnhancedInputComponent>(InputComponent);

        EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Triggered, this, &ThisClass::OnGASInputPressed, (int32)EPLAYERGASINPUTTYPE::JUMP);
        EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Completed, this, &ThisClass::OnGASInputReleased, (int32)EPLAYERGASINPUTTYPE::JUMP);
        EnhancedInputComponent->BindAction(AttackAction, ETriggerEvent::Triggered, this, &ThisClass::OnGASInputPressed, (int32)EPLAYERGASINPUTTYPE::ATTACK);
        EnhancedInputComponent->BindAction(AttackAction, ETriggerEvent::Completed, this, &ThisClass::OnGASInputReleased, (int32)EPLAYERGASINPUTTYPE::ATTACK);
    }
}

void AABGASCharacterPlayer::OnGASInputPressed(int32 InputID)
{
    auto Spec = AbilitySystemComponent->FindAbilitySpecFromInputID(InputID);
    if(Spec)
    {
        Spec->InputPressed = true;
        if (Spec->IsActive())
        {
            AbilitySystemComponent->AbilitySpecInputPressed(*Spec);
        }
        else
        {
            AbilitySystemComponent->TryActivateAbility(Spec->Handle);
        }
    }
}

void AABGASCharacterPlayer::OnGASInputReleased(int32 InputID)
{
    auto Spec = AbilitySystemComponent->FindAbilitySpecFromInputID(InputID);
    if(Spec)
    {
        Spec->InputPressed = false;
        if (Spec->IsActive())
        {
            AbilitySystemComponent->AbilitySpecInputReleased(*Spec);
        }
    }
}

```

Now once you have created and registered the Jump and Attack abilities and added them to the AbilitySystemComponent, the set actions will be triggered based on user input. Jump ability uses the default GAS plugin class, while the Attack ability class will be created using AbilityTask.

## InstancingPolicy

InstancingPolicy determines how the ability is instantiated when executed, limiting what an ability can do in its implementation. The types that can be specified are as follows:
```c++
UENUM(BlueprintType)
namespace EGameplayAbilityInstancingPolicy
{
    enum Type : int
    {
        // This ability is never instanced. Anything that executes the ability is operating on the CDO.
        NonInstanced,

        // Each actor gets their own instance of this ability. State can be saved, replication is possible.
        InstancedPerActor,

        // We instance this ability each time it is executed. Replication possible but not recommended.
        InstancedPerExecution,
    };
}
```

For a jump ability like the default class, it is best to follow the policy set by the base class.

## Ability Task and Gameplay Cue

Ability Tasks are executed only while the ability is active, whereas Gameplay Cues are used for tasks that do not directly affect the game. Abilities are triggered only once during one frame. For tasks that last over time, Ability Tasks and Gameplay Cues are utilized.
Ability tasks are used for tasks that directly impact the game, such as animations, root motion movement, response to attribute changes, and response to input.
Gameplay Cues are used for tasks that do not directly impact the game, like SFX, VFX, and Camera Shake.

In this post, we will create an Attack ability that plays the attack animation using an Ability Task. We will use the UAbilityTask_PlayMontageAndWait to play the animation.
Following the outlined pattern, we will create the ability task, bind callback functions in the ability class, use ReadyForActivation method to ensure the task can execute, and end the ability by calling EndAbility when the delegate is invoked.
```c++
void UABGA_Attack::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
    const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
    Super::ActivateAbility(Handle, ActorInfo, ActivationInfo, TriggerEventData);
    
    auto Character = CastChecked<AABCharacterBase>(ActorInfo->AvatarActor.Get());
    Character->GetCharacterMovement()->SetMovementMode(EMovementMode::MOVE_None);
    
    UAbilityTask_PlayMontageAndWait* PlayerAttackTask = UAbilityTask_PlayMontageAndWait::CreatePlayMontageAndWaitProxy(
        this,
        FName("PlayAttack"),
        Character->GetComboActionMontage()
    );
    PlayerAttackTask->OnCompleted.AddDynamic(this, &ThisClass::OnActionComplete);
    PlayerAttackTask->OnCompleted.AddDynamic(this, &ThisClass::OnActionInterrupted);
    PlayerAttackTask->ReadyForActivation();
}

void UABGA_Attack::EndAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
    const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateEndAbility, bool bWasCancelled)
{
    Super::EndAbility(Handle, ActorInfo, ActivationInfo, bReplicateEndAbility, bWasCancelled);
    
    auto Character = CastChecked<AABCharacterBase>(ActorInfo->AvatarActor.Get());
    Character->GetCharacterMovement()->SetMovementMode(EMovementMode::MOVE_Walking);

}

void UABGA_Attack::OnActionComplete()
{
    EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, false);
}

void UABGA_Attack::OnActionInterrupted()
{
    EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, true);
}
```

## Debugging

If you have succeeded in handling inputs, you should now see the desired actions (jump, attack) being triggered based on the user's input. If not, it is necessary to determine where the bug occurred. To do this, add gameplay tags to the abilities and call the console command `showdebug abilitysystem` to display it in the PIE viewport when the AbilitySystemComponent is initialized via cpp.
```c++
void AABGASCharacterPlayer::PossessedBy(AController* NewController)
{
    Super::PossessedBy(NewController);
    
    #if WITH_EDITOR
    auto PlayerController = CastChecked<APlayerController>(NewController);
    if(IsLocallyControlled())
        PlayerController->ConsoleCommand(TEXT("showdebug abilitysystem"));
    #endif
}
```

## Final Result
<center>

![debug.gif](img/post/gas/debug.gif)

</center>