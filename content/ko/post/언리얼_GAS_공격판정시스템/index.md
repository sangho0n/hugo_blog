---
title: "언리얼 GAS 공격 판정 시스템 구현"
date: 2024-04-03T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "어빌리티"]
categories: ["Unreal"]
series: ["게임플레이 어빌리티 시스템(GAS)"]
---


[이득우 님의 강의](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4)
와 [다른 개발자가 정리해놓은 문서](https://github.com/tranek/GASDocumentation)를 보고 정리한 내용입니다.

자세하고 정확한 내용은 위 링크를 참조하세요

## 시리즈
### GAS 기초
- [언리얼 GAS 개요](../언리얼-gas-개요/)
- [언리얼 GAS 시작](../언리얼-gas-시작/)
### GAS 캐릭터 제작 기초
- [언리얼 GAS 입력처리](../언리얼-gas-입력처리/)
- [언리얼 GAS 연속 공격 구현](../언리얼-gas-연속-공격-구현/)
- [언리얼 GAS 공격 판정 시스템 구현](../언리얼-gas-공격-판정-시스템-구현/)<- 현재포스트
### 어트리뷰트와 게임플레이 이펙트
- 언리얼 GAS 캐릭터 어트리뷰트
- 언리얼 GAS 게임플레이 이펙트
- 언리얼 GAS 어트리뷰트와 UI 연동
### GAS의 활용
- 언리얼 GAS 아이템 상자 구현
- 언리얼 GAS 광역 스킬 구현

---------------

이번 포스트에서는 GAS의 Gameplay Event와 TargetActor를 이용하여,
공격 판정 시점을 GAS에 전달해보고, 공격 판정을 구현해보겠다.

## Gameplay Event

GAS에서는 특정 이벤트에 대해 GameplayTag를 지정하여, 해당 이벤트가 발했음을 GAS에게 알릴 수 있는 기능이 있다. 이를 GameplayEvent라고 한다.
아래 표는 GameplayEvent를 사용하여 GAS에서 어떠한 것을 할 수 있을지 나타낸 것이다.

|                            메서드                             | 설명                                                                                                                                         |
|:----------------------------------------------------------:|--------------------------------------------------------------------------------------------------------------------------------------------|
|  UAbilitySystemBlueprintLibrary::SendGameplayEventToActor  | 특정 이벤트가 발생했을 때, 이를 액터에게 알리고 이를 사용하여 GameplayAbility를 활성화시킬 수 있다.                                                                           |
|     UAbilityTask_WaitGameplayEvent::WaitGameplayEvent      | 특정 이벤트가 발생할 때까지 Task를 기다리게한다. 해당 이벤트에 대한 다양한 정보를 기다리고 있는 어빌리티에 전달할 수 있다. |

이 중 SendGameplayEventToActor 메서드를 이용하여 공격 판정을 위한 어빌리티를 활성화하는 방법에 대해 알아보겠다.
아래와 같은 순서로 이를 구현할 것이다.
- [게임플레이 이벤트를 위한 게임플레이 태그 생성](#이벤트-태그-생성)
- [Custom 애님 노티파이 생성 및 애니메이션에 노티파이 지정](#노티파이-생성-및-이벤트-전달)
- [새로운 게임플레이 어빌리티 생성 및 Trigger 이벤트 태그 지정](#어빌리티-생성-및-trigger)

### 이벤트 태그 생성
```Character.Action.PunchKick```으로 이벤트를 위한 게임플레이 태그 생성

![img.png](img/post/gas/punch_kick_event_tag.png)
### 노티파이 생성 및 이벤트 전달

```c++
class ARENABATTLEGAS_API UAnimNotify_OnPunchKick : public UAnimNotify
{
	GENERATED_BODY()
public:
	UAnimNotify_OnPunchKick();

protected:
	virtual FString GetNotifyName_Implementation() const override;
	virtual void Notify(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation, const FAnimNotifyEventReference& EventReference) override;

	UPROPERTY(EditAnywhere)
	FGameplayTag TriggerGameplayTag;
};

FString UAnimNotify_OnPunchKick::GetNotifyName_Implementation() const
{
	return TEXT("OnGASAttackHit");
}

void UAnimNotify_OnPunchKick::Notify(USkeletalMeshComponent* MeshComp, UAnimSequenceBase* Animation,
	const FAnimNotifyEventReference& EventReference)
{
	Super::Notify(MeshComp, Animation, EventReference);

	if(MeshComp)
	{
		AActor* Owner = MeshComp->GetOwner();
		if(Owner)
		{
			FGameplayEventData EmptyPayload;
			UAbilitySystemBlueprintLibrary::SendGameplayEventToActor(Owner, TriggerGameplayTag, EmptyPayload);
		}
	}
}
```
위와 같이 SendGameplayEventToActor 메서드를 이용하여 애니메이션이 재생중인 액터에 이벤트를 전달한다.

이후 아래와 같이 애니메이션 에셋에서 애님노티파이를 지정 후, 애님노티파이 세부 창에서 이벤트 태그를 지정한다.

![img.png](img/post/gas/event_notify.png)

### 어빌리티 생성 및 Trigger
```c++
UABGameplayAbility_HitPunchKick::UABGameplayAbility_HitPunchKick()
{
	InstancingPolicy = EGameplayAbilityInstancingPolicy::InstancedPerActor;
}

void UABGameplayAbility_HitPunchKick::ActivateAbility(const FGameplayAbilitySpecHandle Handle,
	const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilityActivationInfo ActivationInfo,
	const FGameplayEventData* TriggerEventData)
{
	Super::ActivateAbility(Handle, ActorInfo, ActivationInfo, TriggerEventData);

	UE_LOG(LogABGAS, Log, TEXT("PunchKick notify triggered ability!"));
}

```

위와 같이 어빌리티를 생성한 후, 이를 상속하는 블루프린트 클래스를 만들어 Trigger Tag를 지정해준다.

![img.png](img/post/gas/trigger_tag.png)

이제 게임을 실행시켜 공격을 해보면, 로그가 찍히는 것을 확인할 수 있다.

## Target Actor

```TargetActor```란 Ability의 대상을 지정하는 것을 도와주는 역할을 하는 액터를 말한다.
타겟액터는 일반적으로 Ability Task에 의해 스폰되며, ```TargetData```를 만들어 Ability Task로 전달하는 역할을 한다.
또한 내부에 ```TSubclassOf<AGameplayAbilityWorldReticle> ReticleClass``` 멤버 변수를 가지고 있기 때문에, 
타겟의 위치를 화면에 시각화하거나 탄흔을 나타내는데에 쉽게 이용할 수 있다.

> **주의!** <br>
> 타겟액터는 기본적으로 어빌리티가 활성화될 때마다 스폰되기 때문에 그리 효율적이지는 않다.
> 따라서 최적화를 위해서라면 ```AGameplayAbilityTargetActor``` 클래스의 하위클래스를 만들어 액터를 수정하거나, 
> 비슷한 역할을 하는 다른 액터(혹은 블루프린트)를 만들어 spawn cost를 피하는 것이 좋다.
> 다만 멀티플레이 게임에서의 Target 레플리케이션이 어떻게 구현될 수 있을지 파악하기에는 매우 좋은 클래스이다.

이번 섹션에서는 위에서 구현한 PunchKick 어빌리티가 활성화되었을 때, 
플레이어 앞 일정 범위에 다른 캐릭터가 있을 경우를 감지할 수 있도록 구현해볼 것이다.
요구 조건은 아래와 같다.
- 공격중인 플레이어 전방으로 지름이 50인 구를 100만큼 trace시켜 피격 가능한 물체가 있는지 확인
- DrawDebug로 공격 판정 확인
- 범위 내 여러 액터 감지

이를 아래와 같은 구조로 구현하였다. 
다만 GameplayAbility에서 Task를 생성하고 delegate를 바인딩하는 부분은 블루프린트에서 진행하였다.
이를 위해 이전포스트와 마찬가지로 Task에서 CreateTask 메서드를 전역으로 선언해주었다.

![img.png](/img/post/gas/TargetActor_Flowchart.png)

### Task 구현

```c++

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FTraceTaskDelegate, const FGameplayAbilityTargetDataHandle&, DataHandle);
/**
 * 
 */
UCLASS()
class ARENABATTLEGAS_API UABAbilityTask_Trace : public UAbilityTask
{
	GENERATED_BODY()
public:
	UABAbilityTask_Trace();
	
	UFUNCTION(BlueprintCallable, Category="Abiltiy|Task", meta=(
		DisplayName = "TraceSphere", HidePin = "OwningAbility", DefaultToSelf = "OwningAbility", BlueprintInternalUseOnly=true))
	static UABAbilityTask_Trace* CreateTask(UGameplayAbility* OwningAbility, TSubclassOf<AGameplayAbilityTargetActor> TargetActorType);

// 중략

protected:
	void OnTargetDataReady(const FGameplayAbilityTargetDataHandle& DataHandle);

	UPROPERTY()
	TSubclassOf<AGameplayAbilityTargetActor> TargetActor;

	UPROPERTY()
	TObjectPtr<AGameplayAbilityTargetActor> SpawnedTargetActor;

public:
	UPROPERTY(BlueprintAssignable)
	FTraceTaskDelegate OnComplete;
};

```
TargetActor의 타입정보를 담는 변수 ```TargetActor```와 인스턴스를 가르키는 포인터 ```SpawnedTargetActor```를 이용하여 타겟액터를 관리한다.
이때 GC의 부담을 덜어주기 위해 OnDestroy 메서드를 오버라이딩하여 타겟액터 인스턴스를 해제하였다.
```c++

UABAbilityTask_Trace* UABAbilityTask_Trace::CreateTask(UGameplayAbility* OwningAbility, TSubclassOf<AGameplayAbilityTargetActor> TargetActorType)
{
	auto NewTask = NewAbilityTask<UABAbilityTask_Trace>(OwningAbility);
	NewTask->TargetActor = TargetActorType;
	return NewTask;
}

void UABAbilityTask_Trace::Activate()
{
	Super::Activate();

	// spawn target actor differed
	SpawnedTargetActor = Ability->GetWorld()
		->SpawnActorDeferred<AGameplayAbilityTargetActor>(TargetActor, FTransform::Identity, nullptr, nullptr,
			ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	SpawnedTargetActor->TargetDataReadyDelegate.AddUObject(this, &ThisClass::OnTargetDataReady);

	auto AbilitySystem = AbilitySystemComponent.Get();
	if(AbilitySystem)
	{
		SpawnedTargetActor->FinishSpawning(AbilitySystem->GetAvatarActor()->GetTransform());
		AbilitySystem->SpawnedTargetActors.Push(SpawnedTargetActor);
		SpawnedTargetActor->StartTargeting(Ability);
		SpawnedTargetActor->ConfirmTargeting();
	}
	
	SetWaitingOnAvatar();
}

void UABAbilityTask_Trace::OnDestroy(bool bInOwnerFinished)
{
	if(SpawnedTargetActor)
	{
		SpawnedTargetActor->Destroy();
	}
	
	Super::OnDestroy(bInOwnerFinished);
}

void UABAbilityTask_Trace::OnTargetDataReady(const FGameplayAbilityTargetDataHandle& DataHandle)
{
	if(ShouldBroadcastAbilityTaskDelegates())
	{
		OnComplete.Broadcast(DataHandle);
	}

	EndTask();
}

```

### Ability 블루프린트에서 태스크 생성 및 바인딩

Task의 OnComplete 델리게이트에 OnHit 메서드를 바인딩하였다.

![img.png](img/post/gas/TraceTaskBinding.png)

이때 다중공격으로 구현하기로 했으므로, OnHit 메서드를 아래와 같이 구현하였다.

```c++
void UABGameplayAbility_HitPunchKick::OnHit(const FGameplayAbilityTargetDataHandle& DataHandle)
{
	TArray<FHitResult> HitResults;
	ABGAS_LOG(LogABGAS, Log, TEXT("On Hit"));

	for(int i = 0; true; i++)
	{
		if(UAbilitySystemBlueprintLibrary::TargetDataHasHitResult(DataHandle, i))
		{
			HitResults.Push(UAbilitySystemBlueprintLibrary::GetHitResultFromTargetData(DataHandle, i));
			ABGAS_LOG(LogABGAS, Log, TEXT("Target %s detected!"), *HitResults[i].GetActor()->GetName());
		}
		else break;
	}
	

	EndAbility(CurrentSpecHandle, CurrentActorInfo, CurrentActivationInfo, true, false);
}
```

<details>
<summary>UAbilitySystemBlueprintLibrary::TargetDataHasHitResult 구현부</summary>
<div markdown="1">

```c++
bool UAbilitySystemBlueprintLibrary::TargetDataHasHitResult(const FGameplayAbilityTargetDataHandle& TargetData, int32 Index)
{
	if (TargetData.Data.IsValidIndex(Index))
	{
		FGameplayAbilityTargetData* Data = TargetData.Data[Index].Get();
		if (Data)
		{
			return Data->HasHitResult();
		}
	}
	return false;
}
```

</div>
</details>

### TargetActor 구현

GAS가 기본으로 제공하는 ```AGameplayAbilityTargetActor_Radius```의 구조를 차용하여 구현하였다.

```c++
UCLASS()
class ARENABATTLEGAS_API AABTargetActor_TraceWithSphere : public AGameplayAbilityTargetActor
{
	GENERATED_BODY()

public:
	AABTargetActor_TraceWithSphere();

	virtual void StartTargeting(UGameplayAbility* Ability) override;
	virtual void ConfirmTargetingAndContinue() override;

	/** Radius of detecting sphere that used for tracing. */
	float Radius;
	/** Trace length (End - Start). */
	float Range;
	
	UPROPERTY(BlueprintReadWrite, EditAnywhere, Category = Debug)
	bool bShowDebug;

protected:
	virtual TArray<TWeakObjectPtr<AActor> >	PerformTrace(const FVector& Origin);
	virtual FGameplayAbilityTargetDataHandle MakeTargetData(const TArray<TWeakObjectPtr<AActor>>& Actors, const FVector& Origin) const;
};
```

Task에서 ConfirmTargeting이 호출되면, ConfirmTargetingAndContinue가 호출스택에 싸이고
내부에서 Trace를 수행한 후 타겟 데이터를 만들어 이를 브로드캐스트시킨다.

```c++
void AABTargetActor_TraceWithSphere::StartTargeting(UGameplayAbility* Ability)
{
	Super::StartTargeting(Ability);

	SourceActor = Ability->GetCurrentActorInfo()->AvatarActor.Get();
	bShowDebug = true;

	// 추후에 지정 가능하게 변경 예정
	Radius = 50.0f;
	Range = 100.0f;
}

void AABTargetActor_TraceWithSphere::ConfirmTargetingAndContinue()
{
	if (SourceActor)
	{
		FVector Origin = StartLocation.GetTargetingTransform().GetLocation();
		FGameplayAbilityTargetDataHandle Handle = MakeTargetData(PerformTrace(Origin), Origin);
		TargetDataReadyDelegate.Broadcast(Handle);
	}
}

FGameplayAbilityTargetDataHandle AABTargetActor_TraceWithSphere::MakeTargetData(
	const TArray<TWeakObjectPtr<AActor>>& Actors, const FVector& Origin) const
{
	if (OwningAbility)
	{
		return StartLocation.MakeTargetDataHandleFromActors(Actors, true);
	}

	return FGameplayAbilityTargetDataHandle();
}

TArray<TWeakObjectPtr<AActor>> AABTargetActor_TraceWithSphere::PerformTrace(const FVector& Origin)
{
	TArray<TWeakObjectPtr<AActor>> ReturnActors;
	ACharacter* SourceCharacter = Cast<ACharacter>(SourceActor);

	FCollisionQueryParams Ignore_Self = FCollisionQueryParams(SCENE_QUERY_STAT(AABTargetActor_Trace), false, SourceCharacter);
	const FVector Forward = SourceCharacter->GetActorForwardVector();
	const FVector Start = SourceCharacter->GetActorLocation() + Forward * SourceCharacter->GetCapsuleComponent()->GetScaledCapsuleRadius();
	const FVector End = Start + Forward * Range;

	TArray<FHitResult> HitResults;
	bool bHit = GetWorld()->SweepMultiByChannel(
		HitResults,
		Start,
		End,
		FQuat::Identity,
		CCHANNEL_ABACTION,
		FCollisionShape::MakeSphere(Radius),
		Ignore_Self
	);

	for(FHitResult HitRes : HitResults)
	{
		AActor* HitActor = HitRes.GetActor();
		if(!ReturnActors.Contains(HitActor))
		{
			ReturnActors.Push(HitActor);
		}
	}

#if ENABLE_DRAW_DEBUG
	if(bShowDebug)
	{
		float CapsuleHalfHeight = Range / 2.0f;
		FVector CapsuleOrigin = (Start + End) / 2.0f;
		DrawDebugCapsule(GetWorld(),
			CapsuleOrigin,
			CapsuleHalfHeight,
			Radius,
			FRotationMatrix::MakeFromZ(Forward).ToQuat(),
			bHit ? FColor::Red : FColor::Green,
			false,
			2.0f
		);
	}
#endif

	return ReturnActors;
}

```
이제 공격 애니메이션이 재생될 때마다 특정 프레임에서 공격 판정이 이루어지게 된다.

## 최종화면
<center>

![hitcheck.gif](img/post/gas/hitcheck.gif)

</center>
