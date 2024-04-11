Above is the translation of the document from Korean to English:

---
title: "Implementation of Unreal GAS Attack Judgment System"
date: 2024-04-03T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]

This content is summarized based on the lectures by [Lee Deuk-woo](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4) and [documents compiled by other developers](https://github.com/tranek/GASDocumentation).

For detailed and accurate information, please refer to the above links.

## Series
### GAS Fundamentals
- [Unreal GAS Overview](../unreal-gas-overview/)
- [Getting Started with Unreal GAS](../unreal-gas-getting-started/)
### GAS Character Creation Basics
- [Unreal GAS Input Processing](../unreal-gas-input-processing/)
- [Implementing Continuous Attacks in Unreal GAS](../unreal-gas-implementing-continuous-attacks/)
- [Implementation of Unreal GAS Attack Judgment System](../unreal-gas-attack-judgment-system/)<- Current Post
### Attributes and Gameplay Effects
- Unreal GAS Character Attributes
- Unreal GAS Gameplay Effects
- Linking Unreal GAS Attributes with UI
### Utilization of GAS
- Implementing Unreal GAS Item Box
- Implementing Wide-range Skills in Unreal GAS

---

This post explores sending attack judgment timing to GAS using Gameplay Event and TargetActor, implementing attack judgment within the GAS.

## Gameplay Event

In GAS, there is a functionality called GameplayEvent that notifies GAS of a specific event by specifying a GameplayTag. The table below shows what can be done in GAS using GameplayEvent.

| Method                                                         | Description                                                                                                |
|:--------------------------------------------------------------:|------------------------------------------------------------------------------------------------------------|
| UAbilitySystemBlueprintLibrary::SendGameplayEventToActor       | When a specific event occurs, it notifies the actor about it and can activate GameplayAbility using it.   |
| UAbilityTask_WaitGameplayEvent::WaitGameplayEvent              | It waits for the task until a specific event occurs. Various information related to the event can be passed to the Ability waiting for it. |

We will look into how to activate an ability for attack judgment using the SendGameplayEventToActor method. We will implement this in the following sequence:
- [Generate Gameplay Tag for Gameplay Events](#creating-event-tags)
- [Create Custom Animation Notify and Assign to Animation](#creating-and-relaying-notifies)
- [Create a New Gameplay Ability and Assign Trigger Event Tags](#creating-and-triggering-ability)

### Creating Event Tags
Create a Gameplay Tag for events as ```Character.Action.PunchKick```.

### Creating and Relaying Notifies

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

Use the SendGameplayEventToActor method to relay the event during the animation to the Actor.

Next steps involve the creation and utilization of TargetActor in GAS for attack judgment. This includes detecting possible target actors within a specified range in front of the player during an attack. By following the outlined steps and sequence, you can enhance attack judgment in your game with GAS.

Please let me know if you need any further information or clarifications!