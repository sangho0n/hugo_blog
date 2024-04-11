---
title: "Unreal GAS Start"
date: 2024-03-18T15:58:25+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[This post is a summary based on lectures by [Lee Deok-Woo](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4) and [documentation prepared by another developer](https://github.com/tranek/GASDocumentation).
For detailed and accurate information, please refer to the mentioned links.

## Series
### GAS Basics
- [Unreal GAS Overview](../unreal-gas-overview/)
- [Unreal GAS Start](../unreal-gas-start/) <- Current Post
### GAS Character Creation Basics
- [Unreal GAS Input Handling](../unreal-gas-input-handling/)
- [Unreal GAS Implementing Continuous Attacks](../unreal-gas-implementing-continuous-attacks/)
- [Unreal Gas Implementing Attack Judgment System](../unreal-gas-implementing-attack-judgment-system/)
### Attributes and Gameplay Effects
- Unreal GAS Character Attributes
- Unreal GAS Gameplay Effects
- Unreal GAS Attribute and UI Integration
### Utilization of GAS
- Unreal GAS Implementing Item Boxes
- Unreal GAS Implementing Area of Effect Skills

---

In this post, we will explore three different ways to implement actor movement and understand the usage of the GAS framework while looking at the differences between each method.

- Actor Function Extension
- Using Game Ability System
- Using Game Ability System + Gameplay Tags

For the actor, the fountain, the movement is based on rotating in place for 3 seconds.

## Actor Function Extension
Implemented using URotatingMovementComponent directly without the GAS framework.

## Using Game Ability System
To implement movement using the GAS framework, you need to understand two concepts:
- Ability System Component
- Game Ability
### Ability System Component
- Manages the Gameplay Ability System
- Only one can be attached per actor
- Actors can trigger Gameplay Abilities through this component
- Allows interaction among actors with this component by the Game Ability System

### Game Ability
- An action that can be registered and triggered within the Ability System Component
- Activation Process:
  - Register in Ability System Component: AbilitySystemComponent->GiveAbility()
  - Trigger the action: AbilitySystemComponent->TryActivateAbility()
  - Implement requirements using SpecHandle, ActorInfo, ActivationInfo within the activated ability
- Key Methods:
  - CanActivateAbility
  - **ActivateAbility**
  - **CancelAbility**
  - EndAbility

Implementing the same movement using the above concepts with the GAS framework:

...

## Using Game Ability System + Gameplay Tags

When using only the Game Ability System without Gameplay Tags, the advantages of the GAS framework may not be fully utilized. 
Let's understand what Gameplay Tags are:

...

Implement the same requirements using Gameplay Tags:

...

## Conclusion
Implemented the rotating fountain using three methods:
1. Actor function extension
2. GAS: Separating functionality from the actor with a new class (ability)
3. GAS + Gameplay Tags: Removing dependencies using tags


![RotatingFountain.gif](img/post/gas/RotatingFountain.gif)