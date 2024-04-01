---
title: "언리얼 GAS 개요"
date: 2024-02-14T13:53:44+09:00
image: img/unreal.svg

tags: ["Unreal", "언리얼", "UE", "GAS", "어빌리티"]
categories: ["Unreal"]
series: ["게임플레이 어빌리티 시스템(GAS)"]
---


[이득우 님의 강의](https://www.inflearn.com/course/%EC%9D%B4%EB%93%9D%EC%9A%B0-%EC%96%B8%EB%A6%AC%EC%96%BC-%ED%94%84%EB%A1%9C%EA%B7%B8%EB%9E%98%EB%B0%8D-part-4)
와 [다른 개발자가 정리해놓은 문서](https://github.com/tranek/GASDocumentation)를 보고 정리한 내용입니다.

자세하고 정확한 내용은 위 링크를 참조하세요
 
시리즈
- [언리얼 GAS 개요](/p/언리얼-gas-개요/) <- 현재포스트
- [언리얼 GAS 시작](/p/언리얼-gas-시작/)
- [언리얼 GAS 입력처리](../언리얼-gas-입력처리/)
- [언리얼 GAS 연속 공격 구현](../언리얼-gas-연속공격/)

---------------

## 게임플레이 어빌리티 시스템 
- 액터의 어빌리티 및 어빌리티를 통한 액터 간 상호작용 기능을 제공하는 프레임워크
- 장점
  - 유연성, 확장성 : 다양하고 복잡한 게임 제작에 쉽게 활용할 수 있다.
  - 모듈러 시스템 : 각 기능에 대한 의존성 최소화
  - 네트워크 지원
  - 데이터 기반 설계
  - 완성도 : 포트나이트 등의 게임이 이미 이를 활용하고 있음
- 단점
  - 학습 비용
  - 소규모 프로젝트에서의 오버헤드

> 큰 규모의 RPG 및 멀티플레이 게임을 만들기에 적합함


## 구성 요소

![gas1.png](img/post/gas/gas1.png)

- 게임플레이 어빌리티 : 비용 및 쿨타임(optional) 기반의 캐릭터 어빌리티 구현
- 어트리뷰트 : 액터의 특성 조작
- 게임플레이 이펙트 : 어빌리티 발동에 따른 액터의 상태 변경
- 게임플레이 태그 : 액터에 대한 태그 지정
- 게임플레이 큐 : 시청각효과
- 위 모든 것들에 대한 레플리케이션

![gas1.png](img/post/gas/gas2.png)

## 멀티플레이 게임에서의 GAS
GAS 플러그인은 다음과 같은 client-side-prediction(서버의 허가 없이 어빌리티 발동 및 이펙트를 적용하는 것)을 지원한다.

- 어빌리티 발동
- 애니메이션 몽타주 재생
- 어트리뷰트 변경
- 게임플레이 태그 지정
- 게임플레이 큐 실행
- CharacterMovementComponent와 연결된 RootMotionSource functions를 통한 움직임 조작

## 블루프린트 vs C++

GAS는 cpp을 사용하여 구현되어야 하지만, GameplayAbilities와 GameplayEffects에 한하여 블루프린트로 구현이 가능하다.