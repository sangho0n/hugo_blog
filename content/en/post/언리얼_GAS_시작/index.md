---
title: "Unreal GAS Start"
date: 2024-03-18T15:58:25+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[Based on lectures by Lee Duk-Woo](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4)
and [documentation compiled by another developer](https://github.com/tranek/GASDocumentation).

Please refer to the links above for detailed and accurate information.

Series
- [Unreal GAS Overview](/p/언리얼-gas-개요/)
- [Unreal GAS Start](/p/언리얼-gas-시작/) <- Current Post
- [Unreal GAS Input Processing](../언리얼-gas-입력처리/)
- [Unreal GAS Implementing Continuous Attacks](../언리얼-gas-연속공격/)

---

In this post, I will explore the usage of the GAS framework by implementing actor movement through three different methods, understanding how to use the GAS framework, and examining the differences between each method.

- Actor Function Extension
- Using Game Ability System
- Using Game Ability System + Gameplay Tag

For the actor, a fountain with movement based on a 3-second stationary rotation/stop was created.

## Actor Function Extension
Implemented directly using URotatingMovementComponent without the GAS framework.

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

## Using Game Ability System
To implement movement using the GAS framework, you need to understand two key concepts:
- Ability System Component
- Game Ability

### Ability System Component
- Manages the Gameplay Ability System for the game
- Only one can be attached per actor
- Allows actors to trigger Gameplay Abilities through it
- Enables interaction between actors with this component in the Game Ability System

### Game Ability
- An action that is registered with the Ability System Component to be triggered
- Activation process:
  - Register with Ability System Component: AbilitySystemComponent->GiveAbility()
  - Activate the action: AbilitySystemComponent->TryActivateAbility()
  - Inside the activated ability, utilize SpecHandle, ActorInfo, ActivationInfo to implement requirements
- Key methods:
  - CanActivateAbility
  - **ActivateAbility**
  - **CancelAbility**
  - EndAbility

Using the above concepts, the same movement can be implemented as follows.

1. Create an ability class by inheriting from GameplayAbility

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
    // Omitted
}
```

2. Attach components to the actor and implement the interface

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

3. Register and activate abilities on the attached components

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

## Using Game Ability System + Gameplay Tag

When using Gameplay Tags along with the Game Ability System, the advantages of the GAS framework are maximized.
Gameplay Tags allow for efficient categorization and tracking of states, reducing dependency between objects and enhancing reusability.

---

This post explored implementing a rotating fountain through three different methods:
1. Actor function extension
2. GAS: Creating a new class (ability) to separate functionality from the actor
3. GAS + Gameplay Tags: Using tags to remove dependencies between actors and abilities

Advantages of using GAS and Gameplay Tags together:
1. Minimize the actor's role
2. Reduce dependencies, making maintenance easier and increasing reusability
3. Easy collaboration and scalability with other classes

![RotatingFountain.gif](img/post/gas/RotatingFountain.gif)