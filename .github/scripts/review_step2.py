import os
import sys
import requests
import json

def get_pr_diff(repo, pr_number, token):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

# --- AI가 사용할 도구(Tools) 정의 ---

def read_file(path):
    """지정한 경로의 파일 내용을 읽어옵니다."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file {path}: {str(e)}"

def list_files(directory="."):
    """지정한 디렉토리의 파일 및 폴더 목록을 확인합니다."""
    try:
        items = os.listdir(directory)
        result = []
        for item in items:
            if item.startswith('.') or item in ['build', 'gradle', '.gradle']:
                continue
            full_path = os.path.join(directory, item)
            if os.path.isdir(full_path):
                result.append(f"[DIR] {item}")
            else:
                result.append(f"[FILE] {item}")
        return "\n".join(sorted(result))
    except Exception as e:
        return f"Error listing directory {directory}: {str(e)}"

# 도구 명세 (Gemini에게 알려줄 함수 리스트)
TOOLS_SPEC = [
    {
        "name": "read_file",
        "description": "Read the content of a file in the repository to understand context or find line numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The full path to the file."}
            },
            "required": ["path"]
        }
    },
    {
        "name": "list_files",
        "description": "List files in the repository to find related classes or configurations.",
        "parameters": {
            "type": "object",
            "properties": {
                "directory": {"type": "string", "description": "The directory to list."}
            }
        }
    }
]

def get_gemini_review_with_tools(diff, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
    
    system_prompt = """
    너는 시니어 Java Spring 백엔드 엔지니어 에이전트야. 
    제공된 Git Diff를 분석하되, 정보가 부족하면 도구(tools)를 사용해 관련 파일이나 디렉토리 구조를 확인해.
    
    **너의 임무:**
    1. Diff를 보고 의심되는 부분(동시성, 성능, 캐시 등)을 찾아내.
    2. 도구를 사용해 해당 파일의 전체 내용을 읽어 정확한 맥락과 '실제 라인 번호'를 확인해.
    3. 최종 리뷰를 JSON 형식으로 작성해.
    
    **최종 응답 형식 (JSON):**
    {
      "summary": "총평",
      "reviews": [{"path": "파일경로", "line": 숫자, "body": "리뷰내용"}]
    }
    """

    # 대화 기록 (History) 관리
    messages = [
        {"role": "user", "parts": [{"text": system_prompt}, {"text": f"Here is the diff:

{diff}"}]}
    ]

    while True:
        payload = {
            "contents": messages,
            "tools": [{"function_declarations": TOOLS_SPEC}],
            "generationConfig": {"response_mime_type": "application/json"}
        }

        response = requests.post(url, json=payload)
        response.raise_for_status()
        result = response.json()
        
        part = result['candidates'][0]['content']['parts'][0]
        
        # 1. AI가 함수 호출(Function Call)을 요청한 경우
        if "functionCall" in part:
            call = part["functionCall"]
            func_name = call["name"]
            args = call.get("args", {})
            
            print(f"  [AI 요청] 함수 호출: {func_name}({args})")
            
            # 실제 함수 실행
            if func_name == "read_file":
                output = read_file(args.get("path"))
            elif func_name == "list_files":
                output = list_files(args.get("directory", "."))
            else:
                output = "Unknown function"

            # 실행 결과를 메시지 기록에 추가
            messages.append(result['candidates'][0]['content']) # AI의 호출 요청 추가
            messages.append({
                "role": "function",
                "parts": [{
                    "functionResponse": {
                        "name": func_name,
                        "response": {"name": func_name, "content": output}
                    }
                }]
            })
            continue # 다시 AI에게 질문 (결과를 보고 다음 판단을 하게 함)
            
        # 2. AI가 최종 답변(텍스트/JSON)을 준 경우
        else:
            return part["text"]

def post_pull_request_review(repo, pr_number, token, review_data_str):
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/vnd.github.v3+json"}
    
    try:
        review_data = json.loads(review_data_str)
        comments = []
        for r in review_data.get("reviews", []):
            comments.append({
                "path": r["path"], "line": int(r["line"]), "body": r["body"], "side": "RIGHT"
            })

        payload = {
            "body": f"### 🤖 Gemini 에이전트의 정밀 리뷰 (Step 2)

{review_data.get('summary', '')}",
            "event": "COMMENT",
            "comments": comments
        }
        
        requests.post(url, headers=headers, json=payload).raise_for_status()
        print("✅ Review posted successfully!")
    except Exception as e:
        print(f"Error: {e}
Fallback to general comment.")
        # Fallback 생략 (원리는 Step 1과 동일)

if __name__ == "__main__":
    repo, pr_num, g_token, gemini_key = os.environ.get("REPO_NAME"), os.environ.get("PR_NUMBER"), os.environ.get("GITHUB_TOKEN"), os.environ.get("GEMINI_API_KEY")

    if not all([repo, pr_num, g_token, gemini_key]):
        sys.exit(1)

    print("🚀 Step 2: Agentic Review Started...")
    diff = get_pr_diff(repo, pr_num, g_token)
    review_json = get_gemini_review_with_tools(diff, gemini_key)
    post_pull_request_review(repo, pr_num, g_token, review_json)
