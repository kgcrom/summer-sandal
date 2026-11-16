#!/bin/sh
# clone 뒤 한 번 실행한다: sh .githooks/setup.sh
# 레포 설정(.git/config)만 바꾼다. 전역 설정은 바꾸지 않는다.
#  1. hook 폴더를 연결한다.
#  2. push 인증을 레포 주인 계정의 토큰으로 고정한다. gh 활성 계정과 상관없다.
set -eu
cd "$(git rev-parse --show-toplevel)"

url=$(git remote get-url origin)
owner=$(printf '%s' "$url" | sed -nE 's#^https://github\.com/([^/]+)/.*#\1#p')
if [ -z "$owner" ]; then
    echo "origin 이 https://github.com/<owner>/<repo> 형식이 아니다: $url" >&2
    exit 1
fi

git config --local core.hooksPath .githooks

# 첫 줄의 빈 값은 앞선 도우미(키체인)를 끈다. 토큰이 키체인에 저장되지 않는다.
# 둘째 줄은 gh 에게 주인 계정의 토큰을 달라고 한다. 토큰 값은 파일에 적히지 않는다.
key="credential.https://github.com.helper"
git config --local --unset-all "$key" 2>/dev/null || true
git config --local --add "$key" ""
git config --local --add "$key" "!f() { [ \"\$1\" = get ] || exit 0; t=\$(gh auth token --hostname github.com --user $owner 2>/dev/null) || { echo \"gh 에 $owner 계정이 없다: gh auth login --hostname github.com\" >&2; echo quit=1; exit 0; }; printf 'username=$owner\\npassword=%s\\n' \"\$t\"; }; f"

echo "push 계정: $owner 로 고정했다"
if email=$(git config --local --get user.email); then
    echo "커밋 작성자: $(git config --local --get user.name) <$email>"
else
    echo "커밋 작성자가 레포 설정에 없다. 아래 두 줄을 개인 값으로 실행한다." >&2
    echo "  git config --local user.name \"<이름>\"" >&2
    echo "  git config --local user.email \"<개인 메일>\"" >&2
fi
