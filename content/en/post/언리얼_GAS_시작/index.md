---
title: "Unreal GAS Overview"
date: 2024-02-14T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

Please translate only the values of title, tags, categories, and series into English without altering the structure. If not, errors like the following may occur:
failed to unmarshal YAML: yaml: line 10: could not find expected ':'

After this, a Korean document written in Markdown including header will be provided. Please translate its header and body into English:

---
title: "Unreal GAS Start"
date: 2024-03-18T15:58:25+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[Link to Lee Deokwoo's lecture](https://www.inflearn.com/course/lee-deokwoo-unreal-programming-part-4) and [document compiled by another developer](https://github.com/tranek/GASDocumentation).

This content was summarized based on the lecture by Lee Deokwoo and the documentation provided by other developers.

For detailed and accurate information, please refer to the links above.

Series:
- [Unreal GAS Overview](/p/unreal-gas-overview/)
- [Unreal GAS Start](/p/unreal-gas-start/) <- Current post
- [Unreal GAS Input Handling](../unreal-gas-input-handling/)

---------------

In this post, while implementing the movement of an actor through three different methods, we will explore the usage of the GAS framework and examine the differences between each method.

- Actor Function Extension
- Using the Game Ability System
- Using the Game Ability System + Gameplay Tag

The actor used is a fountain, and the movement is designed based on 3 seconds of stationary rotation/stop as the standard.

## Actor Function Extension
Implementation using URotatingMovementComponent directly without the GAS framework

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
In order to implement movement using the GAS framework, it is necessary to understand the following two concepts:
- Ability System Component
- Gameplay Ability

### Ability System Component
- Manages the Gameplay Ability System
- Can only be attached once per actor
- Actors can trigger Gameplay Abilities through this component
- Enables interaction between actors with this component controlled by the Game Ability System

### Gameplay Ability
- An action that can be registered in the Ability System Component and triggered
- Activation Process
  - Registration in Ability System Component: AbilitySystemComponent->GiveAbility()
  - Triggering the action: AbilitySystemComponent->TryActivateAbility()
  - Inside the triggered ability, requirements are implemented using SpecHandle, ActorInfo, ActivationInfo
- Key Methods
  - CanActivateAbility
  - **ActivateAbility**
  - **CancelAbility**
  - EndAbility

Using the above two concepts, the implementation of the same movement as in the beginning can be done as follows.

1. Create an ability class by inheriting GameplayAbility
```c++
UCLASS()
class ARENABATTLEGAS_API UABGA_Rotate : public UGameplayAbility
{
	GENERATED_BODY()

	virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo, 
		const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData) override;
	virtual void CancelAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo, 
		const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateCancelAbility) override;
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
    // code skipped for brevity
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

	virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override;
	
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
3. Register and trigger abilities in the attached components
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
Let's first understand what Gameplay Tags are:

### Gameplay Tags

FGameplayTag represents a name registered hierarchically like "Parent.Child.Grandchild...". These tags are registered by the GameplayTagManager.
By using these tags, classes can be categorized and states can be effectively tracked.

Using bool values or enums for state tracking and checking through conditional statements can be replaced by checking if an object has a Gameplay Tag.

Furthermore, managing multiple tags is better done through FGameplayTagContainer than Tarray<FGameplayTag>. This is because using a container allows for easy access to tag arrays at any time and provides various methods for tag management.

The GAS framework is very friendly with Gameplay Tags. As the UAbilitySystemComponent implements IGameplayTagAssetInterface, tags can be directly assigned to the Ability System Component and several states of Gameplay Abilities can be managed with tag containers.

When using Gameplay Tags, the same requirements can be implemented as follows:

1. Create tags
```shell
// DefaultGameplayTags.ini
[/Script/GameplayTags.GameplayTagsSettings]
//...
+GameplayTagList=(Tag="Actor.Action.Rotate",DevComment="")
+GameplayTagList=(Tag="Actor.State.IsRotating",DevComment="")
```
2. Write macros to easily retrieve tags
```c++
// ABGameplayTag.h
#define ABTAG_ACTOR_ROTATE FGameplayTag::RequestGameplayTag(FName("Actor.Action.Rotate"))
#define ABTAG_ACTOR_ISROTATING FGameplayTag::RequestGameplayTag(FName("Actor.State.IsRotating"))
```
3. Register tags in Gameplay Ability
```c++
UABGA_Rotate::UABGA_Rotate()
{
	AbilityTags.AddTag(ABTAG_ACTOR_ROTATE);
	ActivationOwnedTags.AddTag(ABTAG_ACTOR_ISROTATING);
}
```
4. Register and activate abilities using the tags
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
Subsequently, a blueprint class that inherits the AABGASFountain cpp class should be created, and the appropriate activities should be added to Abilities in the Details panel.

## Summary
Implemented the rotation of a fountain using three methods:
1. Actor Function Extension
2. GAS: Creating a new class (ability) to separate functionality from the actor
3. GAS + Gameplay Tags: Removing dependency between actor and ability using tags

Advantages of using GAS and Gameplay Tags together:
1. Minimize the role of the actor
2. Dependency removal. Easy maintenance and high reusability
3. Scalability + Ease of collaboration with other job roles

![RotatingFountain.gif](img/post/gas/RotatingFountain.gif)