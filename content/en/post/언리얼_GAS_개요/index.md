---
title: "Unreal GAS Overview"
date: 2024-02-14T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[Based on the lectures by Lee Deukwoo](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4)
and [document compiled by other developers](https://github.com/tranek/GASDocumentation).

For detailed and accurate information, please refer to the links above.

Series
- [Unreal GAS Overview](/p/unreal-gas-overview/) <- Current post
- [Unreal GAS Getting Started](/p/unreal-gas-getting-started/)
- [Unreal GAS Input Handling](../unreal-gas-input-handling/)

---------------

## Gameplay Ability System
- A framework that provides actor abilities and interactions between actors through abilities
- Advantages
  - Flexibility, scalability: Easily utilized for diverse and complex game development
  - Modular system: Minimizes dependency on each function
  - Network support
  - Data-driven design
  - Completeness: Games like Fortnite already utilize it
- Disadvantages
  - Learning curve
  - Overheads in small-scale projects

> Suitable for creating large-scale RPGs and multiplayer games

## Components

![gas1.png](img/post/gas/gas1.png)

- Gameplay Ability: Implements character abilities based on cost and cooldown (optional)
- Attributes: Manipulate actor characteristics
- Gameplay Effects: Change actor states based on ability activation
- Gameplay Tags: Assign tags to actors
- Gameplay Cues: Visual effects
- Replication for all of the above

![gas1.png](img/post/gas/gas2.png)

## GAS in Multiplayer Games
The GAS plugin supports client-side prediction, allowing abilities and effects to be applied without server approval.

- Ability activation
- Animation montage playback
- Attribute modification
- Gameplay tag assignment
- Execution of gameplay cues
- Movement control through CharacterMovementComponent and RootMotionSource functions

## Blueprint vs C++

While GAS should be implemented in C++, GameplayAbilities and GameplayEffects can be implemented in Blueprint.