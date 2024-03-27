---
title: "Unreal GAS Overview"
date: 2024-02-14T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[This content is based on lectures by Lee Deok-woo](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4) and [documents compiled by other developers](https://github.com/tranek/GASDocumentation).

For detailed and accurate information, please refer to the above links.

Series
- [Unreal GAS Overview](/p/언리얼-gas-개요/) <- Current Post
- [Starting Unreal GAS](/p/언리얼-gas-시작/)
- [Handling Unreal GAS Inputs](../언리얼-gas-입력처리/)

---------------

## Gameplay Ability System 
- A framework that provides actor abilities and interaction among actors through abilities
- Advantages
  - Flexibility, scalability: Easily used in various and complex game development scenarios
  - Modular system: Minimizes dependencies for each functionality
  - Network support
  - Data-driven design
  - Completion: Games like Fortnite are already utilizing it
- Disadvantages
  - Learning curve
  - Overhead in small projects

> Suitable for creating large-scale RPGs and multiplayer games

## Components

![gas1.png](img/post/gas/gas1.png)

- Gameplay Ability: Implementation of character abilities based on cost and optional cooldown
- Attributes: Manipulation of actor characteristics
- Gameplay Effects: Changes in actor state based on ability activation
- Gameplay Tags: Tagging actors
- Gameplay Cues: Visual effects
- Replication for all the above components

![gas1.png](img/post/gas/gas2.png)

## GAS in Multiplayer Games
The GAS plugin supports client-side prediction, allowing for the activation of abilities and effects without server approval.

- Ability activation
- Playing animation montages
- Modifying attributes
- Tagging actors
- Executing gameplay cues
- Manipulating movement through RootMotionSource functions linked to CharacterMovementComponent

## Blueprint vs C++

GAS should be implemented in C++, but implementing GameplayAbilities and GameplayEffects can be done in Blueprint.