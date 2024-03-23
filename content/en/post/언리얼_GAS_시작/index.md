---
title: "Unreal GAS Introduction"
date: 2024-03-18T15:58:25+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[Link to Ideukwoo's lecture](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4)
and [document prepared by another developer](https://github.com/tranek/GASDocumentation) were referenced for this summary.

For detailed and accurate information, please refer to the links provided.

Series
- [Unreal GAS Overview](/p/unreal-gas-overview/)
- [Unreal GAS Introduction](/p/unreal-gas-introduction/) <- Current Post

---------------

In this post, we will explore the usage of the GAS framework by implementing actor movement through three different methods, and examining the differences between them.

- Actor Function Extension
- Using Game Ability System
- Using Game Ability System with Gameplay Tags

The actor used is a fountain, and the movement involves rotating/stopping in place for 3 seconds.

## Actor Function Extension
Implemented without the GAS framework using URotatingMovementComponent directly.

## Using Game Ability System
To implement movement using the GAS framework, understanding the following two concepts is necessary:
- Ability System Component
- Gameplay Ability

### Ability System Component
- Manages the gameplay ability system
- Only one attached per actor
- Allows actors to trigger Gameplay Abilities through it
- Enables interaction between actors with this component through the Game Ability System

### Gameplay Ability
- An action that can be registered with the Ability System Component to be triggered
- Activation Process
  - Register with Ability System Component: AbilitySystemComponent->GiveAbility()
  - Trigger Action: AbilitySystemComponent->TryActivateAbility()
  - Within the activated ability, use SpecHandle, ActorInfo, ActivationInfo to implement requirements
- Key Methods
  - CanActivateAbility
  - **ActivateAbility**
  - **CancelAbility**
  - EndAbility

Implementing the same movement as the beginning without GAS is as follows:

1. Create an ability class by inheriting from GameplayAbility
```c++
UCLASS()
class ARENABATTLEGAS_API UABGA_Rotate : public UGameplayAbility
{
	GENERATED_BODY()

	virtual void ActivateAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilityActivationInfo ActivationInfo, const FGameplayEventData* TriggerEventData) override;
	virtual void CancelAbility(const FGameplayAbilitySpecHandle Handle, const FGameplayAbilityActorInfo* ActorInfo, const FGameplayAbilityActivationInfo ActivationInfo, bool bReplicateCancelAbility) override;
	
};
```

2. Attach components to the actor and implement the interfaces
```c++
UCLASS()
class ARENABATTLEGAS_API AABGASFountain : public AABFountain, public IAbilitySystemInterface
{
	GENERATED_BODY()
public:
	AABGASFountain();

	virtual UAbilitySystemComponent* GetAbilitySystemComponent() const override;
	// Additional Implementation...
};
```

3. Register and activate abilities with the attached components
```c++
void AABGASFountain::PostInitializeComponents()
{
	Super::PostInitializeComponents();
	
	AbilitySystemComponent->InitAbilityActorInfo(this, this);
	FGameplayAbilitySpec RotateSpec(UABGA_Rotate::StaticClass());
	AbilitySystemComponent->GiveAbility(RotateSpec);
}
```

## Using Game Ability System + Gameplay Tags
When utilizing Gameplay Tags with the Game Ability System, the advantages include:
1. Minimizing the role of the actor
2. Reducing dependencies, making maintenance easier and increasing reusability
3. Enhanced scalability and collaboration with other job roles

![RotatingFountain.gif](img/post/gas/RotatingFountain.gif)
