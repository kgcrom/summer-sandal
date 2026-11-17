# 변경 기록

위키에 일어난 일을 날짜순으로 덧붙인다. 지난 항목은 고치지 않는다.

## [2026-11-16] setup | 위키 뼈대 생성

- 기준 태그를 정했다: spring-framework `v7.0.10`, spring-boot `v4.1.2`.
- `summer-sandal` 이 `summer-framework` 를 `api` 로 의존하게 했다.

## [2026-11-17] query | XML 빈 로딩 사용법과 호출 흐름

`ClassPathXmlApplicationContext` 사용 예시와 `spring-beans.xsd` 기능을 정리했다. XML → BeanDefinition 등록 → getBean 생성 흐름을 `wiki/spring/xml-bean-loading.md` 에 남겼다.

## [2026-11-17] setup | 조작 페이지 형식 추가

`wiki/visual/xml-to-bean.html` 을 만들었다. XML 등록과 객체 생성을 한 걸음씩 본다. 변환기는 `wiki/` 의 `.html` 에 공통 CSS 를 넣어 옮긴다.
