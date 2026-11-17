# XML 로 빈 정의를 읽고 꺼내 쓰기

Spring 은 XML 을 두 단계로 처리한다. 먼저 XML 을 읽어 `BeanDefinition`(빈을 만드는 설계도)을 이름별로 등록한다. 그 뒤 `getBean` 이나 `refresh` 마지막 단계에서 설계도대로 객체를 만든다. 기준 태그는 spring-framework `v7.0.10` 이다.

같은 흐름을 한 걸음씩 눌러 보는 페이지가 있다: [XML 한 줄이 Kotlin 객체가 되기까지](../visual/xml-to-bean.html).

## 기본 사용법

**XML 파일을 컨텍스트에 넘기고 `getBean` 으로 꺼낸다.** 공식 문서의 예시는 아래와 같다.

```xml
<!-- services.xml -->
<beans xmlns="http://www.springframework.org/schema/beans" ...>
    <bean id="petStore" class="...PetStoreServiceImpl">
        <property name="accountDao" ref="accountDao"/>
        <property name="itemDao" ref="itemDao"/>
    </bean>
</beans>

<!-- daos.xml -->
<beans ...>
    <bean id="accountDao" class="...JpaAccountDao"/>
    <bean id="itemDao" class="...JpaItemDao"/>
</beans>
```

```java
ApplicationContext context = new ClassPathXmlApplicationContext("services.xml", "daos.xml");
PetStoreService service = context.getBean("petStore", PetStoreService.class);
```

- `id` 는 빈 이름이다. `class` 는 만들 클래스의 전체 이름이다.
- `<property name="x" ref="y"/>` 는 `setX(빈 y)` 를 호출한다는 뜻이다.
- `ref` 는 다른 XML 파일의 빈도 가리킬 수 있다. 두 파일이 한 레지스트리에 등록되기 때문이다.

출처: `framework-docs/modules/ROOT/pages/core/beans/basics.adoc:66-283 @v7.0.10`

## 같은 일을 하는 세 가지 방법

**컨텍스트 없이 `BeanFactory` 와 리더만으로도 같은 일을 한다.** 직접 구현할 때는 가장 아래 방법이 출발점으로 좋다.

| 방법 | 코드 | 차이 |
|---|---|---|
| 클래스패스 XML 컨텍스트 | `new ClassPathXmlApplicationContext("a.xml")` | 생성자에서 `refresh()` 까지 한다. 싱글톤을 미리 만든다 |
| 범용 컨텍스트 + 리더 | `new XmlBeanDefinitionReader(ctx).loadBeanDefinitions("a.xml"); ctx.refresh();` | 읽는 일과 컨텍스트를 분리한다 |
| 팩토리 + 리더 | `new XmlBeanDefinitionReader(factory).loadBeanDefinitions(...)` | 컨텍스트 기능이 없다. 빈은 `getBean` 할 때 만든다 |

출처:

- 범용 컨텍스트 + 리더: `framework-docs/modules/ROOT/pages/core/beans/basics.adoc:306-329 @v7.0.10`
- 팩토리 + 리더: `spring-beans/src/test/java/org/springframework/beans/factory/xml/CollectionsWithDefaultTypesTests.java:38-42 @v7.0.10`

## XML 이 제공하는 기능

**`spring-beans.xsd` 하나가 빈 생성·주입·생명주기·범위를 모두 표현한다.** 요소와 속성을 기능별로 묶으면 아래와 같다.

| 기능 | 요소·속성 |
|---|---|
| 파일 구성 | `<beans>`, `<import resource>`, `<alias>`, `<description>`, 중첩 `<beans profile>` |
| 이름 | `id`, `name`(여러 별칭) |
| 만드는 방법 | `class`, `factory-method`, `factory-bean` |
| 생성자 주입 | `<constructor-arg index/type/name>` |
| 세터 주입 | `<property name>` |
| 값 표현 | `value`, `ref`, `<idref>`, `<null>`, `<list>`, `<set>`, `<map>`, `<props>`, 내부 `<bean>` |
| 자동 연결 | `autowire`, `autowire-candidate`, `primary`, `<qualifier>` |
| 범위·시점 | `scope`(singleton·prototype), `lazy-init`, `depends-on` |
| 생명주기 | `init-method`, `destroy-method`, `default-init-method` |
| 상속 | `abstract`, `parent`, `merge` |
| 메서드 바꾸기 | `<lookup-method>`, `<replaced-method>` |
| 확장 | 다른 네임스페이스 요소(`context:`, `util:`)는 `NamespaceHandler` 가 처리한다 |

출처: `spring-beans/src/main/resources/org/springframework/beans/factory/xml/spring-beans.xsd:61-994 @v7.0.10`

## 1단계: XML → BeanDefinition 등록

**XML 을 DOM 으로 읽고, 요소마다 `BeanDefinition` 을 만들어 이름으로 등록한다.** 이 단계에서는 객체를 하나도 만들지 않는다.

```
ClassPathXmlApplicationContext(String[], boolean, ApplicationContext) — 설정 위치를 저장하고 refresh 를 부른다
  spring-context/src/main/java/org/springframework/context/support/ClassPathXmlApplicationContext.java:136 @v7.0.10
AbstractApplicationContext#refresh — 컨텍스트 시작 절차 전체
  spring-context/src/main/java/org/springframework/context/support/AbstractApplicationContext.java:581 @v7.0.10
AbstractApplicationContext#obtainFreshBeanFactory — 새 팩토리를 만들고 정의를 읽게 한다
  spring-context/src/main/java/org/springframework/context/support/AbstractApplicationContext.java:719 @v7.0.10
AbstractRefreshableApplicationContext#refreshBeanFactory — DefaultListableBeanFactory 를 만들고 loadBeanDefinitions 를 부른다
  spring-context/src/main/java/org/springframework/context/support/AbstractRefreshableApplicationContext.java:119 @v7.0.10
AbstractXmlApplicationContext#loadBeanDefinitions — XmlBeanDefinitionReader 를 만들어 설정 위치를 넘긴다
  spring-context/src/main/java/org/springframework/context/support/AbstractXmlApplicationContext.java:83 @v7.0.10
XmlBeanDefinitionReader#loadBeanDefinitions(EncodedResource) — 같은 파일을 두 번 읽는 순환 import 를 막는다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/XmlBeanDefinitionReader.java:327 @v7.0.10
XmlBeanDefinitionReader#doLoadBeanDefinitions — XML 을 DOM Document 로 바꾼다(XSD 검증 포함)
  spring-beans/src/main/java/org/springframework/beans/factory/xml/XmlBeanDefinitionReader.java:393 @v7.0.10
XmlBeanDefinitionReader#registerBeanDefinitions — Document 를 문서 리더에 넘긴다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/XmlBeanDefinitionReader.java:515 @v7.0.10
DefaultBeanDefinitionDocumentReader#doRegisterBeanDefinitions — profile 을 확인하고 delegate 를 만든다. 중첩 <beans> 면 재귀한다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/DefaultBeanDefinitionDocumentReader.java:118 @v7.0.10
DefaultBeanDefinitionDocumentReader#parseBeanDefinitions — 기본 네임스페이스와 확장 네임스페이스로 나눈다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/DefaultBeanDefinitionDocumentReader.java:166 @v7.0.10
DefaultBeanDefinitionDocumentReader#parseDefaultElement — import·alias·bean·beans 네 요소로 분기한다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/DefaultBeanDefinitionDocumentReader.java:186 @v7.0.10
DefaultBeanDefinitionDocumentReader#processBeanDefinition — <bean> 을 파싱해 레지스트리에 등록한다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/DefaultBeanDefinitionDocumentReader.java:302 @v7.0.10
BeanDefinitionParserDelegate#parseBeanDefinitionElement(Element, BeanDefinition) — id·name 으로 이름과 별칭을 정한다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/BeanDefinitionParserDelegate.java:410 @v7.0.10
BeanDefinitionParserDelegate#parseBeanDefinitionElement(Element, String, BeanDefinition) — class·속성·하위 요소를 BeanDefinition 에 담는다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/BeanDefinitionParserDelegate.java:496 @v7.0.10
BeanDefinitionParserDelegate#parseBeanDefinitionAttributes — scope·lazy-init·init-method 등 속성을 읽는다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/BeanDefinitionParserDelegate.java:552 @v7.0.10
BeanDefinitionParserDelegate#parseConstructorArgElement — <constructor-arg> 를 읽는다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/BeanDefinitionParserDelegate.java:774 @v7.0.10
BeanDefinitionParserDelegate#parsePropertyElement — <property> 를 읽는다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/BeanDefinitionParserDelegate.java:835 @v7.0.10
BeanDefinitionParserDelegate#parsePropertyValue — ref 는 RuntimeBeanReference, value 는 TypedStringValue 로 바꾼다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/BeanDefinitionParserDelegate.java:904 @v7.0.10
BeanDefinitionParserDelegate#parseCustomElement — 확장 네임스페이스 요소를 NamespaceHandler 에 넘긴다
  spring-beans/src/main/java/org/springframework/beans/factory/xml/BeanDefinitionParserDelegate.java:1369 @v7.0.10
BeanDefinitionReaderUtils#registerBeanDefinition — 이름과 별칭을 레지스트리에 등록한다
  spring-beans/src/main/java/org/springframework/beans/factory/support/BeanDefinitionReaderUtils.java:158 @v7.0.10
DefaultListableBeanFactory#registerBeanDefinition — 빈 정의를 이름으로 등록한다
  spring-beans/src/main/java/org/springframework/beans/factory/support/DefaultListableBeanFactory.java:1252 @v7.0.10
```

핵심은 `ref` 처리다. 파싱 시점에는 `ref="accountDao"` 를 객체로 바꾸지 않는다. 이름만 담은 `RuntimeBeanReference` 로 둔다. 그래서 파일 순서나 정의 순서와 상관없이 참조할 수 있다.

## 2단계: BeanDefinition → 객체

**`refresh` 마지막에 싱글톤을 모두 만든다. 만드는 길은 `getBean` 과 같다.**

```
AbstractApplicationContext#finishBeanFactoryInitialization — 남은 싱글톤을 미리 만든다
  spring-context/src/main/java/org/springframework/context/support/AbstractApplicationContext.java:621 @v7.0.10
DefaultListableBeanFactory#preInstantiateSingletons — lazy 가 아닌 싱글톤마다 getBean 을 부른다
  spring-beans/src/main/java/org/springframework/beans/factory/support/DefaultListableBeanFactory.java:1102 @v7.0.10
AbstractBeanFactory#getBean(String) — doGetBean 으로 넘긴다
  spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractBeanFactory.java:195 @v7.0.10
AbstractBeanFactory#doGetBean — 캐시를 보고, 없으면 scope 별로 createBean 을 부른다
  spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractBeanFactory.java:236 @v7.0.10
AbstractAutowireCapableBeanFactory#createBean — 생성 전 확장점을 거쳐 doCreateBean 을 부른다
  spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractAutowireCapableBeanFactory.java:486 @v7.0.10
AbstractAutowireCapableBeanFactory#doCreateBean — 생성 → 주입 → 초기화 순서를 묶는다
  spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractAutowireCapableBeanFactory.java:554 @v7.0.10
AbstractAutowireCapableBeanFactory#createBeanInstance — 생성자나 팩토리 메서드로 객체를 만든다
  spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractAutowireCapableBeanFactory.java:1173 @v7.0.10
AbstractAutowireCapableBeanFactory#populateBean — autowire 와 <property> 값을 모은다
  spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractAutowireCapableBeanFactory.java:1388 @v7.0.10
AbstractAutowireCapableBeanFactory#applyPropertyValues — RuntimeBeanReference 를 getBean 으로 풀고 세터를 부른다
  spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractAutowireCapableBeanFactory.java:1660 @v7.0.10
AbstractAutowireCapableBeanFactory#initializeBean — Aware 콜백, BeanPostProcessor, init-method 를 차례로 부른다
  spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractAutowireCapableBeanFactory.java:1797 @v7.0.10
AbstractAutowireCapableBeanFactory#invokeInitMethods — afterPropertiesSet 과 init-method 를 부른다
  spring-beans/src/main/java/org/springframework/beans/factory/support/AbstractAutowireCapableBeanFactory.java:1854 @v7.0.10
```

## 직접 만들 때 볼 경계

**최소 구현은 "파싱해서 정의 등록"과 "정의로 객체 생성"을 나누는 데서 시작한다.** Spring 은 이 둘을 `BeanDefinitionRegistry` 인터페이스 하나로 잇는다. 리더는 레지스트리만 알고, 팩토리가 레지스트리를 구현한다.

- 리더 → 레지스트리: `XmlBeanDefinitionReader` 는 팩토리 전체가 아니라 `BeanDefinitionRegistry` 만 받는다.
- 문서 리더 → 위임자: 요소 순회(`DefaultBeanDefinitionDocumentReader`)와 요소 해석(`BeanDefinitionParserDelegate`)이 나뉘어 있다.
- 참조는 늦게 푼다: 파싱 때는 이름만, 생성 때 `getBean` 으로 푼다.
- 확장 네임스페이스는 이 흐름 밖의 갈래다. 처음 구현에서는 빼도 된다.
