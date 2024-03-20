---
title: "C++ Inheritance and the virtual Keyword"
date: 2024-03-08T11:12:45+09:00
image: img/cpp.svg
tags: ["Technical Interview", "Language", "cpp", "cs", "interview"]
categories: ["c++"]
---

This post aims to delve into the details of **inheritance** relationships and the **virtual** keyword in C++ in order to revive memories blurred by using other languages.

---------------------

## Inheritance

Unlike other object-oriented languages such as Java and C#, C++ allows you to specify access specifiers during inheritance.
```c+
// syntax
class Derived : <access_specifier> Parent
```
This indicates how the elements of the parent class are to be acquired when inheriting from the parent class.
Think of replacing the elements loosely specified in the `access_specifier` with those specified by the type for inheritance.

Let's look at three types of classes that inherit the following class and examine the characteristics of each.
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
Used to represent the is-a relationship. It follows the access specifier of the parent.
```c++
class Pub : public Base // is-a
{
public:
    Pub()
    {
        pubInt = 1; // public
        //privInt = 2; // Cannot access parent class's private
        protInt = 3; // protected
    }
};
```
Therefore, external access is limited to the `pubInt` of the parent class specified as public.
```c++
    Pub* pub = new Pub();
    cout << pub->pubInt << endl;
    //cout << pub->privInt << endl; //error: ‘int Base::privInt’ is private within this context
    //cout << pub->protInt << endl; //error: ‘int Base::protInt’ is protected within this context
```

### private
Used when representing the is-implemented-in-terms-of relationship (default in cpp). Private inheritance inherits the elements of the parent class that can be accessed less strictly than private (i.e., protected and public elements) as private.
```c++
class Priv : private Base // is-implemented-in-terms-of
{
public:
    Priv()
    {
        pubInt = 1; // public -> private
        //privInt = 2; // Cannot access parent class's private
        protInt = 3; // protected -> private
    }
};
```
Therefore, external access is prevented to any elements of the parent class.
```c++
    Priv* priv = new Priv();
    //cout << priv->pubInt << endl; //error: ‘int Base::pubInt’ is inaccessible within this context
    //cout << priv->privInt << endl; //error: ‘int Base::privInt’ is private within this context
    //cout << priv->protInt << endl; //error: ‘int Base::protInt’ is protected within this context
```
Furthermore, even if a new class inherits from this class, access to any elements of the great-grandparent class is still unavailable.
```c++
class GrandChild : Priv
{
public:
    GrandChild()
    {
        // Unable to access any elements of Base
    }
};
```

### protected
Same as the private specifier, it is used when representing the is-implemented-in-terms-of relationship. It inherits the parent class's public elements as protected.
```c++
class Prot : protected Base // is-implemented-in-terms-of
{
public:
    Prot()
    {
        pubInt = 1; // public -> protected
        //privInt = 2; // error: ‘int Base::privInt’ is private within this context
        protInt = 3; // protected
    }
};
```
Therefore, external access is denied to any elements of the Base class.
```c++
    Prot* prot = new Prot();
    //cout << prot->pubInt << endl; //error: ‘int Base::pubInt’ is inaccessible within this context
    //cout << prot->privInt << endl; //error: ‘int Base::privInt’ is private within this context
    //cout << prot->protInt << endl; // error: ‘int Base::protInt’ is protected within this context
```
Moreover, unlike private, when a class inherits from this, it's possible to access the elements of the great-grandparent class.
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

### casting

The supported cast for each case is as follows.
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
    Pub* pub_down = static_cast<Pub*>(base); // checked at compile-time. Doesn't consider polymorphism
    // Pub* pub_down = dynamic_cast<Pub*>(base); // error because source type is not polymorphic
    // Priv* priv_down = static_cast<Priv*>(base); // error: ‘Base’ is an inaccessible base of ‘Priv’
    // Prot* prot_down = static_cast<Prot*>(base); // error: ‘Base’ is an inaccessible base of ‘Prot’
    
    delete ptr1, ptr2, ptr3, pub_down, base;
    return 0;
}
```

## is-implemented-in-terms-of

In general programming languages, the is-a relationship is represented using inheritance (in the case of C++, public inheritance) and the has-a relationship is modeled using composition (containment, aggregation).
C++ introduces the is-implemented-in-terms-of term to indicate relationships between objects where one object uses another to function.
Thus, in C++, is-implemented-in-terms-of can also be represented using composition.
Then, what is the difference between has-a and is-implemented-in-terms-of? The distinction between the two relationships lies in their domain.

The has-a relationship is used to model application domains that we can easily recognize in real life into programming.
For example, application domains like people, means of communication, and modes of transport are modeled through the has-a relationship.
On the other hand, is-implemented-in-terms-of is used solely to indicate the realm of software implementation. Examples include buffers, mutexes, and search trees.

C++ provides the flexibility for implementing has-a relationships using composition or non-public inheritance for is-implemented-in-terms-of relationships.

So, when should we implement a feature using non-public inheritance, and when should we use composition? It's worth examining which approach is suitable by looking at examples of classes created using both methods.

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

### Implementation with Inheritance vs. Composition

As you can see from the above example, whatever can be done with a single composition can also be implemented with inheritance. So, why does C++ distinguish between is-implemented-in-terms-of and has-a?

The reason lies in that some features can be implemented with non-public inheritance but not with a single composition.
Below are five items indicating when to use each method (roughly listed starting from the most common case).
- **When access to protected members is needed.** This usually refers to the need to call protected methods (or constructors).
- **When there is a need to override virtual functions.** If the base class has a pure virtual function, composition cannot be used.
- **When an implementation needs to be constructed (or destroyed) before (or after) another implementation.** If multiple implementations depend on one another such that a specific implementation's lifecycle must cover all others, critical sections like locks, data transactions, etc., it becomes crucial.
- **When sharing a virtual base class or modification is needed when creating a virtual base class.**

Lastly, despite being distant from is-implemented-in-terms-of, non-public inheritance possesses another characteristic that composition alone cannot achieve.
- **When 'restricted polymorphism' is required.** Cases where the Liskov substitution principle needs to be applied only to certain pieces of code. Public inheritance guarantees Liskov substitution always, while non-public inheritance can denote a more limited IS-A relationship. Although from the outside, non-public inheritance may not seem polymorphic at all (D is not a B), situations might arise in member functions or friend classes where polymorphism is needed.

Let's revisit the `MySet` and `MyList` code. In this case:
- `MyList` has no protected members.
- `MyList` is not an abstract class.
- `MySet` has no other classes inherited except `MyList`.
- `MyList` does not inherit any virtual base class.
- `MySet` is not `MyList`; MySet is-not-a MyList

As none of the above five situations apply, it's best to implement it using composition rather than inheritance. Using inheritance can expose unnecessary information to subclasses and create unnecessary dependencies.

With a thorough review, it seems that C++ offers a variety of ways in implementing object relationships compared to other languages. However, it is not easy to understand, and it seems that there are many aspects to consider to avoid violating the principles of object-oriented programming.

_**Note:** The source of this translation is present in the original document._