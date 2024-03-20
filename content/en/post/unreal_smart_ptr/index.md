---
title: "Unreal Smart Pointers"
date: 2024-03-05T17:31:11+09:00
image: img/unreal.svg

tags: ["Unreal", "UE", "Smart Pointer", "Pointer"]
categories: ["Unreal"]
---

Based on the [official documentation](https://docs.unrealengine.com/5.2/en-US/smart-pointers-in-unreal-engine/), this document provides insights into Unreal's implementation of various smart pointers used in C++. The provided classes include Shared Pointers, Weak Pointers, Unique Pointers, and an additional type known as Shared Reference. Due to separate memory management for UObjects, instances of classes inherited from UObject cannot be wrapped with smart pointers (memory is reclaimed differently, following the RAII pattern).

## Types of Pointers

|Type|Usage|
|------|---|
|TSharedPtr|A shared pointer owns the encapsulated object. It prevents the object from being destroyed while it is owned externally, and ultimately governs the destruction of the object when the count of shared pointers (or references) owning it becomes 0. A shared pointer can exist even when it doesn't encapsulate an object. You can create a shared reference anytime the encapsulated object is not null.|
|TSharedRef|Similar to a shared pointer, but the encapsulated object cannot be null. Since null is impossible, it can be converted to a shared pointer anytime, ensuring that the object being pointed to is always valid. It is used when explicit ownership of an object is desired or when ensuring that an object is not null.|
|TWeakPtr|Similar to a shared pointer, but it does not own the object, allowing it to not affect the reference's lifecycle. It can be useful for breaking reference cycles, but accessing an object simultaneously can become null without warning. If safe access is desired, it's recommended to convert it to a shared pointer first.|
|TUniquePtr|A unique pointer exclusively owns the object. Although ownership can be transferred, it cannot be shared. Trying to copy a unique pointer results in a compile error in all cases. When the scope is exited, the owned object is automatically released from memory.|

_1) Refers to a situation where two or more objects reference each other, preventing each other from being released because the reference count never reaches 0, potentially leading to memory leaks._

## Benefits

|Benefit|Description|
|------|---|
|Prevention of Memory Leaks|Automatically deallocates objects, preventing memory leaks.|
|Weak References|Solves circular reference issues and prevents dangling pointer problems.|
|Optional Thread Safety|Additional code can be added for thread safety when needed (comes with overhead).|
|Runtime Safety|Shared references cannot be null and can release references at any time, ensuring runtime safety.|
|Intentional Conveyance|Easily distinguishes between owners and observers.|
|Memory Benefits|Performs all functions with just twice the size of a pointer variable in C++ (based on 64-bit systems; including 16 bytes for reference control). However, a unique pointer has the same size as a C++ pointer.|

_1) Owners own objects and manage their lifecycles. They can own and release objects using shared pointers and unique pointers when they are no longer needed. Observers reference objects but do not own them (weak pointers). When the owner deletes the object, the observer should become null._

## Helper Classes and Functions
|Helper|Description|
|------|---|
|**_Classes_**| |
|**TSharedFromThis**|Inheriting from TSharedFromThis adds AsShared and SharedThis methods to the class. These methods help obtain a TSharedRef for the object.|
|**_Functions_**| |
|**MakeShared** and **MakeShareable**|MakeShared creates a TSharedPtr from a regular C++ pointer. It allocates a new object instance and a reference controller in a single memory block. The object must have a public constructor. MakeShareable is also used to create a TSharedPtr from a C++ pointer. It works even if the object's constructor is private. It allows ownership of objects not created by oneself and can provide custom logic upon destruction. This flexibility can lead to additional programming practices compared to MakeShared but comes with additional overhead.|
|**StaticCastSharedRef** and **StaticCastSharedPtr**| Utility functions supporting static casting (usually downcasting).|
|&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;**ConstCastSharedRef** and **ConstCastSharedPtr**&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;|Return a const to mutable object for each reference and pointer type variable.|

Example of using MakeShareable to add additional logic to the destructor:
```CPP
	TSharedPtr<FOnlineSession> SharedPtr = MakeShareable(new FOnlineSession(), [](FOnlineSession* ObjToDelete)-> void
	{
    	// Custom destructor implementation
		ObjToDelete->PerformAdditionalCleanup();
		delete ObjToDelete;
	});
```

## Detailed Implementation
Unreal's smart pointers library is implemented with both functionality and efficiency in mind.
### Speed
While smart pointers are beneficial in high-level systems like resource management and tool programming, they are not suitable for low-level engine code such as rendering due to performance overhead compared to raw C++ pointers.

Unreal's smart pointers library provides the following performance advantages:
- All operations are performed in constant time.
- (In shipping builds) Dereferencing in most smart pointers is as fast as raw C++ pointers.
- Copying a smart pointer does not require new memory allocation.
- Thread-safe smart pointers do not require locking.

However, there are some drawbacks as well:
- Creating and copying new smart pointers have overhead compared to raw C++ pointers.
- Managing reference counts adds computational overhead to basic operations.
- Some smart pointers require more memory than raw C++ pointers.
- Reference controllers require two heap memory allocations. Using MakeShared can eliminate the second memory allocation.

### Intrusive Accessors
By inheriting TSharedFromThis, a class can obtain accessors for shared pointers that reference it. This allows objects to know which shared pointers are referencing them.
```cpp
class FRegistryObject;
    class FMyBaseClass: public TSharedFromThis<FMyBaseClass>
    {
        virtual void RegisterAsBaseClass(FRegistryObject* RegistryObject)
        {
            // Access a shared reference to 'this'.
            TSharedRef<FMyBaseClass> ThisAsSharedRef = AsShared();
            RegistryObject->Register(ThisAsSharedRef);
        }
    };
    class FMyDerivedClass : public FMyBaseClass
    {
        virtual void Register(FRegistryObject* RegistryObject) override
        {
            TSharedRef<FMyDerivedClass> AsSharedRef = SharedThis(this);
            RegistryObject->Register(ThisAsSharedRef);
        }
    };
    class FRegistryObject
    {
        void Register(TSharedRef<FMyBaseClass>);
    };
```

As mentioned, by inheriting TSharedFromThis, a class can use AsShared and SharedThis methods to obtain a shared reference of its instance. Note that the SharedRef method returns a shared reference to the originally specified type in TSharedFromThis, while SharedThis returns a shared reference with the type of 'this'. It is recommended to use the shared pointer of the base class directly when passing shared pointers in method parameters.

**Be cautious when using AsShared and SharedThis in constructors, as it may lead to crashes or asserts.**

### Type Casting
Unreal's smart pointers library allows casting similar to raw C++ pointers.
- Up Casting: Implicitly performed, allowing a base class pointer to be automatically converted to a derived class pointer.
- Const Casting: Use ConstCastSharedPtr/Ref methods for const casting.
- Static Casting: Use StaticCastSharedPtr/Ref methods for static casting (usually downcasting).
- Dynamic Casting: Dynamic casting is not supported due to the absence of runtime type information (RTTI).

```cpp
TSharedPtr<FDragDropOperation> Operation = DragDropEvent.GetOperation();

// Validating that the FDragDropOperation is an FAssetDragDropOp through other means...

// Casting with StaticCastSharedPtr
TSharedPtr<FAssetDragDropOp> DragDropOp = StaticCastSharedPtr<FAssetDragDropOp>(Operation);
```

### Thread Safety
By default, smart pointers are only safe in single-threaded environments. If you want a thread-safe version, you can use classes like:
- TSharedPtr<T, ESPMode::ThreadSafe>
- TSharedRef<T, ESPMode::ThreadSafe>
- TWeakPtr<T, ESPMode::ThreadSafe>
- TSharedFromThis<T, ESPMode::ThreadSafe>

These classes perform atomic operations on reference counts, which makes them slightly slower than default classes but operation is very similar to raw C++ pointers.
- Reading and copying operations are always thread-safe.
- Writing and reset operations require synchronization for safety.

## Comments

- When passing shared pointers/references as method arguments, there is overhead due to reference counting and dereferencing. If possible, pass by `const &`.
- Shared pointers allow forward declaration of incomplete types.
- As mentioned, smart pointers and garbage collection in C++ ([UObject Handling](https://docs.unrealengine.com/5.2/en-US/unreal-object-handling-in-unreal-engine/)) are two separate memory management systems.