# summer-sandal

Spring Framework 와 Spring Boot 를 0부터 직접 만들며 배우는 레포다. 제품을 만드는 것이 목적이 아니다. 직접 만들고 실패하면서 아는 영역을 넓히는 것이 목적이다.

- `summer-framework`: Spring Framework 에 대응한다.
- `summer-sandal`: Spring Boot 에 대응한다. `summer-framework` 를 `api` 로 의존한다.
- 배운 것은 Andrej Karpathy 의 LLM Wiki 방식으로 쌓는다. 원문: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f

## 누가 어디에 쓰나

| 경로 | 쓰는 쪽 | 규칙 |
|---|---|---|
| `summer-framework/src`, `summer-sandal/src` | 사람 | AI 는 쓰지 않는다. 리뷰하고 질문하고 힌트를 준다 |
| `raw/` | 사람 | AI 는 읽기만 한다 |
| `wiki/` | AI | 사람은 읽고 방향을 준다 |
| `scripts/`, `.github/`, 빌드 설정 | AI | 요청받았을 때 고친다 |
| `site/` | 생성물 | 손으로 고치지 않는다. 커밋하지 않는다 |

- 사용자가 구현을 물으면 Spring 이 무엇을 왜 하는지 설명한다. `summer-*` 구현 코드는 주지 않는다.
- 사용자가 "코드로 보여줘" 라고 말하면 대화에만 예시를 보인다. 파일에는 쓰지 않는다.
- 리뷰할 때는 틀린 곳과 이유를 말한다. 고친 코드를 대신 쓰지 않는다.

## 폴더

```
raw/steps/NN-이름.md     사람이 쓰는 단계 노트 (가설 · 막힌 곳 · 실패)
wiki/index.md            전체 목차. 질문을 받으면 여기부터 읽는다
wiki/log.md              날짜순 기록. 덧붙이기만 한다
wiki/steps/              단계 노트의 요약 페이지
wiki/concepts/           개념 1개 = 1페이지
wiki/spring/             Spring 코드 지도 (경로:줄 @태그)
wiki/summer/             내 구현이 Spring 과 같은 점 · 다른 점
scripts/build_site.py    wiki/ → site/ HTML 변환
```

## 세 가지 작업

### 묻기

1. `wiki/index.md` 를 읽는다.
2. 관련 페이지를 읽는다. 답이 있으면 Spring 소스를 열지 않는다.
3. 답이 없으면 아래 「Spring 소스 읽기」 규칙으로 찾는다.
4. 답한다. 근거는 `경로:줄 @태그` 로 붙인다.
5. 새로 찾은 것을 `wiki/spring/` 에 남긴다. `index.md` 를 갱신한다. `log.md` 에 한 줄을 덧붙인다.

### 넣기

사용자가 `raw/steps/NN-이름.md` 를 쓰고 "넣어줘" 라고 하면 시작한다. 한 번에 노트 하나만 넣는다.

1. 노트와 그 단계의 커밋 diff 를 읽는다.
2. 요약 3~5줄을 대화에 먼저 보인다. 강조할 곳을 묻는다.
3. `wiki/steps/NN-이름.md` 요약 페이지를 쓴다.
4. 관련 `wiki/concepts/`, `wiki/summer/` 페이지를 갱신한다. 새 내용이 옛 서술과 어긋나면 페이지에 그 사실을 적는다.
5. `index.md` 를 갱신한다. `log.md` 에 한 줄을 덧붙인다.
6. `uv run scripts/build_site.py` 로 확인한다.

### 점검

사용자가 "점검해줘" 라고 하면 아래를 찾는다. 결과를 목록으로 보고한다. 사용자가 승인한 것만 고친다.

- 서로 어긋나는 서술, 낡은 서술
- 어디서도 링크하지 않는 페이지
- 언급은 있는데 페이지가 없는 개념
- `wiki/summer/` 서술과 실제 코드가 다른 곳
- `wiki/spring/` 인용의 태그가 사본의 현재 태그와 다른 곳

## Spring 소스 읽기

| 사본 | 위치 | 태그 | 파일 수 (Java·Kotlin) |
|---|---|---|---|
| spring-framework | `../spring-framework` | `v7.0.10` | 9,605 |
| spring-boot | `../spring-boot` | `v4.1.2` (`springFrameworkVersion=7.0.10`) | 9,032 |

사본은 이 레포의 형제 폴더에 있다. 읽기 전용이다. 이 레포에 복사하지 않는다. 사본이 없으면 아래로 받는다.

```bash
git clone --depth 1 --branch v7.0.10 https://github.com/spring-projects/spring-framework ../spring-framework
git clone --depth 1 --branch v4.1.2 https://github.com/spring-projects/spring-boot ../spring-boot
```

토큰은 파일을 읽을 때 든다. 그래서 읽는 양을 줄인다.

1. **위키부터 읽는다.** `wiki/spring/` 에 답이 있으면 소스를 열지 않는다.
2. **파일을 통째로 읽지 않는다.** `DefaultListableBeanFactory.java` 는 2,813줄이다. 줄 범위만 읽는다.
   - 파일 찾기: `rg --files -g "ClassName.java" ../spring-framework`
   - 줄 찾기: `rg -n "메서드이름\(" 파일경로`
   - 읽기: 찾은 줄 앞뒤 범위만 `offset`·`limit` 으로 읽는다.
3. **찾은 것은 `wiki/spring/` 에 남긴다.** 같은 것을 두 번 찾지 않는다.
4. **태그를 바꾸지 않는다.** 태그를 올리면 줄 번호가 바뀐다. 올릴 때는 이 표와 `wiki/spring/` 인용을 함께 고친다.

여러 파일을 거치는 호출 흐름은 보조 에이전트(`Explore`)에 맡긴다. 결과는 위치와 이름만 받는다. 판단은 본 대화가 한다.

Boot 4 는 폴더가 나뉘어 있다. 핵심은 `core/spring-boot`, `core/spring-boot-autoconfigure` 에 있다. 기능별 코드는 `module/` 아래 128개 폴더에 있다.

인용 형식은 아래와 같다. 경로는 사본 루트 기준이다.

```
DefaultListableBeanFactory#registerBeanDefinition — 빈 정의를 이름으로 등록한다
  spring-beans/src/main/java/org/springframework/beans/factory/support/DefaultListableBeanFactory.java:1252 @v7.0.10
SpringApplication#run — 앱을 시작하고 컨텍스트를 돌려준다
  core/spring-boot/src/main/java/org/springframework/boot/SpringApplication.java:292 @v4.1.2
```

## 위키 형식

- 한 페이지는 한 주제다. 파일 이름은 영어 kebab-case 다.
- `# 제목` 은 페이지에 하나다. 제목 아래 첫 문단은 요약이다. 그 뒤는 `## 섹션` 으로 나눈다.
- 섹션 첫 문장은 결론이다. 굵게 쓴다.
- 위키 페이지끼리는 상대 경로 `.md` 로 링크한다. 위키 밖 파일은 `code` 로 경로만 쓴다.
- `log.md` 항목은 `## [2026-11-16] ingest | 제목` 형식이다. 종류는 `setup`·`ingest`·`query`·`lint` 다. `grep "^## \[" wiki/log.md | tail -5` 로 최근 기록을 본다.
- 변환기는 제목이 없거나 링크 대상이 없으면 실패한다.

## 명령

```bash
./gradlew build                  # 두 모듈 빌드 · 테스트
uv run scripts/build_site.py     # wiki/ → site/
```

`main` 에 push 하면 `.github/workflows/pages.yml` 이 `site/` 를 만들어 GitHub Pages 로 배포한다.

## push 계정

이 레포는 레포 주인 계정으로만 커밋하고 push 한다. 주인은 `origin` URL 의 owner 다. `gh` 활성 계정은 회사 계정 그대로 둔다. 전환하지 않는다.

| 장치 | 하는 일 |
|---|---|
| 레포 설정의 인증 도우미 | push 가 항상 주인 계정의 토큰을 쓴다. `gh` 활성 계정과 상관없다 |
| `.githooks/pre-push` | 주인 계정이 `gh` 에 없거나 고정 설정이 없으면 push 를 막는다 |
| `.githooks/pre-commit` | 작성자·커미터 메일이 주인의 메일이 아니면 커밋을 막는다 |

새로 clone 하면 아래를 한 번 실행한다. 레포 설정만 바꾼다. 전역 설정은 바꾸지 않는다.

```bash
sh .githooks/setup.sh
```

- `pre-commit` 은 `<owner>@...` 와 `...+<owner>@users.noreply.github.com` 메일만 통과시킨다. `user.name`·`user.email` 은 레포 설정에 직접 넣는다.
- hook 은 `git commit`·`git push` 만 막는다. `gh pr create` 같은 `gh` 명령은 활성 계정으로 실행된다. 이 레포에서 `gh` 로 글을 쓰는 명령은 실행 전에 사용자에게 계정을 확인받는다.
- `--no-verify` 는 hook 을 건너뛴다. 쓰지 않는다.
