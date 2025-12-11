import json
import random
import os


# =====================================================
# Zar fonksiyonu
# =====================================================
def roll_dice(dice_spec: str) -> int:
    """
    dice_spec örnekleri:
    - "d6"   -> 1d6
    - "1d6"  -> 1d6
    - "2d6"  -> 2d6
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


# =====================================================
# Senaryo dosyası seçimi
# =====================================================
def choose_story_file() -> str:
    """
    Çalıştığın klasördeki .json dosyalarını listeler
    ve numara ile seçmeni sağlar.
    """
    files = [f for f in os.listdir(".") if f.lower().endswith(".json")]
    files.sort()

    if not files:
        print("Bu klasörde hiç .json senaryo dosyası yok!")
        raise FileNotFoundError("Hiç .json bulunamadı")

    print("\n=== Senaryo Seç ===")
    for i, name in enumerate(files, start=1):
        print(f"{i}) {name}")

    default_idx = None
    if "story.json" in files:
        default_idx = files.index("story.json") + 1
        print(f"\nEnter'a basarsan varsayılan: {default_idx}) story.json kullanılacak.")
    else:
        print(f"\nBir numara gir (1–{len(files)}):")

    while True:
        choice = input("Senaryo numarası: ").strip()

        if not choice:
            if default_idx:
                chosen = files[default_idx - 1]
                print(f"\n→ Varsayılan senaryo seçildi: {chosen}\n")
                return chosen
            else:
                print("Varsayılan yok, lütfen bir numara gir.")
                continue

        if not choice.isdigit():
            print("Lütfen bir sayı gir.")
            continue

        num = int(choice)
        if 1 <= num <= len(files):
            chosen = files[num - 1]
            print(f"\n→ Seçilen senaryo: {chosen}\n")
            return chosen
        else:
            print("Geçersiz numara.")


# =====================================================
# JSON senaryo yükleme (start + nodes formatı)
# =====================================================
def load_story_with_nodes(path: str):
    """
    Beklenen format:
    {
      "start": "intro_orbit",
      "nodes": [
        { "id": "intro_orbit", "type": "narrative", ... },
        ...
      ]
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        # Eski tip liste formatı ise:
        raise ValueError(
            "Bu motor 'start' ve 'nodes' içeren JSON bekliyor.\n"
            'Örn: { "start": "intro", "nodes": [ {...}, ... ] }'
        )

    if "nodes" not in data:
        raise ValueError("JSON içinde 'nodes' alanı yok.")

    nodes = data["nodes"]
    start_id = data.get("start")
    if not start_id and nodes:
        start_id = nodes[0].get("id")

    if not start_id:
        raise ValueError("'start' id'si bulunamadı.")

    node_map = {}
    for node in nodes:
        node_id = node.get("id")
        if node_id:
            node_map[node_id] = node

    return start_id, node_map


def print_separator():
    print("\n" + "=" * 60 + "\n")


# =====================================================
# Tek node oynatma
# =====================================================
def play_node(node_id: str, node_map: dict) -> str | None:
    """
    Tek bir nodu oynatır ve bir SONRAKİ node id'si döndürür.
    None dönerse oyun biter.
    """
    if node_id not in node_map:
        print_separator()
        print(f"Geçersiz node id: {node_id}")
        input("Devam etmek için Enter'a bas...")
        return None

    node = node_map[node_id]
    node_type = (node.get("type") or "narrative").lower()

    title = node.get("title", node_id)
    text = node.get("text", "")

    print_separator()
    print(f"🛰  {title}")
    print()
    print(text)
    print()

    # --------------------------------------------
    # NARRATIVE
    # --------------------------------------------
    if node_type == "narrative":
        input("Devam etmek için Enter'a bas...")
        next_id = node.get("next")
        return next_id

    # --------------------------------------------
    # CHOICE
    # --------------------------------------------
    if node_type == "choice":
        choices = node.get("choices", [])
        if not choices:
            print("Bu 'choice' node'unda hiç seçenek yok.")
            input("Devam etmek için Enter'a bas...")
            return node.get("next")

        for ch in choices:
            key = ch.get("key", "?")
            txt = ch.get("text", "")
            print(f"  {key}) {txt}")

        picked_choice = None
        while True:
            answer = input("\nSeçimini gir (ör: A, B, C): ").strip().upper()
            if not answer:
                print("Boş bırakamazsın.")
                continue

            # Geçerli mi?
            for ch in choices:
                if ch.get("key", "").upper() == answer:
                    picked_choice = ch
                    break

            if picked_choice is None:
                print("Geçersiz seçenek. Tekrar dene.")
            else:
                break

        # Sonucu yaz
        result_text = picked_choice.get("result_text")
        if result_text:
            print()
            print(result_text)
            print()

        input("Devam etmek için Enter'a bas...")

        next_id = picked_choice.get("next") or node.get("next")
        return next_id

    # --------------------------------------------
    # ROLL
    # --------------------------------------------
    if node_type == "roll":
        dice_spec = node.get("dice", "d6")
        target = node.get("target", 4)
        success_text = node.get("success_text", "")
        fail_text = node.get("fail_text", "")

        print(f"Bu adımda zar atman gerekiyor. ({dice_spec}, hedef: ≥ {target})")
        yazilan = input(
            "Gerçek zarın varsa sonucu yaz, yoksa Enter'a bas; ben atayım: "
        ).strip()

        if yazilan.isdigit():
            roll = int(yazilan)
            print(f"Senin yazdığın zar sonucu: {roll}")
        else:
            roll = roll_dice(dice_spec)
            print(f"Ben senin için attım, sonuç: {roll}")

        success = roll >= target
        print()
        if success:
            print("✅ BAŞARI!")
            if success_text:
                print(success_text)
        else:
            print("❌ BAŞARISIZLIK!")
            if fail_text:
                print(fail_text)

        print()
        input("Devam etmek için Enter'a bas...")

        if success:
            next_id = node.get("next_success") or node.get("next")
        else:
            next_id = node.get("next_fail") or node.get("next")

        return next_id

    # --------------------------------------------
    # END
    # --------------------------------------------
    if node_type == "end":
        ending_key = node.get("ending_key")
        if ending_key:
            print(f"\n★ SON: {ending_key}")
        input("\nSenaryonun sonuna geldin. Çıkmak için Enter'a bas...")
        return None

    # --------------------------------------------
    # Bilinmeyen tip
    # --------------------------------------------
    print(f"Tanınmayan node tipi: {node_type}")
    input("Devam etmek için Enter'a bas...")
    return None


# =====================================================
# Ana fonksiyon
# =====================================================
def main():
    print("=== ZETA PRIMUS – JSON TABANLI ROLEPLAY OYUNU ===")
    print(
        "JSON içindeki 'start' ve 'nodes' yapısını okuyup dallanan senaryolar oynatırım."
    )
    print()

    try:
        story_file = choose_story_file()
    except Exception as e:
        print(f"\nSenaryo seçerken hata: {e}")
        return

    print(f"Seçilen senaryo dosyası: {story_file}")
    input("Senaryoyu yüklemek ve oyuna başlamak için Enter'a bas...")

    try:
        start_id, node_map = load_story_with_nodes(story_file)
    except Exception as e:
        print(f"\nSenaryo yüklenirken hata: {e}")
        return

    print(f"\nBaşlangıç nodu: {start_id}")
    current_id = start_id

    while current_id is not None:
        current_id = play_node(current_id, node_map)

    print_separator()
    print("Oyun bitti. Farklı seçimler ve zarlarla başka yollar deneyebilirsin.")
    print(f"Kullanılan senaryo: {story_file}")
    print("Tekrar oynamak için programı yeniden çalıştırman yeterli.")


if __name__ == "__main__":
    main()
