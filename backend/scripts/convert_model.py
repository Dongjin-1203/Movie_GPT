"""
Optimum을 사용한 감성 분석 모델 ONNX 변환 및 양자화

실행: python scripts/convert_model.py
"""

import os
from optimum.onnxruntime import ORTModelForSequenceClassification, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig
from transformers import AutoTokenizer
from pathlib import Path

# 설정
MODEL_NAME = "matthewburke/korean_sentiment"  # 또는 다른 감성 분석 모델
OUTPUT_DIR = Path("./app/models/sentiment")

def main():
    """메인 실행"""
    
    print("=" * 60)
    print("감성 분석 모델 변환 및 양자화")
    print("=" * 60)
    print(f"모델: {MODEL_NAME}")
    print(f"출력 경로: {OUTPUT_DIR}")
    
    # 출력 디렉토리 생성
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Step 1: ONNX 변환
    print("\n[1/3] ONNX 변환 중...")
    
    model = ORTModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        export=True  # Hugging Face → ONNX 자동 변환
    )
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    
    # 임시 저장
    temp_dir = OUTPUT_DIR / "temp"
    model.save_pretrained(temp_dir)
    tokenizer.save_pretrained(temp_dir)
    
    print("✅ ONNX 변환 완료!")
    
    # Step 2: 양자화
    print("\n[2/3] Dynamic Quantization 적용 중...")
    
    quantizer = ORTQuantizer.from_pretrained(temp_dir)
    
    # Dynamic Quantization 설정
    dqconfig = AutoQuantizationConfig.avx512_vnni(
        is_static=False,  # Dynamic Quantization
        per_channel=False
    )
    
    # 양자화 수행
    quantizer.quantize(
        save_dir=OUTPUT_DIR,
        quantization_config=dqconfig
    )
    
    # 토크나이저 복사
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print("✅ 양자화 완료!")
    
    # Step 3: 임시 파일 정리
    print("\n[3/3] 임시 파일 정리 중...")
    
    import shutil
    shutil.rmtree(temp_dir)
    
    print("✅ 정리 완료!")
    
    # Step 4: 파일 크기 확인
    print("\n" + "=" * 60)
    print("결과")
    print("=" * 60)
    
    onnx_file = OUTPUT_DIR / "model.onnx"
    quantized_file = OUTPUT_DIR / "model_quantized.onnx"
    
    if onnx_file.exists():
        original_size = onnx_file.stat().st_size / (1024 * 1024)
        print(f"원본 ONNX: {original_size:.2f} MB")
    
    if quantized_file.exists():
        quantized_size = quantized_file.stat().st_size / (1024 * 1024)
        print(f"양자화 모델: {quantized_size:.2f} MB")
        
        if onnx_file.exists():
            reduction = (1 - quantized_size / original_size) * 100
            print(f"크기 감소: {reduction:.1f}%")
    
    print(f"\n✅ 모든 파일이 저장되었습니다: {OUTPUT_DIR}")
    
    # Step 5: 간단한 테스트
    print("\n" + "=" * 60)
    print("테스트")
    print("=" * 60)
    
    test_inference()

def test_inference():
    """양자화 모델 테스트"""
    
    from transformers import pipeline
    
    print("\n테스트 문장으로 추론 중...")
    
    # 양자화 모델 로드
    model = ORTModelForSequenceClassification.from_pretrained(OUTPUT_DIR)
    tokenizer = AutoTokenizer.from_pretrained(OUTPUT_DIR)
    
    # Pipeline 생성
    classifier = pipeline(
        "sentiment-analysis",
        model=model,
        tokenizer=tokenizer
    )
    
    # 테스트
    test_cases = [
        "이 영화 정말 재미있어요! 강력 추천합니다.",
        "너무 지루하고 별로였어요. 시간 낭비.",
        "그냥 그래요. 나쁘지는 않지만 특별하지도 않아요."
    ]
    
    for text in test_cases:
        result = classifier(text)[0]
        label = result["label"]
        score = result["score"]
        
        print(f"\n문장: {text}")
        print(f"결과: {label} ({score:.2%})")

if __name__ == "__main__":
    main()