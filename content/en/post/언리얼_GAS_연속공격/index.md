---
title: "Unreal GAS Continuous Attack Implementation"
date: 2024-04-01T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

This post is a summary based on [Lee Deukwoo's lecture](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4) and [documentation prepared by another developer](https://github.com/tranek/GASDocumentation).

For detailed and accurate information, please refer to the above links.

## Series
### Basics of GAS
- [Unreal GAS Overview](../Unreal-GAS-Overview/)
- [Getting Started with Unreal GAS](../Unreal-GAS-Getting-Started/)
### Basic Character Creation with GAS
- [Handling Input in Unreal GAS](../Unreal-GAS-Input-Handling/)
- [Implementing Continuous Attacks in Unreal GAS](../Unreal-GAS-Continuous-Attack-Implementation/) <- Current Post
- [Implementing Attack Judgment System in Unreal GAS](../Unreal-GAS-Attack-Judgment-System/)
### Attributes and Gameplay Effects
- Unreal GAS Character Attributes
- Unreal GAS Gameplay Effects
- Interfacing Attributes and UI in Unreal GAS
### Utilizing GAS
- Implementing Item Crate in Unreal GAS
- Implementing Area of Effect Skill in Unreal GAS

---

In this post, we will explore how animation sections registered in animation montages can be played in GAS and create a custom Task while learning how to use Ability Tasks in blueprints.

## Implementing Continuous Attack

In the previous post, we represented the attack motion by playing the first section of the animation montage using UAbilityTask_PlayMontageAndWait.
The Gameplay Ability class in GAS already defines a method that allows changing the animation to be played based on the section's name.

```c++
void UGameplayAbility::MontageJumpToSection(FName SectionName)
{
    check(CurrentActorInfo);

    UAbilitySystemComponent* const AbilitySystemComponent = GetAbilitySystemComponentFromActorInfo_Checked();
    if (AbilitySystemComponent->IsAnimatingAbility(this))
    {
       AbilitySystemComponent->CurrentMontageJumpToSection(SectionName);
    }
}
```

Let's implement continuous attacks using this method.

---

### Naive Approach

The most basic mechanism to implement continuous attacks is as follows:
- Register the animation montage in the animation instance
- Set an AnimNotify (NextComboCheck) to verify at the end of each animation montage section if it can transition to the next section
- When an attack request is received before the attack ends, set a flag to proceed to the next section
- Check the flag in AnimNotify and transition to the next section using the Montage_JumpToSection method

```c++
// Invoked upon attack input
void AMyCharacter::AttackNonEquip_Multicast_Implementation()
{
	auto animInstance = Cast<UMSBAnimInstance>(GetMesh()->GetAnimInstance());
	if(CharacterState->IsAttacking())
	{
		animInstance->SetNextComboInputOn(true);
	}
	else
	{
		CharacterState->SetAttacking(true);
		animInstance->PlayComboAnim();
	}
}

// Play continuous attack animation montage
void UMyAnimInstance::PlayComboAnim()
{
	CurrentCombo = 1;
	NextComboInputOn = false;
	
	Montage_Play(ComboMontage);
}

void UMyAnimInstance::AnimNotify_NextComboCheck()
{
	if(NextComboInputOn)
	{
		JumpToNextSection();
		NextComboInputOn = false;
	}
}

FName UMyAnimInstance::GetNextComboSectionName()
{
	CurrentCombo = FMath::Clamp(CurrentCombo+1, 1, MaxComboCount);
	auto NextSection = FName(*FString::Printf(TEXT("Combo%d"), CurrentCombo));
	return NextSection;
}

void UMSBAnimInstance::JumpToNextSection()
{
	auto text = GetNextComboSectionName();
	Montage_JumpToSection(text, ComboMontage);
}
```

---

### Using GAS

We will now implement the equivalent code keeping in mind the following:
- Use of GAS
- Separate and manage Montage Section data as assets (enables rapid development without needing to recompile code even if the total number of attacks, playback speed, etc., change)
- Use of Timer instead of AnimNotify

Primary Data Asset class used:

![data_asset](img/post/gas/data_asset.png)

```c++
void UABGA_Attack::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
    const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
    Super::ActivateAbility(Handle, ActorInfo, ActivationInfo, TriggerEventData);

    auto Character = CastChecked<AABCharacterBase>(ActorInfo->AvatarActor.Get());
    Character->GetCharacterMovement()->SetMovementMode(EMovementMode::MOVE_None);
    CurrentComboData = Character->GetComboActionData(); // Retrieved ABA_ComboAttack defined earlier
    
    UAbilityTask_PlayMontageAndWait* PlayerAttackTask = UAbilityTask_PlayMontageAndWait::CreatePlayMontageAndWaitProxy(
       this,
       FName("PlayAttack"),
       Character->GetComboActionMontage(),
       1.0f,
       GetNextSection()
    );
    PlayerAttackTask->OnCompleted.AddDynamic(this, &ThisClass::OnActionComplete);
    PlayerAttackTask->OnCompleted.AddDynamic(this, &ThisClass::OnActionInterrupted);
    PlayerAttackTask->ReadyForActivation();

    StartComboTimer();
}

void UABGA_Attack::InputPressed(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
    const FGameplayAbilityActivationInfo ActivationInfo)
{
    //Super::InputPressed(Handle, ActorInfo, ActivationInfo);

    if(!ComboTimerHandle.IsValid())
    {
       HasNextComboInputOn = false;
    }
    else
    {
       HasNextComboInputOn = true;
    }
}

FName UABGA_Attack::GetNextSection()
{
    CurrentCombo = FMath::Clamp(CurrentCombo + 1, 1, CurrentComboData->MaxComboCount);
    auto NextSection = FString::Printf(TEXT("%s%d"), *CurrentComboData->MontageSectionNamePrefix, CurrentCombo);
    return FName(NextSection);
}

void UABGA_Attack::StartComboTimer()
{
    int32 ComboIndex = CurrentCombo - 1;
    ensure(CurrentComboData->EffectiveFrameCount.IsValidIndex(ComboIndex));

    float ComboEffectiveTime = CurrentComboData->EffectiveFrameCount[ComboIndex] / CurrentComboData->FrameRate;
    if(ComboEffectiveTime > 0.0f)
    {
       GetWorld()->GetTimerManager()
          .SetTimer(ComboTimerHandle, this, &ThisClass::CheckComboInput, ComboEffectiveTime, false);
    }
}

void UABGA_Attack::CheckComboInput()
{
    ComboTimerHandle.Invalidate();
    if(HasNextComboInputOn)
    {
       MontageJumpToSection(GetNextSection()); // pre-defined from super class
       StartComboTimer();
       HasNextComboInputOn = false;
    }
}
```

## Custom Ability Task

In the previous post, we implemented jumping using the provided Jump ability, but handling the state transitions as needed was not straightforward, and directly jumping the character from the ability made it challenging to adapt to additional requirements.
Let's create a new Jump ability and task to learn how to restrict the activation of different abilities based on the character's state.

### Implementation (C++)

The custom Task implementation follows the **Custom Ability Task Creation Pattern** we mentioned earlier.
- Declare a delegate that broadcasts when the Task has completed
- Declare a callback function to be bound to this delegate in the Ability
- Use the ReadyForActivation method to make the Task executable
- End the Ability in the method called by the delegate

In this case, the Jump Task ends when the character lands, meaning when the character's feet touch the ground.
```c++
// Task Implementation
void UABAT_JumpAndWaitForLanding::Activate()
{
    Super::Activate();

    ACharacter* Character = CastChecked<ACharacter>(GetAvatarActor());
    Character->LandedDelegate.AddDynamic(this, &ThisClass::OnLanded);
    Character->Jump();
    SetWaitingOnAvatar();
}

void UABAT_JumpAndWaitForLanding::OnDestroy(bool bInOwnerFinished)
{
    ACharacter* Character = CastChecked<ACharacter>(GetAvatarActor());
    Character->LandedDelegate.RemoveDynamic(this, &ThisClass::OnLanded);
    
    Super::OnDestroy(bInOwnerFinished);
}

void UABAT_JumpAndWaitForLanding::OnLanded(const FHitResult& Hit)
{
    if(ShouldBroadcastAbilityTaskDelegates())
    {
       OnComplete.Broadcast();
    }
}

// Ability Implementation
UABGA_Jump::UABGA_Jump()
{
    InstancingPolicy = EGameplayAbilityInstancingPolicy::InstancedPerActor;
}

void UABGA_Jump::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
    const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
    Super::ActivateAbility(Handle, ActorInfo, ActivationInfo, TriggerEventData);

    // Implement jump using custom ability task
    auto JumpAndWaitForLandingTask = UAbilityTask::NewAbilityTask<UABAT_JumpAndWaitForLanding>(this);
    JumpAndWaitForLandingTask->OnComplete.AddDynamic(this, &ThisClass::OnLanded);
    // JumpAndWaitForLandingTask->ReadyForActivation();
}

void UABGA_Jump::InputReleased(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
    const FGameplayAbilityActivationInfo ActivationInfo)
{
    auto Character = CastChecked<ACharacter>(ActorInfo->AvatarActor.Get());
    Character->StopJumping();
    
    Super::InputReleased(Handle, ActorInfo, ActivationInfo);
}

bool UABGA_Jump::CanActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
    const FGameplayTagContainer* SourceTags, const FGameplayTagContainer* TargetTags,
    FGameplayTagContainer* OptionalRelevantTags) const
{
    bool bResult = Super::CanActivateAbility(Handle, ActorInfo, SourceTags, TargetTags, OptionalRelevantTags);
    if(!bResult) return false;

    const auto Character = CastChecked<ACharacter>(ActorInfo->AvatarActor.Get());
    return (Character && Character->CanJump());
}

void UABGA_Jump::OnLanded()
{
    EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, false);
}
```

To make tags on whether to block activation for jumping or attacking, these were specified in blueprints.
For jumping, it isn't allowed to attack, and for attacking, it isn't allowed to jump. This was achieved by setting the `Activation Blocked Tags`.

![jump_tags](img/post/gas/jump_tags.png) ![attack_tags](img/post/gas/attack_tags.png)

### Using custom task in Blueprints
The method `UAbilityTask::NewAbilityTask` cannot be called from blueprints. While modifying engine code is an option, here, we will create a separate static method for task creation and declare the OnComplete delegate as `BlueprintAssignable` to let blueprints know when the task has completed.

```c++
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FJumpAndWaitForLandingDelegate);
/**
 * 
 */
UCLASS()
class ARENABATTLEGAS_API UABAT_JumpAndWaitForLanding : public UAbilityTask
{
    GENERATED_BODY()

public:
    UABAT_JumpAndWaitForLanding();

    UFUNCTION(BlueprintCallable, Category="Abiltiy|Task", meta=(
       DisplayName = "JumpAndWaitForLanding", HidePin = "OwningAbility", DefaultToSelf = "OwningAbility", BlueprintInternalUseOnly=true))
    static UABAT_JumpAndWaitForLanding* CreateTask(UGameplayAbility* OwningAbility);

    virtual void Activate() override;
    virtual void OnDestroy(bool bInOwnerFinished) override;

    UPROPERTY(BlueprintAssignable)
    FJumpAndWaitForLandingDelegate OnComplete;

protected:
    UFUNCTION()
    void OnLanded(const FHitResult& Hit);
};

UABAT_JumpAndWaitForLanding* UABAT_JumpAndWaitForLanding::CreateTask(UGameplayAbility* OwningAbility)
{
    UABAT_JumpAndWaitForLanding* NewTask = NewAbilityTask<UABAT_JumpAndWaitForLanding>(OwningAbility);
    return NewTask;
}
```

After modifying the task code as above, the part in `UABGA_Jump::ActivateAbility` where the task was created and `ReadyForActivation` was called should be commented out.
Then, in the blueprint of the Jump ability, bind the delegates.

![bp_task](img/post/gas/bp_task.png)