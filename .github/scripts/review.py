import os
import sys
import requests
import json
import re

# --- 1. 도구(Tools) 정의: 실제 로컬에서 실행될 함수들 ---

def list_files(directory="."):
    """레포지토리의 파일 목록을 나열합니다."""
    files_list = []
    for root, dirs, files in os.walk(directory):
        if ".git" in dirs: dirs.remove(".git")
        if ".gradle" in dirs: dirs.remove(".gradle")
        if "build" in dirs: dirs.remove("build")
        for file in files:
            files_list.append(os.path.join(root, file))
    return "\n".join(files_list)

def read_file_content(file_path):
    """특정 파일의 전체 내용을 읽어옵니다."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# Gemini에게 알려줄 도구 명세 (Function Declaration)
TOOLS_SPEC = [
    {
        "function_declarations": [
            {
                "name": "list_files",
                "description": "레포지토리 내의 모든 파일 목록을 조회합니다. 프로젝트 구조를 파악할 때 사용하세요.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {"type": "string", "description": "조회할 디렉토리 경로 (기본값: .)"}
                    }
                }
            },
            {
                "name": "read_file_content",
                "description": "특정 파일의 전체 내용을 읽어옵니다. Diff만으로 부족한 맥락을 파악하거나 정확한 라인 번호를 확인할 때 사용하세요.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {"type": "string", "description": "읽을 파일의 전체 경로"}
                    },
                    "required": ["file_path"]
                }
            }
        ]
    }
]

# --- 2. API 통신 및 에이전트 루프 ---

def get_pr_diff(repo, pr_number, token):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3.diff"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def call_gemini_api(messages, api_key):
    """Gemini API를 호출합니다 (메시지 히스토리 포함)."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
    
    payload = {
        "contents": messages,
        "tools": TOOLS_SPEC,
        "generationConfig": {"response_mime_type": "application/json"}
    }
    
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
    response.raise_for_status()
    return response.json()

def run_agent_loop(diff, api_key):
    """도구 사용을 포함한 에이전트 실행 루프"""
    
    system_prompt = """
    너는 시니어 Java Spring 백엔드 엔지니어 기술 면접관이자 멘토야. 
    제공되는 Git Diff를 분석하여 리뷰를 남겨줘.
    
    **에이전트 미션:**
    1. 제공된 Diff만으로 분석이 부족하다면 `read_file_content`를 사용하여 연관 코드를 직접 읽어봐.
    2. 특히 정확한 '라인 번호'와 '파일 경로'를 확인하기 위해 전체 파일을 읽는 것을 강력히 권장해.
    3. 리뷰는 반드시 지정된 JSON 형식으로만 응답해.
    
    **응답 형식:**
    {
      "summary": "총평",
      "reviews": [{"path": "경로", "line": 숫자, "body": "내용"}]
    }
    """

    # 메시지 히스토리 초기화
    messages = [
        {"role": "user", "parts": [{"text": system_prompt + f"\n\nHere is the diff:\n{diff}"}]}
    ]

    # 최대 5번까지 도구 사용 루프 허용
    for _ in range(5):
        response = call_gemini_api(messages, api_key)
        candidate = response['candidates'][0]
        content = candidate['content']
        messages.append(content) # AI의 응답을 히스토리에 추가

        # 1. 도구 호출(Function Call)이 있는지 확인
        if 'parts' in content and 'functionCall' in content['parts'][0]:
            function_call = content['parts'][0]['functionCall']
            func_name = function_call['name']
            args = function_call.get('args', {})

            print(f"DEBUG: AI가 도구 사용을 요청함 -> {func_name}({args})")

            # 실제 로컬 함수 실행
            if func_name == "list_files":
                result = list_files(**args)
            elif func_name == "read_file_content":
                result = read_file_content(**args)
            else:
                result = "Unknown function"

            # 도구 실행 결과를 메시지에 추가
            messages.append({
                "role": "function",
                "parts": [{
                    "functionResponse": {
                        "name": func_name,
                        "response": {"result": result}
                    }
                }]
            })
            # 다시 루프를 돌아 Gemini에게 결과 전달
            continue
        
        # 2. 도구 호출이 없으면 최종 답변으로 간주
        return content['parts'][0]['text']

    return "에이전트가 최대 시도 횟수를 초과했습니다."

def post_pull_request_review(repo, pr_number, token, review_data_str):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        review_data = json.loads(review_data_str)
        comments = []
        for r in review_data.get("reviews", []):
            comments.append({
                "path": r["path"],
                "line": int(r["line"]),
                "body": r["body"],
                "side": "RIGHT"
            })

        payload = {
            "body": f"### 🤖 Gemini 에이전트의 정밀 리뷰 (Step 2)\n\n{review_data.get('summary', '')}",
            "event": "COMMENT",
            "comments": comments
        }
        
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
    except Exception as e:
        post_fallback_comment(repo, pr_number, token, f"리뷰 등록 실패: {e}\n\n{review_data_str}")

def post_fallback_comment(repo, pr_number, token, body):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"body": body}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    repo = os.environ.get("REPO_NAME")
    pr_number = os.environ.get("PR_NUMBER")
    github_token = os.environ.get("GITHUB_TOKEN")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    try:
        print("🚀 Step 2: 에이전트 리뷰 시작...")
        diff = get_pr_diff(repo, pr_number, github_token)
        review_json = run_agent_loop(diff, gemini_api_key)
        post_pull_request_review(repo, pr_number, github_token, review_json)
        print("✅ 리뷰 완료!")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        sys.exit(1)
