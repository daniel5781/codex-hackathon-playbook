# codex-hackathon-playbook

제한된 시간 안에 요구사항 확인부터 실제 구현·검증·제출 준비까지 진행하는 한국어 Codex 지침이다.공식 과제 README·운영 규정이 우선이다.

**[AGENTS.md](AGENTS.md)와 [PLAYBOOK.md](PLAYBOOK.md)를 기본으로 읽는다.** 문서 선택은 AGENTS, 조사·문제 정의 합의와 승인 후 구현·공통 기록은 PLAYBOOK, 가져오기·세션 시작·제출은 [QUICKSTART.md](QUICKSTART.md)를 따른다.

| 파일 | 역할·읽는 시점 |
| --- | --- |
| [AGENTS.md](AGENTS.md) | 기본 문서: 선택 기준·최소 규칙·보안 제한 |
| [OPTIMIZATION.md](OPTIMIZATION.md) | 최적화 과제에서 실제로 읽을 문제 분해·기준해·검증·개선 절차 |
| [PROCESS_OPTIMIZATION.md](PROCESS_OPTIMIZATION.md) | 공정 운영 최적화(로트 일정·장비 배정 등) 과제일 때만: 지문을 모델 시트로 옮기기·일정 문제 구성 규칙·독립 검증·솔버 상태 보고 |
| [PLAYBOOK.md](PLAYBOOK.md) | 기본 문서: 조사·합의·승인·구현·검증·공통 기록·개발 이해 지원 |
| [UI_ASSETS.md](UI_ASSETS.md) | 대시보드·웹 UI 과제일 때만 |
| [QUICKSTART.md](QUICKSTART.md) | 가져오기·메인/읽기 전용 검토 세션 시작·제출 확인 |
| [prompts/start.txt](prompts/start.txt) | 플레이북 경로를 준비한 뒤 사용할 짧은 시작 요청 |
| [prompts/process-optimization.txt](prompts/process-optimization.txt) | 공정 운영 최적화 과제에서 단계별로 골라 쓰는 요청 문구 |
| [scripts/setup.sh](scripts/setup.sh) | 선택적 지침 배치. 기본은 점검만, `--apply`일 때만 파일 생성 |
| [tests/test_setup.py](tests/test_setup.py) | 기존 파일 보존·재실행·충돌 검증 |

## 적용 방식

- **공통 준비:** 사용 지침의 필수 제출 의무를 먼저 확인하고, Clone·선택 설치 모두 추가 파일 허용·수집 범위를 확인한다. 기존 파일·Git 변경을 보존한다.
- **기본:** 사용자가 요청한 최초 Clone은 과제 루트의 보이는 `playbook/`에 수행하는 준비 작업이다. 명시적으로 지침을 읽고 조사·문제 정의 합의부터 시작한다. 구현은 “구현 진행” 승인 후 과제 루트에서 하며, 기본 시작에는 `setup.sh`를 실행하지 않는다.
- **선택적 설치·검토 세션:** QUICKSTART의 별도 절차와 시작문을 사용한다. 메인 구현 시작문을 읽기 전용 검토에 재사용하지 않는다.

중첩 Git의 gitlink와 실제 파일 제출은 다를 수 있다. `.git`·사용본·기록을 자동 삭제하거나 무조건 제출에서 제외하지 말고 QUICKSTART의 공식 제출 확인을 따른다. 시험 데이터·구현 코드·작업 로그는 공개 플레이북에 넣지 마라.

## 자동 적용과 명시적 참조

Codex는 시작할 때 전역 지침과 프로젝트 루트(보통 Git 루트)부터 현재 작업 디렉터리까지의 지침을 찾는다. 같은 위치에서는 `AGENTS.override.md`가 `AGENTS.md`보다 우선한다. 하위 `playbook/`의 지침과 링크된 보조 문서를 자동으로 읽었다고 가정하지 말고 필요한 경로·절을 명시하라. [공식 OpenAI 안내](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

설치 스크립트는 기존 루트 지침이 없을 때만 연결용 `AGENTS.md`를 만든다. 사용한 경로·버전과 검증 근거는 PLAYBOOK의 공통 형식으로 보고한다. 제공 버전·설정 차이는 확인하되 업데이트나 전역 설정 변경으로 해결하지 마라.

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
