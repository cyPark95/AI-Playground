# 🤖 AI Code Review Automation Pipeline

## 🎯 프로젝트 목적 (Purpose)

이 레포지토리는 단순한 LLM API 호출을 넘어, **'AI 에이전트(Agent)'와 'MCP(Model Context Protocol)' 아키텍처**를 깊이 있게 이해하고 실무에 적용하기 위한 학습
프로젝트입니다.

단순히 변경된 코드 몇 줄만 검사하는 봇을 시작으로, 점진적으로 프로젝트 전체의 맥락을 이해하고 인프라(DB, Cache 등) 구조까지 파악하여 리뷰를 남기는 고도화된 **Java Spring 기반 멀티 에이전트
파이프라인**으로 발전시키는 것을 목표로 합니다.

## 🗺️ 학습 및 진화 단계 (Roadmap)

### Step 1: 기본 리뷰 봇 구축 (Basic CI/CD)

* **목표:** CI/CD 파이프라인과 AI API 연동의 기본기 체득
* **내용:** GitHub Actions와 Python 스크립트를 활용해, PR 생성 시 변경된 코드(Git Diff)만 Gemini API로 분석하여 코멘트를 남기는 기초 파이프라인 구축.

### Step 2: 에이전트의 이해 (Function Calling)

* **목표:** AI의 맥락(Context) 부족 한계 극복 및 Planner/Skill 개념 체득
* **내용:** 텍스트 생성을 넘어, AI가 스스로 판단하여 레포지토리 내의 다른 연관 파일 내용을 읽어올 수 있도록 로컬 함수 호출(Function Calling) 권한 부여.

### Step 3: MCP 아키텍처 도입 (Model Context Protocol)

* **목표:** 표준화된 AI 도구 생태계(MCP) 연동 및 자율 주행 체감
* **내용:** 개별 함수 하드코딩을 넘어, 외부 'GitHub MCP 서버' 등을 연동하여 AI가 레포지토리 전체를 자율적으로 탐색하는 에이전트 환경 구성.

### Step 4: 엔터프라이즈 백엔드 이관 (Java Spring Boot)

* **목표:** 대규모 트래픽 및 실무 아키텍처(동시성 제어, 병렬 처리) 대응
* **내용:** Python 단발성 스크립트를 **Java Spring Boot + Spring AI** 기반의 전용 웹훅(Webhook) 서버로 이관. MySQL, Redis MCP를 추가로 연결하여 DB
  스키마와 데이터 정합성까지 고려하는 시니어급 자동 리뷰어 완성.

---
*🛠️ Tech Stack: GitHub Actions, Python, Java 21, Spring Boot, Spring AI, Gemini API, MCP*
