"""
FastAPI 백엔드와 통신하는 모든 함수 모음

구현할 함수:
1. get_all_movies()      - 전체 영화 목록 조회
2. get_movie(movie_id)   - 특정 영화 조회
3. create_movie(data)    - 영화 추가
4. delete_movie(movie_id) - 영화 삭제
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()

# FastAPI 백엔드의 기본 URL
base_url = os.getenv("BASE_URL")

class MovieAPIClient:
    """FastAPI 백엔드와 통신하는 클래스"""

    def __init__(self, base_url):
        self.base_url = base_url

    def get_all_movies(self):
        """전체 영화 목록 조회"""
        try:
            response = requests.get(f"{self.base_url}/movies/")
            if response.status_code == 200:
                return response.json()
            else:
                return []
        except requests.RequestException as e:
            print(f"Error fetching all movies: {e}")
            return []

    def get_movie(self, movie_id: int):
        """특정 영화 조회"""
        try:
            response = requests.get(f"{self.base_url}/movies/{movie_id}")
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except requests.RequestException as e:
            print(f"Error fetching movie {movie_id}: {e}")
            return None

    def create_movie(self, movie_data: dict):
        """영화 추가"""
        try:
            response = requests.post(f"{self.base_url}/movies/", json=movie_data)
            if response.status_code == 201:
                return response.json()
            else:
                return None
        except requests.RequestException as e:
            print(f"Error creating movie: {e}")
            return None
        

    def delete_movie(self, movie_id: int):
        """영화 삭제"""
        try:
            response = requests.delete(f"{self.base_url}/movies/{movie_id}")
            if response.status_code == 200:
                return True
            else:
                return False
        except requests.RequestException as e:
            print(f"Error deleting movie {movie_id}: {e}")
            return False
        
    # ======= 리뷰 관련 메서드 =======
    def create_review(self, review_data: dict):
        """리뷰 작성"""
        try:
            response = requests.post(
                f"{self.base_url}/reviews/",
                json=review_data
            )
            
            if response.status_code == 201:
                return response.json()
            else:
                return None
        
        except Exception as e:
            print(f"Error creating review: {e}")
            return None
        
    def get_all_reviews(self, limit: int = 10):
        """최근 리뷰 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/reviews/",
                params={"limit": limit}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
        
        except Exception as e:
            print(f"Error fetching reviews: {e}")
            return []
    
    def get_movie_reviews(self, movie_id: int):
        """특정 영화 리뷰 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/reviews/movie/{movie_id}"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
        
        except Exception as e:
            print(f"Error fetching movie reviews: {e}")
            return []
        
    def delete_review(self, review_id: int):
        """리뷰 삭제"""
        try:
            response = requests.delete(
                f"{self.base_url}/reviews/{review_id}"
            )
            
            if response.status_code == 200:
                return True
            else:
                return False
        
        except Exception as e:
            print(f"Error deleting review: {e}")
            return False

    def get_movie_rating(self, movie_id: int):
        """영화 평균 평점 조회"""
        try:
            response = requests.get(
                f"{self.base_url}/reviews/movie/{movie_id}/rating"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        
        except Exception as e:
            print(f"Error fetching rating: {e}")
            return None

client = MovieAPIClient(base_url)