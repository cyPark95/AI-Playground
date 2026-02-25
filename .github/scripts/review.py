import os
import sys
import requests
import json
import re

def get_pr_diff(repo, pr_number, token):
    """GitHub API를 통해 PR의 코드 변경 사항(Diff)을 가져옵니다."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3.diff"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def get_gemini_review(diff, api_key):
    """Gemini API를 호출하여 구조화된 코드 리뷰를 요청합니다."""
    # 모델명은 안정적인 gemini-1.5-pro-latest를 권장합니다.
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
    
    system_prompt = """
    너는 시니어 Java Spring 백엔드 엔지니어 기술 면접관이자 멘토야. 
    제공되는 Git Diff를 분석하여 리뷰를 남겨줘.
    
    **중요 지침:**
    1. 답변은 반드시 아래의 JSON 형식으로만 작성해줘. 다른 설명은 생략해.
    2. 'reviews' 배열에는 코드의 특정 라인에 대한 구체적인 피드백을 담아줘.
    3. 'path'는 파일의 전체 경로를 사용해.
    4. 'line'은 해당 코드가 위치한 파일의 실제 줄 번호(숫자)를 적어줘. (Diff 내용을 분석해서 유추해줘)
    5. 'body'는 친절하지만 명확한 한국어로 작성하고, 개선 코드가 있다면 마크다운 형식을 사용해.
    
    **응답 형식 예시:**
    {
      "summary": "전체적인 코드 품질에 대한 총평",
      "reviews": [
        {
          "path": "src/main/java/.../ProductService.java",
          "line": 25,
          "body": "이 부분은 동시성 문제가 발생할 수 있습니다. `@Lock` 사용을 고려해보세요."
        }
      ]
    }
    
    **집중 리뷰 포인트:**
    - 대용량 데이터 처리 병목 (findAll 지양)
    - 동시성 제어 및 스레드 안전성
    - DB 쿼리 최적화 및 인덱스 활용
    - Redis 캐시 정합성
    - 클린 코드 및 아키텍처 원칙
    """
    
    payload = {
        "contents": [{
            "parts": [
                {"text": system_prompt},
                {"text": f"Here is the code diff:\n\n{diff}"}
            ]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }
    
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
    response.raise_for_status()
    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']

def post_pull_request_review(repo, pr_number, token, review_data_str):
    """리뷰 결과를 PR의 Line-by-line 리뷰로 등록합니다."""
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    try:
        # AI 응답에서 JSON 블록만 추출 (혹시 모를 텍스트 혼입 대비)
        review_data = json.loads(review_data_str)
        
        # GitHub API 형식으로 변환
        comments = []
        for r in review_data.get("reviews", []):
            comments.append({
                "path": r["path"],
                "line": int(r["line"]),
                "body": r["body"],
                "side": "RIGHT" # 새롭게 추가된 코드 쪽에 코멘트
            })

        payload = {
            "body": f"### 🤖 Gemini 시니어 엔지니어의 리뷰\n\n{review_data.get('summary', '')}",
            "event": "COMMENT",
            "comments": comments
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 201:
            print(f"Failed to post review: {response.text}")
        response.raise_for_status()
        
    except Exception as e:
        print(f"Error parsing or posting review: {e}")
        # 실패 시 일반 코멘트로라도 남기기 (Fallback)
        post_fallback_comment(repo, pr_number, token, review_data_str)

def post_fallback_comment(repo, pr_number, token, body):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"body": f"### ⚠️ Line-by-line 리뷰 생성 실패\n\n{body}"}
    requests.post(url, headers=headers, json=payload)

if __name__ == "__main__":
    repo = os.environ.get("REPO_NAME")
    pr_number = os.environ.get("PR_NUMBER")
    github_token = os.environ.get("GITHUB_TOKEN")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if not all([repo, pr_number, github_token, gemini_api_key]):
        print("Missing environment variables.")
        sys.exit(1)

    try:
        print("1. Fetching Diff...")
        diff = get_pr_diff(repo, pr_number, github_token)
        
        print("2. Requesting Structured Review from Gemini...")
        review_json = get_gemini_review(diff, gemini_api_key)
        
        print("3. Posting Line-by-line Review to GitHub...")
        post_pull_request_review(repo, pr_number, github_token, review_json)
        
        print("✅ Success!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
