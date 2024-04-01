---
title: "언리얼 GAS 연속 공격 구현"
date: 2024-04-01T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "어빌리티"]
categories: ["Unreal"]
series: ["게임플레이 어빌리티 시스템(GAS)"]
---

 
[이득우 님의 강의](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4)
와 [다른 개발자가 정리해놓은 문서](https://github.com/tranek/GASDocumentation)를 보고 정리한 내용입니다.

자세하고 정확한 내용은 위 링크를 참조하세요

시리즈
- [언리얼 GAS 개요](../언리얼-gas-개요/)
- [언리얼 GAS 시작](../언리얼-gas-시작/)
- [언리얼 GAS 입력처리](../언리얼-gas-입력처리/)
- [언리얼 GAS 연속 공격 구현](../언리얼-gas-연속공격/) <- 현재포스트

---------------
 
이번 포스트에서는 애니메이션 몽타주에 등록되어있는 섹션을 GAS에서는 어떻게 재생시킬 수 있는지 알아보겠다. 
더불어 custom Task를 만들어보고, Ability Task를 블루프린트에서 사용하는 방식에 대해 알아보겠다.

## 연속공격 구현

이전 포스트에서는 UAbilityTask_PlayMontageAndWait를 이용해 애님몽타주의 첫 섹션을 재생시키는 것으로 공격 움직임을 나타냈었다.
GAS의 Gameplay Ability 클래스에는 다음과 같이 섹션의 이름으로 플레이될 애니메이션을 바꿀 수 있는 메서드가 이미 정의되어 있다.

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
위 메서드를 활용하여 연속 공격을 구현해보자.

--------
### Naive

연속공격을 구현할 때 가장 기본적인 메커니즘은 아래와 같다.
- 애님인스턴스에 애님몽타주 등록
- 애님몽타주 섹션의 끝마다 다음 section으로 넘어갈 수 있는지 확인하는 AnimNotify(NextComboCheck) 설정
- 공격이 끝나지 않았는데 공격 요청이 들어왔을 경우 다음 섹션으로 넘어가는 flag를 true로 설정
- AnimNotify에서 flag 확인 후 조건에 따라 Montage_JumpToSection 메서드를 이용해 섹션 이동
```c++
// 공격 input에 의해 아래 함수 호출
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

// 연속공격 애니메이션 몽타주 재생
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

### GAS 이용

같은 역할을 하는 코드를 다음과 같은 점을 염두에 두고 구현해보겠다.
- GAS 이용
- Montage Section 데이터들을 별도 에셋으로 분리하여 관리(전체 연속 공격 수, 재생 속도 등이 바뀌더라도 코드 컴파일 없이 빠른 개발 가능)
- 애님노티파이 대신 Timer를 이용

사용된 Primary Data Asset 클래스

![data_asset](img/post/gas/data_asset.png)

```c++
void UABGA_Attack::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
    const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
    Super::ActivateAbility(Handle, ActorInfo, ActivationInfo, TriggerEventData);

    auto Character = CastChecked<AABCharacterBase>(ActorInfo->AvatarActor.Get());
    Character->GetCharacterMovement()->SetMovementMode(EMovementMode::MOVE_None);
    CurrentComboData = Character->GetComboActionData(); // 위에서 정의한 ABA_ComboAttack을 가져옴
    
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

지난 포스트에서는 기본으로 제공되던 Jump 어빌리티를 이용해 점프를 구현했었다. 
이 경우 상태추적이 원하는대로 쉽게 되지 않고, 태스크 없이 어빌리티에서 직접 캐릭터를 점프시켜버리기 때문에 추가 요구사항에 유연하게 대처하기 힘들다.
새로 점프 어빌리티와 태스크를 만들고 상태에 따라 다른 어빌리티의 발동을 제한하는 법을 알아보자.

### 구현(cpp)
이전에 언급했었던 **커스텀 어빌리티 생성 패턴**에 맞춰 제작하겠다.
><p>1. 어빌리티 태스크에 작업이 완료된 후 브로드캐스팅되는 델리게이트 선언<br>2. 어빌리티에서 위 델리게이트에 바인딩 될 콜백 함수 선언 및 바인딩<br>3. 바인딩 후 ReadyForActivation 메서드를 이용해 태스크가 실행될 수 있는 상태 만들기<br>4. 델리게이트에 의해 호출된 메서드에서 EndAbility를 통해 어빌리티 종료</p>

이때, 점프 태스크의 종료는 점프 애니메이션의 종료, 즉 땅에 발을 디뎠을 때 종료되는 것으로 설정하였다.
```c++
// Task 구현부
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

// Ability 구현부
UABGA_Jump::UABGA_Jump()
{
    InstancingPolicy = EGameplayAbilityInstancingPolicy::InstancedPerActor;
}

void UABGA_Jump::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
    const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
    Super::ActivateAbility(Handle, ActorInfo, ActivationInfo, TriggerEventData);

    // custom ability task를 이용해 jump 구현
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

마찬가지로 태그 지정은 블루프린트에서 이루어졌다. 이때 점프 중에는 공격이 불가능, 
공격 중에는 점프가 불가능하도록 구현하였는데, 이를 위해서는 ```Activation Blocked Tags```를 지정해주면 된다.

<center>

![jump_tags](img/post/gas/jump_tags.png) ![attack_tags](img/post/gas/attack_tags.png)

</center>

### 블루프린트에서 custom task 사용하기

```UAbilityTask::NewAbilityTask``` 메서드는 블루프린트에서 호출할 수 없다. 엔진 코드를 수정해도 되지만, 여기서는 태스크 생성을 위한
별도의 static 메서드를 만든 후, 해당 메서드를 ```BlueprintCallable```로 선언하겠다.
또한 OnComplete 델리게이트를 ```BlueprintAssignable```로 선언하여 블루프린트에서도 태스크가 끝났다는 사실을 알 수 있도록 하겠다.

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

태스크 코드를 위처럼 변경한 후, ```UABGA_Jump::ActivateAbility``` 메서드에서 태스크를 생성하여 ReadyForActivation을 호출하던 부분을 주석처리한다.
이후 Jump 어빌리티 블루프린트에서 다음과 같이 바인딩한다.

<center>

![bp_task](img/post/gas/bp_task.png)

</center>

~~이상하게 블루프린트에서는 ReadyForActivation을 호출하지 않아도 태스크가 정상적으로 동작한다! 아마도 엔진 내부에서 생성만 해도 활성화가 되도록 구현이 된 것 같다.~~
