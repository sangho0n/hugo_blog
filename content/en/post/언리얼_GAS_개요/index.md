---
title: "Unreal GAS Overview"
date: 2024-02-14T13:53:44+09:00
image: img/unreal.svg
tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[This content is based on lectures by Lee Eunwoo](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4) and [documents compiled by other developers](https://github.com/tranek/GASDocumentation).

For detailed and accurate information, please refer to the above links.

Series
- [Unreal GAS Overview](/p/unreal-gas-overview/) <- Current Post
- [Getting Started with Unreal GAS](/p/getting-started-with-unreal-gas/)

---

## Gameplay Ability System 
- A framework that provides actor abilities and interactions among actors through abilities.
- Advantages
  - Flexibility, Scalability: Easily adaptable to various complex game designs.
  - Modular System: Minimizes dependencies for each function.
  - Network Support
  - Data-Driven Design
  - Maturity: Games like Fortnite already utilize it.
- Disadvantages
  - Learning Curve
  - Overhead in small projects

> Suitable for creating large-scale RPGs and multiplayer games.

## Components

![gas1.png](img/post/gas/gas1.png)

- Gameplay Ability: Implementation of character abilities based on cost and cooldown (optional).
- Attributes: Manipulation of actor characteristics.
- Gameplay Effects: Changes in actor states triggered by ability activation.
- Gameplay Tags: Tagging actors.
- Gameplay Cue: Visual effects.
- Replication for all of the above.

![gas1.png](img/post/gas/gas2.png)

## GAS in Multiplayer Games
The GAS plugin supports client-side prediction (ability activation and effects application without server authorization) as follows:

- Ability Activation
- Animation Montage Playback
- Attribute Changes
- Gameplay Tagging
- Gameplay Cue Execution
- Movement control through CharacterMovementComponent and RootMotionSource functions.

## Blueprint vs C++

GAS should be implemented using C++, but implementation via Blueprints is possible for GameplayAbilities and GameplayEffects.