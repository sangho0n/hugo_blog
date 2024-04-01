---
title: "Unreal GAS Continuous Attack Implementation"
date: 2024-04-01T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[Based on the lecture by Lee Duk-woo](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4) 
and [documentation compiled by other developers](https://github.com/tranek/GASDocumentation).

For detailed and accurate information, please refer to the links above.

Series:
- [Unreal GAS Overview](../unreal-gas-overview/)
- [Unreal GAS Start](../unreal-gas-start/)
- [Unreal GAS Input Handling](../unreal-gas-input-handling/)
- [Unreal GAS Continuous Attack Implementation](../unreal-gas-continuous-attack/) <- Current Post

---------------

In this post, we'll explore how the sections registered in the animation montage can be played in GAS and implemented. 
Additionally, we'll create a custom Task and examine how to use Ability Task in blueprints.

## Continuous Attack Implementation

In the previous post, we represented the attack movement by playing the first section of the animation montage using UAbilityTask_PlayMontageAndWait.
The Gameplay Ability class in GAS already defines a method that allows you to change the animation to be played by the section's name as follows:

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

--------
### Naive Approach

The most basic mechanism for implementing continuous attacks is as follows:
- Register the animation montage to the animation instance
- Set AnimNotify (NextComboCheck) to check if it can move to the next section at the end of each montage section
- If an attack request is received while the attack has not ended, set the flag for transitioning to the next section to true
- Check the flag in AnimNotify and move to the next section using the Montage_JumpToSection method as per conditions

```c++
// Called by the attack input
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

// Play the continuous attack animation montage
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

------------

### Using GAS

When implementing the same role in code, consider the following:
- Utilize GAS
- Separate Montage Section data into separate assets for easier management (allows for quick development without recompiling even if the number of continuous attacks, playback speed, etc., changes)
- Use Timer instead of AnimNotify

Primary Data Asset class used:

![data_asset](img/post/gas/data_asset.png)

```c++
void UABGA_Attack::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
    const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
    Super::ActivateAbility(Handle, ActorInfo, ActivationInfo, TriggerEventData);

    auto Character = CastChecked<AABCharacterBase>(ActorInfo->AvatarActor.Get());
    Character->GetCharacterMovement()->SetMovementMode(EMovementMode::MOVE_None);
    CurrentComboData = Character->GetComboActionData(); // Obtain the ABA_ComboAttack defined above
    
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

In the previous post, we implemented jumping using the provided Jump ability. 
It was difficult to track the state as desired, and directly forcing the character to jump without a task made it challenging to address additional requirements.
Let's create a new Jump ability and task, and learn how to restrict the activation of different abilities based on states.

### Implementation (cpp)

Following the **custom ability creation pattern** mentioned earlier, we shall create the Task:
><p>1. Declare a delegate that is broadcasted when the task is complete in the Ability Task<br>2. Declare a callback function to be bound to the delegate and bind it in the Ability<br>3. Use the ReadyForActivation method to enable the task to be executed after binding<br>4. End the ability in the method called by the delegate</p>

In this case, the completion of the jump task is set to the landing of the jump animation, i.e., when the character's feet touch the ground.

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

    // Implement jump using the custom ability task
    auto JumpAndWaitForLandingTask = UAbilityTask::NewAbilityTask<UABAT_JumpAndWaitForLanding>(this);
    JumpAndWaitForLandingTask->OnComplete.AddDynamic(this, &ThisClass::OnLanded);
    JumpAndWaitForLandingTask->ReadyForActivation();
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

We also assigned tags in blueprints. Jumping is disabled during an attack, and attacking is disabled during a jump to achieve this, we specified the `Activation Blocked Tags`.

<center>

![jump_tags](img/post/gas/jump_tags.png) ![attack_tags](img/post/gas/attack_tags.png)

</center>

### Using custom task in Blueprints

```UAbilityTask::NewAbilityTask``` method cannot be called from Blueprints. While modifying the engine code is an option, here we will create a separate static method for task creation and declare the method as `BlueprintCallable`.
Additionally, we'll declare the OnComplete delegate as `BlueprintAssignable` to indicate the task completion in Blueprints.

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

    UFUNCTION(BlueprintCallable, Category="Ability|Task", meta=(
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

After modifying the task code as above, comment out the part in `UABGA_Jump::ActivateAbility` method that creates the task with ReadyForActivation.
Next, bind it in the Jump ability blueprint as shown below.

<center>

![bp_task](img/post/gas/bp_task.png)

</center>

~~Oddly, the task works fine in Blueprints even without calling ReadyForActivation! It seems like the engine internally activates the task once it is created.~~