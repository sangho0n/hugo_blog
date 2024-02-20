---
title: "언리얼 Enhanced Input"
date: 2024-02-14T17:44:19+09:00

tags: ["Unreal", "언리얼", "UE", "Enhanced Input", "향상된", "UE5"]
categories: ["Unreal"]
---
![image.png](img%2Fpost%2FEnhancedInput%2Fimage.png)

언리얼 엔진 5버전부터는 기존의 입력 맵핑 시스템이 deprecated 되었다. 이를 대체하는 Enhanced Input에 대해 알아보도록 하자.

 -------------------------------

복잡한 입력 처리, 런타임 컨트롤 리맵핑 등을 효과적으로 지원하기 위해 UE5부터 등장한 개념이다. 
UE4의 디폴트 인풋 시스템의 업그레이드 버전이지만, 하위 호환성 역시 제공한다.
입력 데이터 처리뿐만 아니라 방사형 데스 존, 복합 액션, 콤보공격 등과 같은 기능들을 **에셋 베이스 환경**에서 구현할 수 있다.

# 핵심 개념

Enhanced Input 시스템은 다음 네 가지의 핵심 개념을 갖는다.
- **Input Action** : Enhanced Input 시스템과 프로젝트 코드 간의 연결 통로. 인풋 액션은 자기 자신을 트리거한 입력과는 별개로 최대 3개의 독립적인 축(floating point)의 값을 알릴 수 있다.
- **Input Mapping Context** : 유저의 인풋을 인풋액션에 맵핑하는 역할 수행. 사용자별로 동적으로 추가하거나 삭제할 수 있으며, 우선순위를 가질 수도 있다. 하나 이상의 인풋 맵핑 컨텍스트를 플레이어에 적용하고 우선순위를 매기면, 여러 액션들이 동일한 입력에 의해 트리거되더라도 충돌을 해결할 수 있다.
  
ex) 문 여는 버튼과 가방을 여는 버튼이 같은 경우

한편 아래의 두 개념은 입력 처리를 더욱 유연하게 만드는 데 도움을 주는 요소들이다.
- **Modifier** : 입력값을 다듬을 때 사용. 데드존을 적용하여 미세한 움직임에는 반응하지 않게 하거나, 입력값을 부드럽게 만드는 등의 작업을 수행한다. 이미 정의되어있는 모디파이어를 사용할 수도 있고, 개발자가 직접 정의할 수도 있다.
- **Trigger** : 모디파이어에 의해 가공된 데이터 혹은 다른 인풋 액션의 결괏값을 토대로 해당 인풋 액션을 활성화할지 결정.

## Input Actions
Enhacned Input 시스템과 프로젝트 코드를 연결하는 역할. 
인풋 액션을 트리거하기 위해서는 인풋 맵핑 컨텍스트에 해당 인풋 액션을 추가하고, 인풋 맵핑 컨텍스트를 로컬 플레이어의 **Enhanced Input Local Player Subsystem**에 등록해야한다.

트리거된 인풋 액션에 **Pawn**이 반응하게 하기 위해서는 블루프린트를 이용하거나 cpp에서 이를 제어해야 한다.

![image1.png](img%2Fpost%2FEnhancedInput%2Fimage1.png)

![image2.png](img%2Fpost%2FEnhancedInput%2Fimage2.png)

```c++
void AMyCharacter::SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    
    UEnhancedInputComponent* EnhancedInputComponent = CastChecked<UEnhancedInputComponent>(PlayerInputComponent);
    EnhancedInputComponent->BindAction(MyAction, ETriggerEvent::Triggered, this, &AMyCharacter::MyAction);
}

void AMyCharacter::MyAction(const FInputActionValue& Value) 
{
    // do sth
}
```

## Input Mapping Contexts

인풋 맵핑 컨텍스트에서는 입력과 인풋 액션을 맵핑시킬 수 있다. 맵핑이 완료된 컨텍스트는 로컬 플레이어의 Enhanced Input Local Player Subsystem에 언제든 추가/삭제할 수 있다.

```c++
// do sth ...
    APlayerController* PlayerController = CastChecked<APlayerController>(GetController());
    if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
    {
        Subsystem->ClearAllMappings();
        UInputMappingContext* NewMappingContext = NewCharacterControl->InputMappingContext;
        if (NewMappingContext)
        {
           Subsystem->AddMappingContext(NewMappingContext, 0);
        }
    }
// do sth ...
```

## Modifier
모디파이어는 트리거로 입력 값을 보내기 전 이를 조절할 수 있는 프리 프로세서이다. 언리얼 엔진은 아래의 모디파이어를 기본적으로 제공한다.

![image3.png](img%2Fpost%2FEnhancedInput%2Fimage3.png)

모디파이어를 새로 생성하려면 먼저 InputModifier 클래스를 상속받는 클래스를 만들어야 한다.
![](https://docs.unrealengine.com/5.0/Images/making-interactive-experiences/Input/enhanced-input/image_11.png)
그리고 Modify Raw 함수를 오버라이드한다.
![](https://docs.unrealengine.com/5.0/Images/making-interactive-experiences/Input/enhanced-input/image_12.png)

### 방향 입력

모디파이어의를 적절히 사용한 사례로 하나의 입력 액션을 활용한 2차원 방향 입력을 들 수 있다.
3인칭 템플릿 프로젝트 생성 시, IA_Move와 IMC_Default를 살펴보면 아래와 같이 설정되어 있는 것을 확인할 수 있다.

| 문자 키 | 방향키 | 스칼라값 |                     모디파이어                      | 원하는 방향 벡터  |
|:-----|:----|------|:----------------------------------------------:|------------|
| w    | 위   | 1    |   Swizzle Input Axis Value     | (1, 0, 0)  |
| s    | 아래  | 1    |      Swizzle Input Axis Value, Negate   | (-1, 0, 0) |
| a    | 왼쪽  | 1    |   Negate     | (0, -1, 0) |
| d    | 오른쪽 | 1    |                 -   | (0, 1, 0)  |

UInputModifierSwizzleAxis 모디파이어의 선언부와 구현부 일부를 보면 다음과 같은 것을 확인할 수 있는데,
```c++
/** Swizzle axis components of an input value.
    * Useful to map a 1D input onto the Y axis of a 2D action.
    */
UCLASS(NotBlueprintable, MinimalAPI, meta = (DisplayName = "Swizzle Input Axis Values"))
class UInputModifierSwizzleAxis : public UInputModifier
{
    GENERATED_BODY()

public:

    // Default to XY swap, useful for binding 1D inputs to the Y axis.
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = Settings)
    EInputAxisSwizzle Order = EInputAxisSwizzle::YXZ;

protected:
    virtual FInputActionValue ModifyRaw_Implementation(const UEnhancedPlayerInput* PlayerInput, FInputActionValue CurrentValue, float DeltaTime) override;
    virtual FLinearColor GetVisualizationColor_Implementation(FInputActionValue SampleValue, FInputActionValue FinalValue) const override;
};

FInputActionValue UInputModifierSwizzleAxis::ModifyRaw_Implementation(const UEnhancedPlayerInput* PlayerInput, FInputActionValue CurrentValue, float DeltaTime)
{
    FVector Value = CurrentValue.Get<FVector>();
    switch (Order)
    {
    case EInputAxisSwizzle::YXZ:
       Swap(Value.X, Value.Y);
       break;
    case EInputAxisSwizzle::ZYX:
       Swap(Value.X, Value.Z);
       break;
    case EInputAxisSwizzle::XZY:
       Swap(Value.Y, Value.Z);
       break;
    case EInputAxisSwizzle::YZX:
       Value = FVector(Value.Y, Value.Z, Value.X);
       break;
    case EInputAxisSwizzle::ZXY:
       Value = FVector(Value.Z, Value.X, Value.Y);
       break;
    }
    return FInputActionValue(CurrentValue.GetValueType(), Value);
}
```

Order가 default로 YXZ이므로 위 스칼라값인 1을 모디파이어를 통과시키면 (1.0f, 0.0f, 0.0f)의 값을 가지게 된다.
따라서 위의 표와 같이 모디파이어를 설정하면 스칼라값들을 원하는 방향 벡터로 변환시킬 수 있게 되는 것이다.

## Trigger
트리거는 모디파이어 리스트를 통과한 값을 확인 후, 해당 값이 액션을 활성화시킬 수 있는지 여부를 결정한다. 
다만 예외적으로 Chored Action 트리거는 다른 인풋 액션을 통해서 트리거된다. 아래 사진은 기본 트리거들이다.

![image4.png](img%2Fpost%2FEnhancedInput%2Fimage4.png)

트리거 타입에는 Explicit, Implicit, Blocker 3가지가 있다.
- Explicit : 트리거 성공 시, 입력 성공
- Implicit : 트리거 성공 + 모든 암시 타입의 트리거 성공 시, 입력 성공
- Blocker : 트리거 성공 시, 입력 실패

아래의 표는 트리거 유형에 따른 타입이다.

| 트리거 클래스(cpp)              |                     타입 |
|:--------------------------|-----------------------:|
| UInputTrigger(default)    | ETriggerType::Explicit |
| UInputTriggerCombo        |ETriggerType::Implicit |
| UInputTriggerChordAction  |ETriggerType::Implicit |
| UInputTriggerChordBlocker |ETriggerType::Blocker |


한편 사용자 입력을 처리하고 나면 트리거는 다음 세 개의 상태 중 하나를 반환할 수 있다.
- None : 조건이 충족되지 않아 트리거에 실패함
- Ongoing : 조건이 부분적으로 충족되었으며 트리거가 처리 중이지만 아직 성공하지 않음을 의미
- Triggered : 모든 입력 트리거 조건이 충족되었고 입력 트리거가 성공함

InputTrigger 클래스 혹은 InputTriggerTimedBase 클래스를 상속하면 커스텀 트리거를 생성할 수 있다.
InputTriggerTimedBase는 특정 시간 동안 입력이 지속되었는지 확인하고, 지속되는 동안 Ongoing 상태를 반환한다.
다만 기본적으로 InputTriggerTimedBase는 조건이 충족되어도 Triggered를 반환하지 않기 때문에, 해당 클래스를 상속받아 새로운 트리거를 만들었다면
GetTriggerType과 UpdateState 메서드를 오버라이드하여 원하는 상태를 반환토록 해야한다.