---
title: "Unreal GAS Overview"
date: 2024-02-14T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "Ability"]
categories: ["Unreal"]
series: ["Gameplay Ability System (GAS)"]
---

[Overview of Unreal GAS](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4)
and [documents organized by other developers](https://github.com/tranek/GASDocumentation) were reviewed to create this content.

For detailed and accurate information, please refer to the above links.

Series
- [Overview of Unreal GAS](/p/overview-of-unreal-gas/) <- Current Post
- [Getting Started with Unreal GAS](/p/getting-started-with-unreal-gas/)
- [Input Processing in Unreal GAS](../input-processing-in-unreal-gas/)
- [Implementing Continuous Attacks in Unreal GAS](../implementing-continuous-attacks-in-unreal-gas/)

---------------

## Gameplay Ability System
- A framework that provides actor abilities and interaction functions among actors through abilities
- Advantages
  - Flexibility, Scalability: Easily applicable to various and complex game development
  - Modular System: Minimizes dependencies for each function
  - Network Support
  - Data-Driven Design
  - Completion: Games like Fortnite are already utilizing this
- Disadvantages
  - Learning Curve
  - Overhead in small projects

> Suitable for creating large-scale RPGs and multiplayer games

## Components

![gas1.png](img/post/gas/gas1.png)

- Gameplay Ability: Implementing character abilities based on cost and cooldown (optional)
- Attributes: Manipulating actor characteristics
- Gameplay Effects: Changing actor states based on ability activation
- Gameplay Tags: Tagging actors
- Gameplay Cues: Visual effects
- Replication for all of the above

![gas1.png](img/post/gas/gas2.png)

## GAS in Multiplayer Games
The GAS plugin supports client-side prediction, allowing abilities to be activated and effects applied without server approval.

- Ability activation
- Playing animation montages
- Attribute changes
- Tagging in gameplay
- Executing gameplay cues
- Manipulating movement through CharacterMovementComponent and RootMotionSource functions

## Blueprint vs C++

GAS should be implemented using C++, but can be implemented using Blueprints for GameplayAbilities and GameplayEffects.