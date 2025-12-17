from optimum.onnxruntime import ORTModelForSequenceClassification
from transformers import AutoTokenizer, pipeline

# 모델 경로
MODEL_DIR = "app/models/sentiment"

# 전역 변수 (Lazy Loading)
sentiment_pipeline = None

def get_sentiment_analyzer():
    """감성 분석 파이프라인 로드 (한 번만 실행)"""
    global sentiment_pipeline
    
    if sentiment_pipeline is None:
        print("📦 감성 분석 모델 로드 중...")
        
        try:
            # ONNX 모델 로드
            model = ORTModelForSequenceClassification.from_pretrained(MODEL_DIR)
            tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
            
            # Pipeline 생성
            sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=model,
                tokenizer=tokenizer
            )
            
            print("✅ 감성 분석 모델 로드 완료!")
            
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
            raise e
    
    return sentiment_pipeline

def analyze_sentiment(text: str):
    """텍스트 감성 분석"""
    
    try:
        # 입력 검증
        if not text or len(text.strip()) < 5:
            return {
                "label": "neutral",
                "score": 0.5
            }
        
        # 분석기 로드
        analyzer = get_sentiment_analyzer()
        
        # 텍스트 길이 제한 (512자)
        text = text[:512]
        
        # 감성 분석 수행
        result = analyzer(text)[0]
        
        # 결과 처리
        raw_label = result["label"]
        score = result["score"]
        
        # 라벨 정규화 (모델에 따라 다를 수 있음)
        label = normalize_label(raw_label)
        
        return {
            "label": label,
            "score": float(score)
        }
    
    except Exception as e:
        print(f"❌ 감성 분석 에러: {e}")
        # 에러 시 중립 반환
        return {
            "label": "neutral",
            "score": 0.5
        }
    
def normalize_label(raw_label: str):
    """모델 출력 라벨을 정규화"""
    
    label_lower = raw_label.lower()
    
    # 긍정 패턴
    if label_lower in ["positive", "pos", "1", "긍정", "label_1"]:  # ← label_1 추가됨
        return "positive"
    
    # 부정 패턴
    elif label_lower in ["negative", "neg", "0", "부정", "label_0"]:  # ← label_0 추가됨
        return "negative"
    
    # 기타
    else:
        return "neutral"