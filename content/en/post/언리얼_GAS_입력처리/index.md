
This post is an overview of how to handle input in Unreal GAS.

### Series
#### GAS Basics
- [Unreal GAS Overview](../unreal-gas-overview/)
- [Getting Started with Unreal GAS](../unreal-gas-getting-started/)
#### Creating Characters with GAS Basics
- [Unreal GAS Input Handling](../unreal-gas-input-handling/) <- Current Post
- [Implementing Continuous Attacks in Unreal GAS](../unreal-gas-implementing-continuous-attacks/)
- [Implementing Attack Judgment System in Unreal GAS](../unreal-gas-implementing-attack-judgment-system/)
#### Attributes and Gameplay Effects
- Unreal GAS Character Attributes
- Unreal GAS Gameplay Effects
- Linking Unreal GAS Attributes with UI
#### Utilizing GAS
- Implementing Unreal GAS Item Box
- Implementing Broad Area Skill in Unreal GAS

In this post, we explore how to activate abilities (like jump and attack) through user input.

## OwnerActor and AvatarActor

In the Gameplay Ability System, OwnerActor refers to the actor with AbilitySystemComponent, while AvatarActor represents the physical representation of AbilitySystemComponent.

It's common practice to set PlayerState as the OwnerActor since a character's abilities are often activated based on its current state. In this post, we attach the ability system to the PlayerState and set the OwnerActor and AvatarActor. (Note: Both actors should implement IAbilitySystemInterface even if Owner and Avatar are different.)

## FGameplayAbilitySpec and FGameplayAbilitySpecHandle

To grant abilities to the AbilitySystemComponent, we need to create an FGameplayAbilitySpec structure and register it using the GiveAbility or GiveAbilityAndActivateOnce method.

Once registered, abilities can be accessed through the FGameplayAbilitySpecContainer ActivatableAbilities within the component. The FGameplayAbilitySpecHandle structure is used to uniquely identify granted abilities.

## InputID

To handle input bindings, we can leverage EnhancedInputComponent's BindAction along with the InputID contained in FGameplayAbilitySpec. This approach simplifies generic input processing for abilities like jump and attack.

## InstancingPolicy

InstancingPolicy determines how gameplay abilities are instantiated during execution. For jump abilities, we align with the default class policy.

## Ability Task and Gameplay Cue

Ability Tasks and Gameplay Cues are essential for executing gameplay-related operations and non-gameplay tasks like SFX, VFX, or Camera Shake. Ability Tasks are ideal for actions that need to run only when the ability is active, like animations.

In our case, we utilize UAbilityTask_PlayMontageAndWait to play attack animations as part of the gameplay ability.

## Debugging

To debug ability handling, we create a blueprint class inheriting from our game ability class in Unreal Engine. This blueprint class allows easy assignment of gameplay tags without the need for source code compilation. We also call the console command ```showdebug abilitysystem``` to visualize ability system debugging in the PIE viewport.

Through this process, we can efficiently handle user input to trigger various abilities in the game.