---
title: "Unreal GAS Start"
date: 2024-03-18T15:58:25+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---


[Based on lectures by Lee Geun-woo](https://www.inflearn.com/course/lee-geunwoo-unreal-programming-part-4) 
and [documents compiled by other developers](https://github.com/tranek/GASDocumentation).

For detailed and accurate information, please refer to the links above.

Series
- [Unreal GAS Overview](/p/unreal-gas-overview/)
- [Unreal GAS Start](/p/unreal-gas-start/) <- Current Post
- [Unreal GAS Input Handling](../unreal-gas-input-handling/)

---------------

In this post, we will explore the implementation of actor movement through three methods to understand the usage of the GAS framework,
and examine the differences between each method.

- Actor Function Extension
- Using the Game Ability System
- Using Game Ability System with Gameplay Tags

For the actor, a fountain is used, and the movement is designed based on a 3-second stationary rotation/stop as a reference.

## Actor Function Extension
Implementing movement using URotatingMovementComponent directly without the GAS framework.
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

## Using the Game Ability System
To implement movement using the GAS framework, you need to understand the following two concepts first:
- Ability System Component
- Game Ability
### Ability System Component
- A component that manages the Gameplay Ability System
- Only one can be attached per actor
- Actors can invoke Gameplay Abilities through this component
- Enables interaction between actors with this component through the Game Ability System

### Game Ability
- An action registered in the Ability System Component that can be activated
- Activation Process
  - Registered in Ability System Component: AbilitySystemComponent->GiveAbility()
  - Activating the ability: AbilitySystemComponent->TryActivateAbility()
  - Within the activated ability, requirements are implemented using SpecHandle, ActorInfo, ActivationInfo
- Key Methods
  - CanActivateAbility
  - **ActivateAbility**
  - **CancelAbility**
  - EndAbility

Implementing the same movement as before using the two above concepts:
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
    // omitted
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
3. Register and activate the ability on the attached component
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

## Using Game Ability System + Gameplay Tags

When using the Game Ability System without Gameplay Tags, the advantages of the GAS framework are not fully utilized.
Let's first understand what Gameplay Tags are.

### Gameplay Tags

FGameplayTag represents a name registered in a hierarchical form like ```Parent.Child.Grandchild...```. These tags are registered by the GameplayTagManager.
By using these tags, classes can be classified and states can be effectively tracked.

Instead of using bool values or enums to track states, the presence of Gameplay Tags in an object can replace conditions based on values to determine the state.

Furthermore, managing multiple tags is better done using FGameplayTagContainer than Tarray<FGameplayTag>. This is because not only can you receive tags in array form at any time,
but also various methods make tag management easier.

The GAS framework is very friendly with Gameplay Tags. As the UAbilitySystemComponent implements IGameplayTagAssetInterface, you can directly assign tags to the Ability System Component,
and also manage various states within GameplayAbility using tag containers such as CancelAbilitiesWithTag, BlockAbilitiesWithTag, and ActivationOwnedTags.

By utilizing Gameplay Tags, you can implement the same requirements as follows:

1. Create tags
```shell
// DefaultGameplayTags.ini
[/Script/GameplayTags.GameplayTagsSettings]
//...
+GameplayTagList=(Tag="Actor.Action.Rotate",DevComment="")
+GameplayTagList=(Tag="Actor.State.IsRotating",DevComment="")
```
2. Define macros for easy retrieval of tags
```c++
// ABGameplayTag.h
#define ABTAG_ACTOR_ROTATE FGameplayTag::RequestGameplayTag(FName("Actor.Action.Rotate"))
#define ABTAG_ACTOR_ISROTATING FGameplayTag::RequestGameplayTag(FName("Actor.State.IsRotating"))
```
3. Register tags on the Gameplay Ability
```c++
UABGA_Rotate::UABGA_Rotate()
{
	AbilityTags.AddTag(ABTAG_ACTOR_ROTATE);
	// Tag planted upon activation
	ActivationOwnedTags.AddTag(ABTAG_ACTOR_ISROTATING);
}
```
4. Register and activate abilities based on tags
```c++
// ABGASFountain.h
	UPROPERTY(EditAnywhere, Category=GAS)
	TArray<TSubclassOf<UGameplayAbility>> Abilities;

// Implementation
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
After creating a blueprint class that inherits from the AABGASFountain cpp class, simply add the appropriate activity to the Abilities in the Details panel.

## Summary
Rotating fountain implemented through three methods:
   1. Actor function extension
   2. GAS: Creating a new class (ability) to separate functionality from the actor
   3. GAS + Gameplay Tags: Removing dependencies between the actor and ability

Benefits of using GAS and Gameplay Tags together:
1. Minimization of actor roles
2. Dependency removal. Easy maintenance and higher reusability
3. Scalability + Ease of collaboration with other job roles


![RotatingFountain.gif](img/post/gas/RotatingFountain.gif)