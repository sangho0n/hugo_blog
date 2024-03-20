---
title: "안녕하세요"
layout: "about"
slug: "about"
---


# 방문을 환영합니다! 👋

## About Me

작성중...

## About This Blog
이 블로그는 hugo 프레임워크와 hugo-theme-stack 테마를 바탕으로 제작되었습니다. 기본 언어는 한국어지만, 영어도 지원합니다.

배포는 깃헙액션을 통해 자동으로 이루어집니다. 배포과정을 나타내면 아래와 같습니다.

- 한국어로 게시글 작성
- git push -> 워크플로우 실행
- 변경되거나 새롭게 추가된 ```.md```파일 확인
- 위 파일들을 영어로 번역(OpenAI api; gpt3.5 사용)
- hugo 빌드
- 빌드된 파일을 서브모듈로 배포
- 서브모듈에서 깃허브 페이지로 배포

자세한 사항이 궁금하다면, [워크플로우](https://github.com/sangho0n/hugo_blog/blob/master/.github/workflows/main.yml)를 확인해보세요!

제목은 dev-log이지만, 가끔은 취미생활도 올리고 일기장 형식으로 뻘글도 올릴 예정입니다 ㅎㅎ