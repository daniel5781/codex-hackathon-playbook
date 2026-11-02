# codex-hackathon-playbook

제한된 시간 안에 요구사항 확인부터 실제 구현·검증·제출 준비까지 진행하는 한국어 Codex 지침이다.공식 과제 README·운영 규정이 우선이다.

**기본 지침은 [AGENTS.md](AGENTS.md)다.** 최적화 과제이면 [OPTIMIZATION.md](OPTIMIZATION.md), 웹 UI 과제이면 [UI_ASSETS.md](UI_ASSETS.md)를 실제로 읽어라. 둘 다 해당하면 둘 다 읽고, 무관한 문서는 생략한다. UI 지침을 읽는다고 외부 라이브러리를 반드시 도입하지는 않는다. 문서 상대경로는 플레이북 위치를 기준으로 해석한다. 최초 환경 설정은 [QUICKSTART.md](QUICKSTART.md)를 따른다.

| 파일 | 역할·읽는 시점 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 항상 적용할 최소 규칙 |
| [OPTIMIZATION.md](OPTIMIZATION.md) | 최적화 과제에서 실제로 읽을 문제 분해·기준해·검증·개선 절차 |
| [PLAYBOOK.md](PLAYBOOK.md) | 복잡한 구현·디버깅·검증, 개발 이해 요청 |
| [UI_ASSETS.md](UI_ASSETS.md) | 대시보드·웹 UI 과제일 때만 |
| [QUICKSTART.md](QUICKSTART.md) | 최초 환경 설정·제출 영향 확인 |
| [prompts/start.txt](prompts/start.txt) | 플레이북 경로를 준비한 뒤 사용할 짧은 시작 요청 |
| [scripts/setup.sh](scripts/setup.sh) | 선택적 지침 배치. 기본은 점검만, `--apply`일 때만 파일 생성 |
| [tests/test_setup.py](tests/test_setup.py) | 기존 파일 보존·재실행·충돌 검증 |

## 적용 방식

- **기본:** 공식 과제 README·기존 구현으로 과제 루트를 확인하고, 이 저장소를 그 아래 보이는 `playbook/`에 Clone한다. `playbook/AGENTS.md`와 `playbook/prompts/start.txt`를 명시적으로 읽고 필요한 보조 문서를 선택한다. 과제 루트와 플레이북 경로를 구분하며 구현·실행은 과제 루트에서 한다. 기본 시작에는 `setup.sh`를 실행하지 않는다.
- `playbook/`이 이미 있으면 내용·원격·Git 루트·변경 상태를 확인하고 적합한 기존 사본만 사용한다. 다른 폴더를 덮어쓰거나 임의로 pull·reset·삭제하지 말고, 과제 README·기존 지침도 보존한다. 구체적인 시작 요청은 QUICKSTART를 따른다.
- **선택적 설치:** 공식 제출 규칙에서 추가 파일의 허용·수집 범위를 확인한 경우에만 `setup.sh --apply`를 사용한다. 기존 과제 README·지침을 보존하며 자세한 생성 경로는 QUICKSTART에 있다.
- 숨김 폴더·`.gitignore`·제출 미리보기에서 보이지 않는다는 사실만으로 제출 제외를 판단하지 마라. 설치는 제출물 제외 설정을 바꾸지 않는다.

내부 Clone의 `.git` 때문에 부모 Git에 실제 파일 대신 gitlink가 기록될 수 있다. 기존 과제·사용자 저장소의 `.git`을 삭제하지 마라. 공식 제출 방식에서 사용한 지침의 실제 파일이 포함되는지 확인하고, 일반 파일 제출이 필요하면 Git 메타데이터를 제외한 사용본과 출처·버전을 허용된 제출 경로에 스냅샷으로 보존하라. 적용 위치와 제출용 보존 위치를 구분하고, 시험 데이터·구현 코드·작업 로그는 공개 플레이북에 넣지 마라.

## 자동 적용과 명시적 참조

Codex는 시작할 때 전역 지침과 프로젝트 루트(보통 Git 루트)부터 현재 작업 디렉터리까지의 지침을 찾는다. 같은 위치에서는 `AGENTS.override.md`가 `AGENTS.md`보다 우선한다. 하위 `playbook/`의 지침과 링크된 보조 문서를 자동으로 읽었다고 가정하지 말고 필요한 경로·절을 명시하라. [공식 OpenAI 안내](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

설치 스크립트는 기존 루트 지침이 없을 때만 보조 지침을 읽도록 연결하는 `AGENTS.md`를 만든다. 이미 실행 중인 세션에는 새 경로를 읽도록 요청하고, 새 세션에서도 실제 적용 경로를 확인하라. 제공 버전·설정 차이는 확인하되 업데이트나 전역 설정 변경으로 해결하지 마라.

시작에 한 번만 `실제로 읽은 문서 경로·확인한 플레이북 커밋 버전 / 선택·생략한 문서와 이유 / 적용할 원칙 2개`를 짧게 보고한다. 과제 루트에서 `git -C playbook rev-parse HEAD`와 `git -C playbook status --short`로 플레이북 버전과 미커밋 변경을 구분한다. Git 정보가 없는 복사본은 원본과의 대응을 확인할 수 없으면 버전 미확인으로 기록한다. 과제 저장소의 커밋을 플레이북 버전으로 대신 보고하지 않는다.

완료 시 해당 프로젝트의 기존 작업 기록에 `적용 지침 → 실제 변경 파일·함수 → 실행 명령·결과`를 연결한다. 읽지 않은 문서를 읽었다거나 계획만 한 것을 적용했다고 보고하지 않는다. 작업 기록을 공개 플레이북으로 복사하지 않는다.

## 개발 중 요청

`구조 설명`은 5줄 이내의 구조·데이터 흐름·기술 선택, `변경 설명`은 직전 주요 변경, `이해 점검`은 질문 1개와 답변 후 평가를 제공한다. 자세한 규칙은 PLAYBOOK의 해당 절에 있다. AI 금지 후속 서술형에서는 사용하지 마라.

Computer Use와 시험 자료 외부 전송 등 기본 제약은 AGENTS에 모았다. **시험 환경에서는 Push 금지**, 현재 개인 준비 환경의 공개 플레이북 정리에는 사용자 요청에 따라 커밋·Push할 수 있다. 실제 시험 자료·작업 기록은 이 저장소에 넣지 마라.

## 유지보수 검증

```sh
bash -n scripts/setup.sh
python3 -B -m unittest discover -s tests -p 'test_*.py' -v
git diff --check
```

세팅은 Bash와 기본 명령만 사용하고 의존성·모델·MCP를 설치하지 않는다. 위 검증은 개인 개발 환경용이며 실제 시험의 모델·감독·제출 흐름은 사전 체험에서 확인한다.
