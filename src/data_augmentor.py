import random
import os
import re

class DataAugmentor:
    def __init__(self, gazetteer_dir="gazetteers"):
        self.gazetteers = {}
        self.load_gazetteers(gazetteer_dir)

        # Templates for generating sentences
        # Keys match the gazetteer filenames
        self.templates = {
            'kisiler': [
                ("{x} bugün okula gitti.", "PER"),
                ("{x} yarın Ankara'ya gidecek.", "PER"),
                ("Dün {x} ile görüştüm.", "PER"),
                ("Sayın {x} açıklama yaptı.", "PER"),
            ],
            'yerler': [
                ("{x} çok güzel bir şehir.", "LOC"),
                ("Tatil için {x} bölgesine gidiyoruz.", "LOC"),
                ("{x} tarihi bir yerdir.", "LOC"),
                ("{x} başkentimizdir.", "LOC"),
            ],
            'sirketler': [
                ("{x} yeni telefonunu tanıttı.", "COMPANY"),
                ("{x} hisseleri yükseldi.", "COMPANY"),
                ("Babam {x} şirketinde çalışıyor.", "COMPANY"),
                ("{x} ile anlaşma imzalandı.", "COMPANY"),
            ],
            'kurumlar': [
                ("{x} burs başvurularını başlattı.", "ORG"),
                ("{x} toplantısı bugün yapıldı.", "ORG"),
                ("{x} insani yardım gönderdi.", "ORG"),
                ("{x} projeyi destekliyor.", "ORG"),
            ],
            'film_muzik': [
                ("{x} filmini çok beğendim.", "MOVIE"),
                ("{x} şarkısını dinliyorum.", "MOVIE"),
                ("Sinemada {x} izledik.", "MOVIE"),
                ("{x} albümü satışa çıktı.", "MOVIE"),
            ],
            'topluluklar': [
                ("{x} üye alımına başladı.", "GROUP"),
                ("{x} etkinlik düzenliyor.", "GROUP"),
                ("{x} başkanı konuştu.", "GROUP"),
                ("Okulda {x} kuruldu.", "GROUP"),
            ],
            # Mixed templates to help with entity separation
            'mixed': [
                ("{PER}, {MOVIE} şarkısını seslendirdi.", "MULTI"),
                ("{PER} ve {PER} {MOVIE} filminde başrol oynadı.", "MULTI"),
                # Diverse Templates
                ("{PER}, {MOVIE} şarkısını seslendirdi.", "MULTI"),
                ("{PER}’ın {MOVIE} filmi vizyona girdi.", "MULTI"),
                ("{PER}, {MOVIE} kitabını {LOC}’da yazdı.", "MULTI"),
                ("{PER}, {LOC}’da {MOVIE} konseri verdi.", "MULTI"),
                ("{GROUP} grubu {LOC} turnesine çıktı.", "MULTI"),
                ("{COMPANY} şirketi {LOC}’da yeni bir şube açtı.", "MULTI"),
                ("{PER}, {COMPANY}’nin yeni CEO’su oldu.", "MULTI"),
                ("{GROUP} ekibi {MOVIE} albümü için stüdyoya girdi.", "MULTI"),
                ("{PER} ve {GROUP} {LOC}’da beraber sahne aldı.", "MULTI"),
                ("{MOVIE} eseri {PER} tarafından kaleme alındı.", "MULTI"),
                ("{COMPANY}, {GROUP} kulübüne sponsor oldu.", "MULTI"),
                ("{PER}, {ORG} üniversitesinden mezun oldu.", "MULTI"),
                ("{ORG} derneği {LOC}’da yardım topladı.", "MULTI"),
                ("{GROUP} üyeleri {LOC} şehrinde konser verdi.", "MULTI"),
                ("{PER} {COMPANY} bünyesinde çalışıyor.", "MULTI"),
                ("{MOVIE} eseri {PER} tarafından yazıldı.", "MULTI"),
                ("{PER} {LOC} doğumludur.", "MULTI"),
                ("{COMPANY} yeni şubesini {LOC} lokasyonunda açtı.", "MULTI")
            ]
        }

    def load_gazetteers(self, gazetteer_dir):
        for filename in os.listdir(gazetteer_dir):
            if filename.endswith(".txt"):
                name = filename.replace(".txt", "")
                path = os.path.join(gazetteer_dir, filename)
                with open(path, "r", encoding="utf-8") as f:
                    self.gazetteers[name] = [line.strip() for line in f if line.strip()]

    def generate_sentence(self, category):
        """
        Generates a labeled sentence for a category or a mixed template.
        Returns: (tokens, tags)
        """
        if category not in self.templates:
            return None, None

        template, tag_type = random.choice(self.templates[category])

        # Mapping for mixed placeholders
        tag_map = {
            '{PER}': ('kisiler', 'PER'),
            '{LOC}': ('yerler', 'LOC'),
            '{MOVIE}': ('film_muzik', 'MOVIE'),
            '{COMPANY}': ('sirketler', 'COMPANY'),
            '{ORG}': ('kurumlar', 'ORG'),
            '{GROUP}': ('topluluklar', 'GROUP')
        }

        sentence = template
        entities_to_label = []

        if tag_type == "MULTI":
            # Find all placeholders
            placeholders = re.findall(r'\{[A-Z_]+\}', template)
            for ph in placeholders:
                if ph in tag_map:
                    gaz_name, t_type = tag_map[ph]
                    if self.gazetteers.get(gaz_name):
                        entity = random.choice(self.gazetteers[gaz_name])
                        # Replace first occurrence
                        sentence = sentence.replace(ph, entity, 1)
                        entities_to_label.append((entity, t_type))
        else:
            # Single entity case
            if category in self.gazetteers and self.gazetteers[category]:
                entity = random.choice(self.gazetteers[category])
                sentence = template.replace("{x}", entity)
                entities_to_label.append((entity, tag_type))

        if not entities_to_label:
            return None, None

        tokens = sentence.split()
        tags = ['O'] * len(tokens)

        # Label all entities in order
        search_start = 0
        for entity, t_type in entities_to_label:
            entity_tokens = entity.split()
            # Find subsequence match (ignoring trailing punctuation on tokens)
            for i in range(search_start, len(tokens) - len(entity_tokens) + 1):
                match = True
                for idx in range(len(entity_tokens)):
                    # Clean the token from punctuation for matching
                    clean_token = re.sub(r'[^\w\s]', '', tokens[i+idx])
                    clean_entity_token = re.sub(r'[^\w\s]', '', entity_tokens[idx])
                    if clean_token != clean_entity_token:
                        match = False
                        break

                if match:
                    tags[i] = f"B-{t_type}"
                    for j in range(1, len(entity_tokens)):
                        tags[i+j] = f"I-{t_type}"
                    search_start = i + len(entity_tokens)
                    break

        return tokens, tags

    def generate_dataset(self, n_samples=500):
        data = []
        for _ in range(n_samples):
            cat = random.choice(list(self.templates.keys()))
            tokens, tags = self.generate_sentence(cat)
            if tokens:
                data.append((tokens, tags))
        return data

if __name__ == "__main__":
    aug = DataAugmentor()
    dataset = aug.generate_dataset(5)
    for t, tags in dataset:
        print(list(zip(t, tags)))
