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

After this, a Korean document written in Markdown including the header will be provided. Please translate its header and body into English. 

---
title: "Unreal GAS Introduction"
date: 2024-03-18T15:58:25+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]

[Based on lectures by Lee Deuk-Woo](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4) and [documentation by other developers](https://github.com/tranek/GASDocumentation).

Refer to the given links for detailed and accurate information.

Series:
- [Unreal GAS Overview](/p/unreal-gas-overview/)
- [Unreal GAS Introduction](/p/unreal-gas-introduction/) <- Current post
---

In this post, we will explore the implementation of actor movement using three methods to understand the usage of the GAS framework and examine the differences between each method.

- Actor Function Extension
- Using the Game Ability System
- Using Game Ability System with Gameplay Tags

The actor chosen for this demonstration is a fountain, and the movement involves a 3-second stationary rotation/stop as the base.

## Actor Function Extension
Implementation without the GAS framework using URotatingMovementComponent directly.

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
To implement movement using the GAS framework, it is essential to understand the following two concepts:
- Ability System Component
- Game Ability

### Ability System Component
- Manages the Gameplay Ability System
- Only one can be attached per actor
- Actors can trigger Gameplay Abilities through this component
- Allows for interaction between actors with this component under the Game Ability System

### Game Ability
- An action that can be registered with the Ability System Component to be triggered
- Activation process:
  - Registration with Ability System Component: AbilitySystemComponent->GiveAbility()
  - Activating the action: AbilitySystemComponent->TryActivateAbility()
  - Within the activated ability, requirements are implemented using SpecHandle, ActorInfo, ActivationInfo
- Key methods:
  - CanActivateAbility
  - **ActivateAbility**
  - **CancelAbility**
  - EndAbility

Implementing the same movement as before using these two concepts would look like this:

1. Create an Ability class that inherits from GameplayAbility
```c++
UCLASS()
class ARENABATTLEGAS_API UABGA_Rotate : public UGameplayAbility
{
	GENERATED_BODY()

	virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData) override;
	virtual void CancelAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateCancelAbility) override;
	
};
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
	//...
};
```

3. Register and trigger abilities with the attached components
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

## Using Game Ability System with Gameplay Tags
When using the Game Ability System without Gameplay Tags, the full advantages of the GAS framework may not be utilized.
First, let's understand what Gameplay Tags are.

### Gameplay Tags
FGameplayTag represents a name registered hierarchically like `Parent.Child.Grandchild...`. These tags are registered by the GameplayTagManager.
Using these tags, classes can be categorized, and states can be effectively tracked.

By checking if an object has a Gameplay Tag, the system can replace using bool values or enums with condition statements to track states.

GAS framework is very friendly with Gameplay Tags. Since UAbilitySystemComponent implements IGameplayTagAssetInterface, tags can be directly assigned to Ability System Components and abilities can be managed effectively with Gameplay Tags.

By using Gameplay Tags, the same requirements can be implemented as shown below.

1. Create tags as needed
```shell
// DefaultGameplayTags.ini
[/Script/GameplayTags.GameplayTagsSettings]
//...
+GameplayTagList=(Tag="Actor.Action.Rotate",DevComment="")
+GameplayTagList=(Tag="Actor.State.IsRotating",DevComment="")
```

2. Define macros to easily access tags
```c++
// ABGameplayTag.h
#define ABTAG_ACTOR_ROTATE FGameplayTag::RequestGameplayTag(FName("Actor.Action.Rotate"))
#define ABTAG_ACTOR_ISROTATING FGameplayTag::RequestGameplayTag(FName("Actor.State.IsRotating"))
```

3. Register tags in Gameplay Abilities
```c++
UABGA_Rotate::UABGA_Rotate()
{
	AbilityTags.AddTag(ABTAG_ACTOR_ROTATE);
	// Activation adds the following tag
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

Following this, create a Blueprint class that inherits from the AABGASFountain cpp class and add the desired activities to the Abilities array in the Details panel.

## Summary
Implemented rotating fountain using three methods:
   1. Actor Function Extension
   2. GAS: Creating a new class (ability) to separate functionality from the actor
   3. GAS + Gameplay Tags: Using tags to remove dependencies between actors and abilities

Advantages of using GAS and Gameplay Tags together:
1. Minimize the role of the actor
2. Reduce dependencies, making maintenance easier and increasing reusability
3. Improved scalability and ease of collaboration with other departments

![RotatingFountain.gif](img/post/gas/RotatingFountain.gif)