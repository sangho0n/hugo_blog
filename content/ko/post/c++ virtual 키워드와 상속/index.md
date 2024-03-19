---
title: "C++ 상속과 virtual 키워드"
date: 2024-03-08T11:12:45+09:00
image: img/cpp.svg

tags: ["기술면접", "언어", "cpp", "cs", "면접"]
categories: ["c++"]
---
 
다른 언어를 쓰면서 희미해졌던 기억을 되살리기 위한 글.
이번 포스트에서는 c++에서의 **상속**관계 및 **virtual** 키워드에 대해 자세히 알아보도록 하겠다.

---------------------
 
## 상속

c++은 java와 c#등과 같은 다른 객체지향 언어와 달리 상속 시 접근 제한자를 지정할 수 있다.
```c+
// syntax
clsss Derived : <access_specifier> Parent
```
이는 부모클래스를 상속할 때, 부모클래스의 원소를 어떻게 받을 것인지를 나타낸다. 
```access_specifier```에 명시된 유형보다 느슨하게 지정된 원소들을 해당 유형으로 바꿔 상속받는다 생각하면 된다.

아래의 클래스를 상속하는 3가지 유형의 클래스를 살펴보며 각각 어떤 특징을 갖는지 살펴볼 것이다.
```c++
class Base
{
public:
    int pubInt = 1;
private:
    int privInt = 2;
protected:
    int protInt = 3;
};
```
### public
is-a 관계를 나타낼 때 사용. 부모의 접근지정자를 그대로 따른다.
```c++
class Pub : public Base // is-a
{
public:
    Pub()
    {
        pubInt = 1; // public
        //privInt = 2; // 부모클래스의 private이기 때문에 접근할 수 없음
        protInt = 3; // protected
    }
};
```
따라서 외부에서는 부모클래스에서 public으로 지정된 pubInt에만 접근할 수 있다.
```c++
    Pub* pub = new Pub();
    cout << pub->pubInt << endl;
    //cout << pub->privInt << endl; //error: ‘int Base::privInt’ is private within this context
    //cout << pub->protInt << endl; //error: ‘int Base::protInt’ is protected within this context
```

### private
is-implemented-in-terms-of 관계를 나타낼 때 사용(default in cpp). 부모 클래스의 원소 중
private보다 느슨하게 접근할 수 있는 원소(protected와 public으로 지정된 원소)를 private으로 상속한다.
```c++
class Priv : private Base // is-implemented-in-terms-of(cover this later)
{
public:
    Priv()
    {
        pubInt = 1; // public -> private
        //privInt = 2; // 부모클래스의 private이기 때문에 접근할 수 없음
        protInt = 3; // protected- > private
    }
};
```
따라서 외부에서는 부모클래스의 어떤 원소에도 접근할 수 없다.
```c++
    Priv* priv = new Priv();
    //cout << priv->pubInt << endl; //error: ‘int Base::pubInt’ is inaccessible within this context
    //cout << priv->privInt << endl; //error: ‘int Base::privInt’ is private within this context
    //cout << priv->protInt << endl; //error: ‘int Base::protInt’ is protected within this context
```
또한 이 클래스를 상속받는 새로운 클래스를 만들어도 조부모클래스의 어떤 원소에도 접근할 수 없다.
```c++
class GrandChild : Priv
{
public:
    GrandChild()
    {
        // Base의 어떤 원소에도 접근 불가능
    }
};
```

### protected
private 지정자와 마찬가지로 is-implemented-in-terms-of 관계를 나타낼 때 사용.
부모클래스의 public원소를 protected로 변경하여 상속한다.
```c++
class Prot : protected Base // is-implemented-in-terms-of
{
public:
    Prot()
    {
        pubInt = 1; // public -> protected
        //privInt = 2; // error: ‘int Base::privInt’ is private within this context
        protInt = 3;// protected
    }
};
```
따라서 외부에서는 Base클래스의 어떤 원소에도 접근할 수 없다.
```c++
    Prot* prot = new Prot();
    //cout << prot->pubInt << endl; //error: ‘int Base::pubInt’ is inaccessible within this context
    //cout << prot->privInt << endl; //error: ‘int Base::privInt’ is private within this context
    //cout << prot->protInt << endl; // error: ‘int Base::protInt’ is protected within this context
```
또한 private과 달리 이를 상속받는 클래스를 작성했을 때에는 조부모클래스의 원소에 접근할 수 있다.
```c++
class GrandChild2 : Prot
{
public:
    GrandChild2()
    {
        pubInt = 1; // because it is specified protected
        protInt = 3; // because it is specified protected
    }
};
```
다만 위 코드에서는 default(private)으로 상속하였기 때문에, 외부에서는 GrandChild2의 pubInt와 protInt에 접근할 수 없다.

### casting

각각의 경우에 대한 캐스팅 지원 여부는 아래와 같다.
```c++
int main()
{
    // upcasting check
    Base *ptr1, *ptr2, *ptr3;
    ptr1 = new Pub();
    //ptr2 = new Priv(); // error: ‘Base’ is an inaccessible base of ‘Priv’
    //ptr3 = new Prot(); // error: ‘Base’ is an inaccessible base of ‘Prot’
    
    // downcasting check
    Base* base = new Base();
    Pub* pub_down = static_cast<Pub*>(base); // compile-time에 검사. 다형성 여부 신경 쓰지 않음
    // Pub* pub_down = dynamic_cast<Pub*>(base); // 가상함수가 없기 때문에 (source type is not polymorphic) 오류
    // Priv* priv_down = static_cast<Priv*>(base); // error: ‘Base’ is an inaccessible base of ‘Priv’
    // Prot* prot_down = static_cast<Prot*>(base); // error: ‘Base’ is an inaccessible base of ‘Prot’
    
    delete ptr1, ptr2, ptr3, pub_down, base;
    return 0;
}
```
한편,
다른 언어에 익숙한 사람이거나 개발하면서 상속에서의 접근지정자에 대해 크게 고민해본 적이 없는 사람이라면 도대체
is-implemented-in-terms-of이 뭐길래 non-public 상속으로 이를 나타내는지 궁금해할 것이다.

## is-implemented-in-terms-of
일반적인 프로그래밍 언어에서는 is-a관계는 상속(cpp의 경우 public 상속)을, has-a관계는 composition(;containment, aggregation)을 이용해 객체 간의 관계를 나타낸다.
cpp은 위 두 개념과 더불어 is-implemented-in-terms-of라는 용어를 사용하여 객체 관의 관계를 나타낸다.

이름에서도 알 수 있듯, is-implemented-in-terms-of는 어떤 객체가 다른 객체를 사용하여 동작할 때를 의미한다. 
따라서 is-implemented-in-terms-of 역시 cpp에서는 composition을 이용해 나타낼 수 있다.
그렇다면 has-a와 is-implemented-in-terms-of의 차이가 무엇일까? 두 관계를 나누는 기준은 바로 domain이다.

has-a관계는 우리가 일상속에서 쉽게 인지할 수 있는 영역을 프로그래밍으로 모델링할 때 사용된다.
예를 들어 사람, 통신수단, 운송수단과 같은 어플리케이션 도메인을 has-a 관계로 모델링할 수 있다.
반면 is-implemented-in-terms-of는 온전히 소프트웨어 구현의 영역을 나타낼 때를 지칭힌다. 버퍼, 뮤텍스, 탐색트리 등을 예시로 들 수 있다.

cpp에서의 has-a 관계는 다른 언어와 마찬가지로 컴포지션으로 구현할 수 있다. 
한편 is-implemented-in-terms-of 관계는 has-a와 같은 방식으로 구현하거나, non-public 상속을 통해 구현할 수 있다.

그렇다면 어떨 때 non-public 상속으로 구현하고, 어떨 때 composition으로 구현하는 게 적절할까? 
두 방식으로 구현된 클래스를 보며 어떤 방식으로 구현하는 것이 좋을지 살펴보도록 하자.

```c++
template <class T>
class MyList {
public:
    bool   Insert( const T&, size_t index );
    T      Access( size_t index ) const;
    size_t Size() const;
private:
    T*     buf_;
    size_t bufsize_;
};

template <class T>
class MySet1 : private MyList<T> {
public:
    bool   Add( const T& ); // calls Insert()
    T      Get( size_t index ) const; // calls Access()
    using MyList<T>::Size;
//...
};

template <class T>
class MySet2 {
public:
    bool   Add( const T& ); // calls impl_.Insert()
    T      Get( size_t index ) const; // calls impl_.Access()
    size_t Size() const;    // calls impl_.Size();
//...
private:
    MyList<T> impl_;
};
```

### 상속으로 구현 vs  컴포지션으로 구현
앞선 예시 코드를 통해서 확인할 수 있듯, 단일 컴포지션으로 할 수 있는 것은 모두 상속으로도 구현이 가능하다. 그렇다면 왜 is-implemented-in-terms-of와 has-a를 cpp은 구분하는 것일까?

바로 non public 상속으로는 구현할 수 있는 것을 단일 컴포지션으로는 구현할 수 없는 경우가 있기 때문이다.
아래 5가지 항목은 각각의 경우를 말해준다(대략 자주 발생하는 경우부터 나열되었다).
- **protected 멤버에 접근할 필요가 있는 경우.** 보통 protected 메서드(혹은 생성자)를 호출할 필요가 있는 경우를 뜻한다.
- **가상함수를 오버라이딩할 필요가 있는 경우.** base 클래스에 pure virtual function이 있는 경우에는 컴포지션을 사용할 수 없다.
- **구현체를 또다른 구현체의 생성 이전에 생성(혹은 파괴 이후 파괴)해야 하는 경우.** 여러 구현체가 서로 종속되어 있어, 특정 구현체의 생애가 조금 더 길어야하는 경우를 말한다.
구현체에 critical section이나 data transaction과 같이 lock이 필요한 경우엔 다른 구현체의 lifetime을 전부 다 cover할 수 있어야 한다.
- **가상 기본 클래스(virtual base class)를 공유하거나, 가상 기본 클래스 생성에 대한 변경이 필요한 경우.**

마지막으로, is-implemented-in-terms-of과는 거리가 있지만, 컴포지션으로는 구현할 수 없는 non public 상속만의 특징이 하나 더 있다.
- **'제한된 다형성'이 필요한 경우**; 일부 코드에 대해서만 리스코프 치환이 필요한 경우. public 상속은 '항상' 리스코프 치환 가능하다.
반면 non public 상속은 '제한된' IS-A관계를 나타낼 수 있다. 물론 클래스 외부에서는 non public 상속으로는 전혀 다형적이지 않게 느껴지지만
(Derived 클래스는 Base클래스가 아니지만; D is not a B), 멤버함수 내부에서 혹은 freind 클래스에서는 다형성이 필요한 경우가 있을 수 있다.

다시 MySet과 MyList 코드를 살펴보도록 하자. 이 경우에는
- MyList는 protected 멤버가 없다.
- MyList는 추상 클래스가 아니다.
- MySet은 MyList 이외에 다른 클래스를 상속받지 않는다.
- MyList는 MySet이 필요로하거나 생성을 재정의할 가상 기본 클래스를 상속하지 않는다.
- MySet은 MyList가 아니다; MySet is-not-a MyList

다섯가지 상황에 모두 해당되지 않으므로 상속보다는 컴포지션으로 구현하는 것이 좋다. 
상속의 경우 쓸데없는 정보까지 자식클래스에서 확인할 수 있기도 하고, 필요 이상의 종속성이 생기기 때문이다.

~~정리하면서 느낀 건데, c++은 다른 언어에 비해 객체 관계를 구현하는 방법이 참 많은 것 같다.
동시에 이해하기도 쉽지 않을 뿐더러, 객체지향의 원칙에 위배되기에 함부로 남발하면 안되는 부분도 참 많은 것 같다.~~

~~오죽하면 언리얼에서도 [public 상속을 강제](https://forums.unrealengine.com/t/how-to-use-private-inheritance-for-uobject/392346)할까~~


## 다형성

다형성이란 같은 이름의 연산자 혹은 메서드가 다른 역할을 수행할 수 있는 것을 말한다. cpp에서의 다형성은 연산자/메서드 오버로딩과, 메서드 오버라이딩을 통해 구현할 수 있다.
이 중 메서드 오버라이딩은 virtual 키워드와 함께 사용된다. 
이번 포스트에서는 메서드 오버라이딩과 함께 사용되는 virtual키워드가 어떻게 사용되는지 알아보겠다.

![](https://media.geeksforgeeks.org/wp-content/uploads/20200703160531/Polymorphism-in-CPP.png "출처 : https://www.geeksforgeeks.org/cpp-polymorphism/")

### virtual

cpp에서 virtual 키워드는 가상함수를 선언할 때와, 가상 기반 클래스(virtual base class)를 상속할 때 사용된다.

```c++
// syntax
virtual [type-specifiers] member_function_declarator

class Class_Name : virtual [access-specifier] Base_Class_Name
class Class_Name : [access-specifier] virtual Base_Class_Name
```

#### virtual function
가상함수는 다형성을 위해 자식 클래스에서 override하기 위한 함수를 선언할 때 사용된다. 
가상함수로 선언된 함수는 컴파일러에 의해 클래스마다 생성된 vTable(virtual table)에 등록되며,
런타임에 이에 접근(vPtr)하여 어떤 함수를 호출할지 결정한다.

```c++
// C++ program to show the working of vtable and vptr 
#include <iostream> 
using namespace std; 
  
// base class 
class Base { 
public: 
    virtual void function1() 
    { 
        cout << "Base function1()" << endl; 
    } 
    virtual void function2() 
    { 
        cout << "Base function2()" << endl; 
    } 
    virtual void function3() 
    { 
        cout << "Base function3()" << endl; 
    } 
}; 
  
// class derived from Base 
class Derived1 : public Base { 
public: 
    // overriding function1() 
    void function1() 
    { 
        cout << "Derived1 function1()" << endl; 
    } 
    // not overriding function2() and function3() 
}; 
  
// class derived from Derived1 
class Derived2 : public Derived1 { 
public: 
    // again overriding function2() 
    void function2() 
    { 
        cout << "Derived2 function2()" << endl; 
    } 
    // not overriding function1() and function3() 
}; 
  
// driver code 
int main() 
{ 
    // defining base class pointers 
    Base* ptr1 = new Base(); 
    Base* ptr2 = new Derived1(); 
    Base* ptr3 = new Derived2(); 
  
    // calling all functions 
    ptr1->function1(); 
    ptr1->function2(); 
    ptr1->function3(); 
    ptr2->function1(); 
    ptr2->function2(); 
    ptr2->function3(); 
    ptr3->function1(); 
    ptr3->function2(); 
    ptr3->function3(); 
  
    // deleting objects 
    delete ptr1; 
    delete ptr2; 
    delete ptr3; 
  
    return 0; 
}


// Console Output
Base function1()
Base function2()
Base function3()
Derived1 function1()
Base function2()
Base function3()
Derived1 function1()
Derived2 function2()
Base function3()
```

#### virtual base class

cpp은 다중상속을 허용한다. 한편 인스턴스 생성 시 주소공간에 부모가 먼저 생성된 후, 자식의 생성자가 호출된다.
그렇다면 어떤 클래스가 다른 부모, 같은 조부모를 두었다고 했을 때는 어떤 일이 벌어질까?

```c++
#include <iostream> 
using namespace std; 
  
class A { 
public: 
    void show() 
    { 
        cout << "Hello form A \n"; 
    } 
}; 
  
class B : public A { 
}; 
  
class C : public A { 
}; 
  
class D : public B, public C { 
}; 
  
int main() 
{ 
    D object; 
    object.show(); 
} 
```
위와 같은 상황에서는 메모리에 A 영역이 2번 올라가려고 할 것이다. 다행이도 컴파일러는 이를 검출해내어 오류를 방출한다.
사실 위와 같은 상속구조는 데스 다이아몬드 문제를 야기할 수 있기 때문에, 권장되는 상속구조는 아니다.

그럼에도 불구하고 A의 show()를 호출하고 싶을 때는 B와 C가 A를 가상 기본으로 상속받게하면 된다.
```c++
class B : virtual public A { 
}; 
  
class C : public virtual A { 
}; 
// 둘 다 가능한 문법
```

## References
- ["Effective C++” Third Edition by Scott Meyers.](https://aristeia.com/books.html)
- [Uses and Abuses of Inheritance](http://www.gotw.ca/publications/mill06.htm)
- [What is the difference between public, private, and protected inheritance?](https://stackoverflow.com/questions/860339/what-is-the-difference-between-public-private-and-protected-inheritance)
- [virtual (C++)](https://learn.microsoft.com/ko-kr/cpp/cpp/virtual-cpp?view=msvc-170)
- [C++ Polymorphism](https://www.geeksforgeeks.org/cpp-polymorphism/)
- [vTable And vPtr in C++](https://www.geeksforgeeks.org/vtable-and-vptr-in-cpp/)
- [Virtual base class in C++](https://www.geeksforgeeks.org/virtual-base-class-in-c/)