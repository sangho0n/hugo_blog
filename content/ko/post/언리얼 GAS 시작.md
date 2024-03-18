---
title: "언리얼 GAS 시작"
date: 2024-03-18T15:58:25+09:00

tags: ["Unreal", "언리얼", "UE", "GAS", "어빌리티"]
categories: ["Unreal"]
series: ["게임플레이 어빌리티 시스템(GAS)"]
---

[이득우 님의 강의](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4)
와 [다른 개발자가 정리해놓은 문서](https://github.com/tranek/GASDocumentation)를 보고 정리한 내용입니다.

자세하고 정확한 내용은 위 링크를 참조하세요

시리즈
- [언리얼 GAS 개요](/p/언리얼-gas-개요/)
- [언리얼 GAS 시작](/p/언리얼-gas-시작/) <- 현재포스트

---------------

이번 포스트에서는 아래 3가지의 방법을 통해 액터의 움직임을 구현해보면서 GAS 프레임워크의 사용 방식에 대해 알아보고,
각 방식에 따른 차이점을 살펴보겠다.

- 액터 기능 확장
- Game Ability System 사용
- Game Ability System + Gameplay Tag 사용

액터로는 분수대, 움직임은 3초간 제자리 회전/정지를 기준으로 제작하였다.

## 액터 기능 확장
GAS 프레임워크 없이 URotatingMovementComponent을 직접 사용하여 구현
```c++
UCLASS()
class ARENABATTLEGAS_API AABGASFountain : public AABFountain
{
	GENERATED_BODY()

public:
	AABGASFountain();

protected:
	virtual void PostInitializeComponents() override;
	virtual void BeginPlay() override;

	virtual void TimerAction();

protected:
	UPROPERTY(VisibleAnywhere, Category=Movement)
	TObjectPtr<URotatingMovementComponent> RotatingMovement;

	UPROPERTY(EditAnywhere, Category=Timer)
	float ActionInterval;

	FTimerHandle ActionTimer;
};

void AABGASFountain::BeginPlay()
{
	Super::BeginPlay();

	GetWorld()->GetTimerManager().SetTimer(ActionTimer, this, &AABGASFountain::TimerAction, ActionInterval, true, 0.0f);
}

void AABGASFountain::TimerAction()
{
	if(!RotatingMovement->IsActive())
	{
		RotatingMovement->Activate();
	}
	else
	{
		RotatingMovement->Deactivate();
	}
}

```

## Game Ability System 사용
GAS 프레임워크를 이용하여 움직임을 구현하기 위해서는, 아래 두 개념을 먼저 이해해야 한다.
- Ability System Component 
- Game Ability
### Ability System Component
- 게임플레이 어빌리티 시스템을 관리하는 컴포넌트
- 액터 당 하나만 부착 가능
- 액터는 이를 통하여 Gameplay Ability를 발동시킬 수 있음
- 해당 컴포넌트를 부착한 액터 사이에 Game Ability System에 의한 상호작용이 가능해짐

### Game Ability
- Ability System Component에 등록되어 발동시킬 수 있는 액션
- 발동 과정
  - Ability System Component에 등록 : AbilitySystemComponent->GiveAbility()
  - 액션 발동 : AbilitySystemComponent->TryActivateAbility()
  - 발동된 ability 내부에서는 SpecHandle, ActorInfo, ActivationInfo를 활용하여 요구사항 구현
- 주요 메서드
  - CanActivateAbility
  - **ActivateAbility**
  - **CancelAbility**
  - EndAbility

위 두 개념을 이용하여 맨 처음과 동일한 움직임을 구현하면 아래와 같다.

1. GameplayAbility를 상속하여 어빌리티 클래스 생성
```c++
UCLASS()
class ARENABATTLEGAS_API UABGA_Rotate : public UGameplayAbility
{
	GENERATED_BODY()

	virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData) override;
	virtual void CancelAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateCancelAbility) override;
	
};
void UABGA_Rotate::ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
                                   const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData)
{
	Super::ActivateAbility(Handle, ActorInfo, ActivationInfo, TriggerEventData);

	if(auto Avatar = ActorInfo->AvatarActor.Get())
	{
		if(auto RotatingMovement = Avatar->GetComponentByClass(URotatingMovementComponent::StaticClass()))
		{
			RotatingMovement->Activate();
		}
	}
}

void UABGA_Rotate::CancelAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo,
	const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateCancelAbility)
{
	Super::CancelAbility(Handle, ActorInfo, ActivationInfo, bReplicateCancelAbility);
    // 생략
}
```
2. 액터에 컴포넌트 부착 및 인터페이스 구현
```c++
UCLASS()
class ARENABATTLEGAS_API AABGASFountain : public AABFountain, public IAbilitySystemInterface
{
	GENERATED_BODY()
public:
	AABGASFountain();

	virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override; // pure virtual
	//...
	UPROPERTY(VisibleAnywhere, Category=Ability)
	TObjectPtr<UAbilitySystemComponent> AbilitySystemComponent;
	UPROPERTY(VisibleAnywhere, Category=Ability)
	TObjectPtr<URotatingMovementComponent> RotatingMovement;

	UPROPERTY(EditAnywhere, Category=Timer)
	float ActionInterval;

	FTimerHandle ActionTimer;
};

UAbilitySystemComponent* AABGASFountain::GetAbilitySystemComponent() const
{
	return AbilitySystemComponent;
}
```
3. 부착된 컴포넌트에 어빌리티 등록 및 발동
```c++

void AABGASFountain::PostInitializeComponents()
{
	Super::PostInitializeComponents();
	
	AbilitySystemComponent->InitAbilityActorInfo(this, this);
	FGameplayAbilitySpec RotateSpec(UABGA_Rotate::StaticClass());
	AbilitySystemComponent->GiveAbility(RotateSpec);
}

void AABGASFountain::TimerAction()
{
	if(auto RotateSpec = AbilitySystemComponent->FindAbilitySpecFromClass(UABGA_Rotate::StaticClass()))
	{
		if(!RotateSpec->IsActive())
		{
			AbilitySystemComponent->TryActivateAbility(RotateSpec->Handle);
		}
		else
		{
			AbilitySystemComponent->CancelAbilityHandle(RotateSpec->Handle);
		}
	}
}
```

## Game Ability System + Gameplay Tag 사용

게임플레이 태그 없이 Game Ability System만을 사용하여 구현하는 경우, GAS 프레임워크의 장점을 최대로 활용할 수 없다. 
Gameplay Tag가 무엇인지 먼저 알아보자

### Gameplay Tags

FGameplayTag란 ```Parent.Child.Grandchild...```와 같이 계층적 형태로 등록/관리되는 이름을 의미한다. GameplayTagManager에 의해 등록된다.
이러한 태그들을 이용하여 클래스들을 분류하고, 상태를 효과적으로 추적할 수 있다.

상태 추적을 위해 bool값이나 enum을 두고 해당 값을 기준으로 조건문을 통해 상태를 확인하던 방식들은,
해당 오브젝트가 Gameplay Tag를 가지고있는지 여부로 대체할 수 있다.

한편 여러개의 Tag들은 Tarray<FGameplayTag>보다는 FGameplayTagContainer를 이용하여 관리하는 것이 좋다. 언제든 배열 형태로
태그들을 받아볼 수 있을 뿐만 아니라, 여러 메서드를 통해 태그 관리를 쉽게 할 수 있기 때문이다.

GAS 프레임워크는 Gameplay Tag와 매우 친화적이다. UAbilitySystemComponent가 IGameplayTagAssetInterface를 구현하기 때문에 Ability System Component에 직접 태그를 지정할 수 있을 뿐만 아니라,
아래와 같이 GameplayAbility의 여러 상태들을 태그 컨테이너로 관리할 수 있도록 구현해두었기 때문이다.
```c++
// GameplayAbility.h
    /** Abilities with these tags are cancelled when this ability is executed */
    UPROPERTY(EditDefaultsOnly, Category = Tags, meta=(Categories="AbilityTagCategory"))
    FGameplayTagContainer CancelAbilitiesWithTag;
    
    /** Abilities with these tags are blocked while this ability is active */
    UPROPERTY(EditDefaultsOnly, Category = Tags, meta=(Categories="AbilityTagCategory"))
    FGameplayTagContainer BlockAbilitiesWithTag;
    
    /** Tags to apply to activating owner while this ability is active. These are replicated if ReplicateActivationOwnedTags is enabled in AbilitySystemGlobals. */
    UPROPERTY(EditDefaultsOnly, Category = Tags, meta=(Categories="OwnedTagsCategory"))
    FGameplayTagContainer ActivationOwnedTags;
```

또한 게임플레이 태그를 활용하면, 액터 클래스에서 Gameplay Ability 클래스에 대한 정보가 없어도 동일한 요구사항을 구현할 수 있기 때문에
코드 간 낮은 의존성을 유지시킬 수 있다는 장점이 있다.

게임플레이 태그를 활용하면 동일한 요구 사항을 아래와 같이 구현할 수 있다.

1. 태그 생성
```shell
// DefaultGameplayTags.ini
[/Script/GameplayTags.GameplayTagsSettings]
//...
+GameplayTagList=(Tag="Actor.Action.Rotate",DevComment="")
+GameplayTagList=(Tag="Actor.State.IsRotating",DevComment="")
```
2. 태그를 쉽게 얻어오기 위한 매크로 작성
```c++
// ABGameplayTag.h
#define ABTAG_ACTOR_ROTATE FGameplayTag::RequestGameplayTag(FName("Actor.Action.Rotate"))
#define ABTAG_ACTOR_ISROTATING FGameplayTag::RequestGameplayTag(FName("Actor.State.IsRotating"))
```
3. Gameplay Ability에 태그 등록
```c++
UABGA_Rotate::UABGA_Rotate()
{
	AbilityTags.AddTag(ABTAG_ACTOR_ROTATE);
	// 활성화될 때 아래 태그가 심어짐
	ActivationOwnedTags.AddTag(ABTAG_ACTOR_ISROTATING);
}
```
4. 태그를 활용한 어빌리티 등록 및 활성화
```c++
// ABGASFountain.h
	UPROPERTY(EditAnywhere, Category=GAS)
	TArray<TSubclassOf<UGameplayAbility>> Abilities;

// 구현부
void AABGASFountain::PostInitializeComponents()
{
	Super::PostInitializeComponents();
	
	AbilitySystemComponent->InitAbilityActorInfo(this, this);
	for (auto Element : Abilities)
	{
		FGameplayAbilitySpec Spec(Element);
		AbilitySystemComponent->GiveAbility(Spec);
	}
}

void AABGASFountain::TimerAction()
{
	FGameplayTagContainer TargetTag(ABTAG_ACTOR_ROTATE);

	if(!AbilitySystemComponent->HasMatchingGameplayTag(ABTAG_ACTOR_ISROTATING))
	{
		AbilitySystemComponent->TryActivateAbilitiesByTag(TargetTag);
	}
	else
	{
		AbilitySystemComponent->CancelAbilities(&TargetTag);
	}
}
```
이후 AABGASFountain cpp 클래스를 상속하는 블루프린트 클래스를 만든 후, Details 패널에서 알맞은 액티비티를 Abilities에 넣어주면 된다.

## 정리
회전하는 분수대를 세 가지의 방법으로 구현
   1. 액터의 기능 확장
   2. GAS : 새로운 클래스(ability)를 만들어 액터로부터 기능 분리
   3. GAS + Gameplay Tags : 태그를 활용해 액터와 ability 간 의존성 제거

GAS와 Gameplay Tags를 같이 사용했을 때의 좋은 점
1. 액터의 역할 최소화
2. 의존성 제거. 유지보수가 쉬워지고, 재사용성이 높아짐
3. 확장성 + 타직군 과의 협업 용이


![RotatingFountain.gif](img/post/gas/RotatingFountain.gif)

