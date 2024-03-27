In the `md` file, the metadata translation is as follows:

```md
---
title: "Unreal GAS Input Processing"
date: 2024-03-26T22:19:41+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---
```

The Korean document body written in Markdown is translated into English below:

---
This post will explore how to trigger abilities (jump, attack) based on user input.

## OwnerActor and AvatarActor

In the Gameplay Ability System, OwnerActor refers to the actor that has the AbilitySystemComponent. On the other hand, AvatarActor indicates the physical representation of the AbilitySystemComponent.

As seen in the previous post, OwnerActor and AvatarActor can be set to the same actor. In most cases, character abilities are triggered based on the current state, so it's common to set PlayerState as the OwnerActor. In this post, we will attach the ability system to the PlayerState and set OwnerActor and AvatarActor accordingly. (Note: even in cases where Owner and Avatar are different actors, both actors must implement IAbilitySystemInterface.)

Furthermore, PlayerState is a convenient class for pub-sub communication between the server and clients, making it especially useful in multiplayer game development. It's advisable to set the PlayerState class as the Owner in multiplayer games.

## FGameplayAbilitySpec and FGameplayAbilitySpecHandle

As mentioned in the previous post, in order to grant abilities to the AbilitySystemComponent, you need to create an instance of the FGameplayAbilitySpec structure and register it. The registered structures can be accessed through the `FGameplayAbilitySpecContainer ActivatableAbilities` within the component.

In methods related to ability activation, you'll notice that FGameplayAbilitySpecHandle structures are used as arguments. This structure is used to uniquely identify granted abilities. It is designed this way when dealing with GameplayAbility in the AbilitySystemComponent.

## InputID

Now, let's consider how to bind actions to trigger abilities. Using the EnhancedInputComponent and InputID, you can create a generic input handling mechanism.

In this post, we will look at the example of how input handling for abilities like jumping and attacking is implemented.

---

These are the English translations of the respective sections of the Korean Markdown document.