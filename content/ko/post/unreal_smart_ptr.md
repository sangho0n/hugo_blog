---
title: "언리얼 스마트 포인터"
date: 2024-03-05T17:31:11+09:00

tags: ["Unreal", "언리얼", "UE", "스마트포인터", "포인터"]
categories: ["Unreal"]
---

[공식문서](https://docs.unrealengine.com/5.2/en-US/smart-pointers-in-unreal-engine/)를 바탕으로 이해한 내용을 작성한 글입니다. (의역 多)
실제와는 다른 내용이 있을 수 있습니다. 지적해주시면 감사하겠습니다.

------------

언리얼은 cpp 사용되는 여러 스마트 포인터들에 대한 구현체를 제공한다. 제공되는 클래스로는 Shared 포인터와 Weak포인터, Unique 포인터는 물론 여기에다가 Shared Reference라는 특이한 타입이 하나가 추가되었다. UObject는 별도의 메모리 트래킹 시스템에 의해 관리되기 때문에, UObject를 상속받는 클래스의 인스턴스는 스마트포인터로 감쌀 수 없다. (가비지 컬렉션과는 다른 방식으로 메모리를 회수하는 구조; RAII 패턴)


## 타입 종류

|타입명|사용처|
|------|---|
|TSharedPtr|쉐어드 포인터는 감싸고 있는 객체를 소유하는 클래스이다. 소유하고 있는 동안 객체가 외부에 의해 소멸되지 못하게 막으며, 궁극적으로는 해당 객체를 소유하고 있는 쉐어드 포인터(혹은 레퍼런스)의 개수가 0이 될 때 객체의 소멸을 관장한다. 쉐어드포인터는 감싸고 있는 객체가 없는 상태로도 존재할 수 있다. 감싸고 있는 객체가 null이 아닐 때 언제든 쉐어드 레퍼런스를 생성할 수 있다.|
|TSharedRef|쉐어드 포인터와 유사하게 동작하지만, 감싸고 있는 객체가 null이 될 수 없다는 점에서 다르다. null이 불가능하기 때문에 언제든 쉐어드 포인터로 변환될 수 있으며, 이때 가리키고 있는 객체는 항상 유효한 상태이다. 객체의 소유권을 명확히하고 싶을 때나 객체가 null이 아님을 보장하고 싶을 때 사용된다.|
|TWeakPtr|쉐어드 포인터와 유사하지만, 객체를 소유하고 있지 않기 때문에 라이프사이클에 영향을 주지 않는다. 이러한 특징 때문에 1)**참조사이클**을 끊는 데 유용하게 사용할 수 있지만, 동시에 참조하는 객체가 언제든 경고 없이 null이 될 수 있기에 안전한 접근을 보장하고 싶다면 TSharedPtr로 변환 후 사용하는 것이 좋다.|
|TUniquePtr|유니크 포인터는 객체를 독점적으로 소유한다. 소유권을 넘겨줄 수는 있지만 공유하지는 못한다. 유니크 포인터를 복사하려는 모든 경우에 컴파일 에러가 난다. 스코프를 벗어나게 되면 자동으로 소유하고 있는 객체를 메모리에서 해제한다.|

_1) 두 개 이상의 객체가 서로를 참조하는 경우 발생하는 현상. 참조카운트가 0이 되지 않아 객체들이 해제되지 않고 메모리 누수가 발생할 수 있다._

## 이점

|이점|설명|
|------|---|
|메모리 누수 방지|객체를 자동으로 소멸시켜주기 때문에 메모리 누수를 방지할 수 있다.|
|약한 참조| 순환 참조 문제를 해결하고, 댕글링 포인터 문제를 방지한다.|
|스레드 안전 보장(optional)|필요한 경우 스레드 안전을 보장하는 코드를 추가로 작성할 수 있다. (오버헤드 존재)|
|런타임 안전성| 쉐어드 레퍼런스는 null이 될 수 없고 언제든 참조를 해제할 수 있기 때문에 런타임 안정성을 부여한다.|
|의도 전달|1)**소유자와 관찰자**를 쉽게 구분할 수 있다.|
|메모리 상의 이점|cpp의 포인터 변수의 크기의 2배만으로도 이 모든 기능을 수행한다(64비트 기준; 16바이트의 참조 제어자 포함). 단, 유니크포인터는 cpp의 포인터와 동일한 크기를 갖는다.|

_1) 소유자는 객체를 소유하고 수명주기를 관리한다. 쉐어드포인터와 유니크포인터를 통해 객체를 소유하며, 더이상 필요하지 않을 때 메모리에서 해제한다. 관찰자는 객체를 참조하고 있지만 소유하지는 않는다(위크포인터). 객체의 소유자가 해당 객체를 삭제하면 관찰자는 알아서 null이되어야 한다._

## 헬퍼 클래스와 함수
|헬퍼|설명|
|------|---|
|**_클래스_**| |
|**TSharedFromThis**| TSahredFromThis를 상속받게 하면 해당 클래스에 AsShared와 SharedThis 메서드가 추가된다. 이러한 메서드들은 객체에 대한 TSharedRef를 얻을 수 있게 도와준다.|
|**_함수_**| |
|**MakeShared**와 **MakeShareable**|MakeShared 함수는 일반적인 cpp 포인터에서 TSharedPtr를 생성해낸다. 이 함수는 새로운 객체 인스턴스와 참조 컨트롤러를 단일 메모리 블록에 할당한다. 객체가 public 생성자를 가지고있어야한다. MakeShareable 역시 cpp포인터에서 TSharedPtr를 생성하는 데 사용된다. 이 함수는 객체의 생성자가 private인 경우에도 작동한다. 따라서 본인이 생성하지 않은 객체의 소유권을 얻고싶을 때에도 사용할 수 있으며, 추가로 소멸자가 호출되었을 때 개발자가 원하는 로직을 부여할 수도 있다. 이러한 추가 기능 때문에 MakeShared에 비해 더 유연한 프로그래밍을 할 수 있지만, 동시에 오버헤드 또한 존재한다.|
|**StaticCastSharedRef**와 **StaticCastSharedPtr**| 정적 캐스팅을 지원 하는 유틸리티 함수(주로 다운캐스팅)|
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**ConstCastSharedRef**와 **ConstCastSharedPtr**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|각각의 레퍼런스와 포인터형 변수에 대해 const에서 mutalble 가능한 객체를 반환한다.|

MakeShareable을 사용하여 소멸자에 추가 로직을 부여하는 예시
```CPP
	TSharedPtr<FOnlineSession> SharedPtr = MakeShareable(new FOnlineSession(), [](FOnlineSession* ObjToDelete)-> void
	{
    	// 커스텀 소멸자 구현
		ObjToDelete->PerformAdditionalCleanup();
		delete ObjToDelete;
	});
```

## 세부 구현
언리얼의 스마트포인터 라이브러리는 기능성과 효율성 모두 살린 채 구현되었다.
### 속도
스마트포인터는 자원 관리 및 툴 프로그래밍과 같은 high-level 시스템에서는 매우 유용하게 사용되지만, cpp의 기본 포인터에 비해 느리게 동작하기에 렌더링 같은 low-level 엔진 코드에는 적합하지 않다.

언리얼 스마트포인터 라이브러리는 다음과 같은 성능상의 이점을 갖는다.
- 모든 연산이 상수시간에 수행된다.
- (Shipping 빌드 시) 대부분의 스마트포인터에서의 Dereferencing 시간은 cpp의 기본 포인터만큼 빠르다.
- 스마트포인터의 복사는 새로운 메모리 할당을 요구하지 않는다.
- 스레드 안전 스마트포인터는 lock을 걸지 않는다.

다만 다음과 같은 결점 또한 존재한다.
- 새로운 스마트포인터 생성 및 복사는 cpp 기본 포인터보다 오버헤드가 존재한다.
- 참조카운트를 관리하기에 기본 연산 시 연산 주기가 추가된다.
- 몇몇의 스마트포인터는 cpp 기본 포인터보다 많은 메모리를 사용한다.
- 참조 제어자는 두 번의 힙 메모리 할당을 필요로 한다. MakeSharable 대신 MakeShared를 사용하는 경우 두번째 메모리 할당을 피할 수 있다.

### Intrusive Accessors
일반적으로 스마트포인터가 참조하고 있는 인스턴스는 자신을 소유하고 있는 스마트포인터의 존재를 인지하지 못한다.(이를 non-intrusive라고 부름)
그러나 언리얼의 스마트포인터 라이브러리는 TSharedFromThis를 통해 자신을 참조하는 스마트포인터에 대한 접근자를 얻을 수 있다.
```cpp
class FRegistryObject;
    class FMyBaseClass: public TSharedFromThis<FMyBaseClass>
    {
        virtual void RegisterAsBaseClass(FRegistryObject* RegistryObject)
        {
            // Access a shared reference to 'this'.
            // We are directly inherited from <TSharedFromThis> , so AsShared() and SharedThis(this) return the same type.
            TSharedRef<FMyBaseClass> ThisAsSharedRef = AsShared();
            // RegistryObject expects a TSharedRef<FMyBaseClass>, or a TSharedPtr<FMyBaseClass>. TSharedRef can implicitly be converted to a TSharedPtr.
            RegistryObject->Register(ThisAsSharedRef);
        }
    };
    class FMyDerivedClass : public FMyBaseClass
    {
        virtual void Register(FRegistryObject* RegistryObject) override
        {
            // We are not directly inherited from TSharedFromThis<>, so AsShared() and SharedThis(this) return different types.
            // AsShared() will return the type originally specified in TSharedFromThis<> - TSharedRef<FMyBaseClass> in this example.
            // SharedThis(this) will return a TSharedRef with the type of 'this' - TSharedRef<FMyDerivedClass> in this example.
            // The SharedThis() function is only available in the same scope as the 'this' pointer.
            TSharedRef<FMyDerivedClass> AsSharedRef = SharedThis(this);
            // RegistryObject will accept a TSharedRef<FMyDerivedClass> because FMyDerivedClass is a type of FMyBaseClass.
            RegistryObject->Register(ThisAsSharedRef);
        }
    };
    class FRegistryObject
    {
        // This function will accept a TSharedRef or TSharedPtr to FMyBaseClass or any of its children.
        void Register(TSharedRef<FMyBaseClass>);
    };
```

앞서 언급했듯이 TSharedFromThis를 상속받음으로서 해당 클래스는 AsShared 메서드와 SharedThis를 사용하여 자신의 인스턴스를 참조하는 스마트포인터(TSharedRef)를 얻을 수 있다.
다만 SharedRef 메서드의 경우 파라미터로 this를 받기 때문에, TSharedFromThis를 직접 상속하지 않는 클래스의 경우에는 반환값이 달라진다. 만약 쉐어드 레퍼런스를 반환하는 팩토리 클래스 혹은 쉐어드 레퍼런스(또는 포인터)를 파라미터로 갖는 메서드의 경우(위 예시에서의 ```FRegistryObject::Register(TSharedRef<FMyBaseClass>)```), TSharedFromThis를 직접 상속하는 base class의 쉐어드 포인터를 파라미터 타입으로 설정하는 것이 좋다.

**AsShared 와 SharedThis는 인스턴스화 된 오브젝트의 스마트포인터를 반환하기 때문에, 생성자에서 사용하게되면 crash나 assert를 유발함에 주의**

### 타입캐스팅
언리얼 스마트포인트 라이브러리는 cpp의 포인터와 유사한 방식으로 캐스팅을 할 수 있다.
- Up Casting : cpp의 기본 포인터와 유사하게 암묵적으로 수행된다.(기본 클래스의 포인터를 파생 클래스의 포인터로 자동으로 변환할 수 있다.)
- Const Casting : ConstCastSharedPtr/Ref 메서드를 이용해 수행.
- Static Casting : StaticCastSharedPtr/Ref 메서드를 이용해 수행(주로 다운캐스팅이다).
- Dynamic Casting : 런타임 타입 정보(RTTI)가 없기 때문에 동적캐스팅은 지원되지 않는다.

```cpp
TSharedPtr<FDragDropOperation> Operation = DragDropEvent.GetOperation();

// Some code for validating that the FDragDropOperation is actually an FAssetDragDropOp through other means...

// We can now cast with StaticCastSharedPtr.
TSharedPtr<FAssetDragDropOp> DragDropOp = StaticCastSharedPtr<FAssetDragDropOp>(Operation);
```

### 스레드 안정성
디폴트로 스마트포인터는 싱글스레드 환경에서만 안전하다. 스레드 세이프한 버전을 원한다면 다음과 같은 클래스들을 사용하면 된다.
- TSharedPtr<T, ESPMode::ThreadSafe>
- TSharedRef<T, ESPMode::ThreadSafe>
- TWeakPtr<T, ESPMode::ThreadSafe>
- TSharedFromThis<T, ESPMode::ThreadSafe>

이 클래스들은 레퍼런스 카운트에 대한 원자적 연산을 수행하기 때문에 디폴트 클래스들보다 약간 느리지만, 동작 과정은 cpp 기본 포인터와 매우 유사하다.
- 읽기와 복사 연산은 항상 스레드 안전하다
- 쓰기와 리셋 연산은 안정성을 위해 반드시 동기화되어야한다.

## 첨언

- 쉐어드 포인터/레퍼런스를 메서드의 인자로 넘기는 경우 레퍼런스 카운팅 및 Dereferencing에 의한 오버헤드가 존재한다. 가능하다면 ```const &```로 넘겨주자
- 쉐어드 포인터의 경우 불완전한 클래스에 대한 전방선언을 하는 것이 가능하다.
- 앞서 언급했듯, 스마트포인터와 가비지 컬렉션([UObject Handling](https://docs.unrealengine.com/5.2/en-US/unreal-object-handling-in-unreal-engine/))은 완전히 분리된 메모리 관리 시스템이다.

전방선언 예시
```cpp
// 전방 선언
class IncompleteType;

// 전방 선언된 타입에 대한 스마트 포인터
TSharedPtr<IncompleteType> incompleteTypePtr;

// 나중에 IncompleteType의 정의가 완료되면 해당 타입으로 스마트 포인터를 생성할 수 있음
TSharedPtr<IncompleteType> incompleteTypePtr2 = MakeShared<IncompleteType>();
```