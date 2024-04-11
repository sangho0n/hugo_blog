---
title: "Unreal GAS Overview"
date: 2024-02-14T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[Based on lectures by Lee Geuk Woo](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4)
and [documents summarized by other developers](https://github.com/tranek/GASDocumentation).

For detailed and accurate information, please refer to the links above.

## Series
### Basic of GAS
- [Unreal GAS Overview](../unreal-gas-overview/) <- Current post
- [Getting Started with Unreal GAS](../getting-started-with-unreal-gas/)
### Basic of Creating GAS Characters
- [Input Handling in Unreal GAS](../input-handling-in-unreal-gas/)
- [Implementing Continuous Attacks in Unreal GAS](../implementing-continuous-attacks-in-unreal-gas/)
- [Implementing Attack Judgment System in Unreal GAS](../implementing-attack-judgment-system-in-unreal-gas/)
### Attributes and Gameplay Effects
- Unreal GAS Character Attributes
- Unreal GAS Gameplay Effects
- Linking Attributes to UI in Unreal GAS
### Utilization of GAS
- Implementing Item Boxes in Unreal GAS
- Implementing Area of Effect Skills in Unreal GAS

---------------

## Gameplay Ability System
- A framework that provides the functionality of actor abilities and interaction among actors through abilities.
- Advantages
  - Flexibility, scalability: Easily applicable to a variety of complex game designs.
  - Modular system: Minimizes dependencies for each functionality.
  - Network support
  - Data-driven design
  - Completion: Games like Fortnite are already using it.
- Disadvantages
  - Learning curve
  - Overhead in small-scale projects

> Suitable for creating large-scale RPG and multiplayer games

## Components

![gas1.png](img/post/gas/gas1.png)

- Gameplay Ability: Implementing character abilities based on cost and cooldown (optional).
- Attributes: Manipulating actor characteristics.
- Gameplay Effects: Changes in actor state based on ability activation.
- Gameplay Tags: Assigning tags to actors.
- Gameplay Cues: Visual effects.
- Replication for all of the above.

![gas1.png](img/post/gas/gas2.png)

## GAS in Multiplayer Games
The GAS plugin supports client-side prediction, allowing the activation of abilities and effects without server permission.

- Ability activation
- Playing animation montages
- Modifying attributes
- Assigning gameplay tags
- Executing gameplay cues
- Manipulating movement through CharacterMovementComponent and RootMotionSource functions

## Blueprint vs C++

GAS should be implemented using C++, but it is possible to implement GameplayAbilities and GameplayEffects using blueprints.