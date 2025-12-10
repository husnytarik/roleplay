import json
import random

STORY_FILE = "story.json"  # İstersen adı story.txt de olabilir, içerik aynı.

def roll_dice(dice_spec: str) -> int:
    """
    dice_spec örnekleri:
    - "d6"  -> 1d6
    - "1d6" -> 1d6
    - "2d6" -> 2d6 (ileride kullanmak istersen)
    """
    spec = dice_spec.lower().strip()
    if spec.startswith("d"):
        count = 1
        sides = int(spec[1:])
    else:
        parts = spec.split("d")
        if len(parts) != 2:
            raise ValueError(f"Geçersiz zar formatı: {dice_spec}")
        count = int(parts[0])
        sides = int(parts[1])

    total = 0
    for _ in range(count):
        total += random.randint(1, sides)
    return total


def load_story(path: str):
    """
    story.json dosyasını okur ve adım listesini döndürür.
    Dosya JSON formatında:
    [
      { ...1. adım... },
      { ...2. adım... },
      ...
    ]
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Basit kontrol
    if not isinstance(data, list):
        raise ValueError("Hikaye dosyası bir liste (array) olmalı.")

    return data


def print_separator():
    print("\n" + "-" * 60 + "\n")


def play_step(step: dict):
    """
    Tek bir adımı (step) oynatır.
    step örnek yapısı:
    {
      "id": 1,
      "title": "Başlık",
      "text": "Uzun açıklama...",
      "type": "roll" / "choice" / "narrative" / "end",
      ...
    }
    """
    print_separator()
    title = step.get("title", "Bilinmeyen Bölge")
    text = step.get("text", "")

    print(f"🛰  {title}")
    print()
    print(text)
    print()

    step_type = step.get("type", "narrative")

    # Sadece metin, devam etmek için Enter
    if step_type == "narrative":
        input("Devam etmek için Enter'a bas...")
        return

    # Seçenekli soru
    if step_type == "choice":
        choices = step.get("choices", [])
        if not choices:
            print("Bu 'choice' adımında hiç seçenek tanımlı değil.")
            input("Devam etmek için Enter'a bas...")
            return

        # Seçenekleri göster
        for ch in choices:
            key = ch.get("key", "?")
            text = ch.get("text", "")
            print(f"  {key}) {text}")

        # Kullanıcıdan cevap al
        valid_keys = [c.get("key", "").upper() for c in choices]
        answer = None
        while answer not in valid_keys:
            answer = input("\nSeçimin (ör: A): ").strip().upper()
            if answer not in valid_keys:
                print("Geçersiz seçim, tekrar dene.")

        # Seçime özel mesaj varsa göster
        for ch in choices:
            if ch.get("key", "").upper() == answer:
                result_text = ch.get("result_text")
                if result_text:
                    print()
                    print(result_text)
                break

        input("\nDevam etmek için Enter'a bas...")
        return

    # Zar atmalı adım
    if step_type == "roll":
        dice_spec = step.get("dice", "d6")   # varsayılan d6
        target = step.get("target", 4)       # varsayılan hedef 4
        success_text = step.get("success_text", "Görev başarılı!")
        fail_text = step.get("fail_text", "Görev başarısız, geri çekiliyorsun.")

        print(f"Bu adımda zar atman gerekiyor. ({dice_spec}, hedef: ≥ {target})")
        user_input = input("Gerçek zarın varsa atıp sonucu yaz, yoksa Enter'a basınca ben atacağım: ").strip()

        if user_input.isdigit():
            roll = int(user_input)
            print(f"Senin yazdığın zar sonucu: {roll}")
        else:
            roll = roll_dice(dice_spec)
            print(f"Ben senin için attım, sonuç: {roll}")

        if roll >= target:
            print()
            print("✅ BAŞARI!")
            print(success_text)
        else:
            print()
            print("❌ BAŞARISIZLIK!")
            print(fail_text)

        input("\nDevam etmek için Enter'a bas...")
        return

    # Oyun sonu adımı
    if step_type == "end":
        input("Senaryonun sonuna geldin. Çıkmak için Enter'a bas...")
        return

    # Tanınmayan tip
    print(f"Tanınmayan adım tipi: {step_type}")
    input("Devam etmek için Enter'a bas...")


def main():
    print("=== GALAKSİ ÇATIŞMASI: ZETA PRİMUS GÜNLÜKLERİ ===")
    print("3 farklı galaksiden gelen güçlerin işgal ettiği bir gezegendesin.")
    print("Farklı bölgelerde görevler alacak bir ajanı oynuyorsun.")
    input("\nBaşlamak için Enter'a bas...")

    try:
        story = load_story(STORY_FILE)
    except Exception as e:
        print(f"Hikaye dosyası okunurken hata oluştu: {e}")
        print("Lütfen story.json dosyasını kontrol et.")
        return

    # Sıralı oynatıyoruz. İleride id bazlı dallanma da eklenebilir.
    for step in story:
        play_step(step)
        # type=end ise yine de döngü devam eder ama genelde end sona konur.

    print_separator()
    print("Senaryo bitti. Yeni görevler için story.json dosyasını güncelleyebilirsin.")
    print("Oynamak için programı yeniden çalıştırman yeterli.")


if __name__ == "__main__":
    main()
