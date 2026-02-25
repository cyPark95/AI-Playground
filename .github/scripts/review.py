import os
import sys
import requests
import json

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
    """Gemini API를 호출하여 코드 리뷰를 요청합니다."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={api_key}"
    
    # 💡 시스템 프롬프트: 개발 환경에 맞게 AI의 페르소나와 집중 리뷰 포인트를 설정합니다.
    system_prompt = """
    너는 시니어 Java Spring 백엔드 엔지니어 기술 면접관이자 멘토야. 
    아래 제공되는 Git Diff 형식의 코드 변경 사항을 꼼꼼하게 리뷰해 줘.
    
    특히 다음 사항들을 집중적으로 확인해 줘:
    1. 대용량 데이터 처리 시 발생할 수 있는 병목 현상 (Spring Batch 청크 최적화 등)
    2. 동시성 제어 및 멀티프로세싱/멀티태스킹 환경에서의 스레드 안전성(Thread Safety)
    3. MySQL 복잡한 쿼리의 성능 최적화 여부
    4. Redis 캐시 사용 시 발생할 수 있는 데이터 정합성 문제
    5. 전반적인 아키텍처 관점에서의 개선점과 클린 코드 여부
    
    친절하지만 명확하고, 개선이 필요한 코드는 구체적인 예시 코드와 함께 한국어로 답변해 줘.
    """
    
    payload = {
        "contents": [{
            "parts": [
                {"text": system_prompt},
                {"text": f"Here is the code diff:\n\n{diff}"}
            ]
        }]
    }
    
    response = requests.post(url, headers={"Content-Type": "application/json"}, json=payload)
    response.raise_for_status()
    result = response.json()
    return result['candidates'][0]['content']['parts'][0]['text']

def post_comment_to_pr(repo, pr_number, token, comment):
    """리뷰 결과를 PR의 코멘트로 등록합니다."""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    payload = {"body": f"### 🤖 Gemini 자동 코드 리뷰\n\n{comment}"}
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

if __name__ == "__main__":
    repo = os.environ.get("REPO_NAME")
    pr_number = os.environ.get("PR_NUMBER")
    github_token = os.environ.get("GITHUB_TOKEN")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")

    if not all([repo, pr_number, github_token, gemini_api_key]):
        print("Missing required environment variables.")
        sys.exit(1)

    try:
        print("1. Fetching PR Diff...")
        diff = get_pr_diff(repo, pr_number, github_token)
        
        # 변경 사항이 너무 길면 자르거나 처리하는 로직을 추가할 수 있습니다.
        # if len(diff) > 30000:
        #     diff = diff[:30000] + "\n... (Diff truncated due to length)"

        print("2. Requesting review from Gemini...")
        review_comment = get_gemini_review(diff, gemini_api_key)
        
        print("3. Posting comment to PR...")
        post_comment_to_pr(repo, pr_number, github_token, review_comment)
        
        print("✅ Review completed successfully!")
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        sys.exit(1)
