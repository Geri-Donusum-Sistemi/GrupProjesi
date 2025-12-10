from app import app, db, Quiz

def create_sample_quiz():
    with app.app_context():
        # Önce mevcut soruları temizle
        Quiz.query.delete()
        
        # 10 adet geri dönüşüm sorusu
        questions = [
            {
                "question": "Plastik şişeler hangi renkli geri dönüşüm kutusuna atılmalıdır?",
                "option_a": "Mavi kutu",
                "option_b": "Yeşil kutu",
                "option_c": "Kırmızı kutu",
                "option_d": "Sarı kutu",
                "correct_answer": "A"
            },
            {
                "question": "Cam şişeler hangi renkli geri dönüşüm kutusuna atılmalıdır?",
                "option_a": "Mavi kutu",
                "option_b": "Yeşil kutu",
                "option_c": "Kırmızı kutu",
                "option_d": "Turuncu kutu",
                "correct_answer": "B"
            },
            {
                "question": "Organik atıklar (meyve kabuğu, sebze artıkları) hangi kutuya atılır?",
                "option_a": "Mavi kutu",
                "option_b": "Yeşil kutu",
                "option_c": "Kahverengi kutu",
                "option_d": "Gri kutu",
                "correct_answer": "C"
            },
            {
                "question": "Kağıt ve karton atıklar hangi kutuya atılmalıdır?",
                "option_a": "Mavi kutu",
                "option_b": "Yeşil kutu",
                "option_c": "Kırmızı kutu",
                "option_d": "Siyah kutu",
                "correct_answer": "A"
            },
            {
                "question": "Hangi atık türü geri dönüşüme uygun DEĞİLDİR?",
                "option_a": "Temiz plastik şişe",
                "option_b": "Yağlı pizza kutusu",
                "option_c": "Alüminyum konserve kutusu",
                "option_d": "Gazete kağıdı",
                "correct_answer": "B"
            },
            {
                "question": "Pil ve elektronik atıklar hangi renkli kutuya atılmalıdır?",
                "option_a": "Mavi kutu",
                "option_b": "Kırmızı kutu",
                "option_c": "Turuncu kutu",
                "option_d": "Yeşil kutu",
                "correct_answer": "B"
            },
            {
                "question": "1 ton kağıt geri dönüştürülerek kaç ağaç kurtarılır?",
                "option_a": "5-10 ağaç",
                "option_b": "17-20 ağaç",
                "option_c": "30-35 ağaç",
                "option_d": "50-60 ağaç",
                "correct_answer": "B"
            },
            {
                "question": "Hangi plastik türü en çok geri dönüştürülebilir?",
                "option_a": "PET (1 numaralı)",
                "option_b": "PVC (3 numaralı)",
                "option_c": "PS (6 numaralı)",
                "option_d": "Diğer (7 numaralı)",
                "correct_answer": "A"
            },
            {
                "question": "Cam geri dönüştürüldüğünde özelliklerini kaybeder mi?",
                "option_a": "Evet, her defasında kalitesi düşer",
                "option_b": "Hayır, sonsuz kez geri dönüştürülebilir",
                "option_c": "Sadece 5 kez geri dönüştürülebilir",
                "option_d": "Geri dönüştürülemez",
                "correct_answer": "B"
            },
            {
                "question": "Alüminyum kutu geri dönüştürüldüğünde ne kadar enerji tasarrufu sağlanır?",
                "option_a": "%30",
                "option_b": "%50",
                "option_c": "%75",
                "option_d": "%95",
                "correct_answer": "D"
            }
        ]
        
        # Soruları veritabanına ekle
        for q_data in questions:
            question = Quiz(
                question=q_data["question"],
                option_a=q_data["option_a"],
                option_b=q_data["option_b"],
                option_c=q_data["option_c"],
                option_d=q_data["option_d"],
                correct_answer=q_data["correct_answer"]
            )
            db.session.add(question)
        
        db.session.commit()
        print("✅ 10 adet quiz sorusu başarıyla oluşturuldu!")

if __name__ == "__main__":
    create_sample_quiz()
