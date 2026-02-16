import os

path = '/Users/drenbuqa/Library/CloudStorage/OneDrive-Personal/MeldPharm/BarnatoreMeldPharm-1/templates/index.html'
with open(path, 'r') as f:
    content = f.read()

# Define the blocks to remove
blocks = [
    """                    <div class="hero-content">
                        <div class="hero-text">
                            <span class="hero-label">SKIN CARE SPECIALIST</span>
                            <h1>Eucerin – Kujdesi i duhur për çdo lëkurë.</h1>
                            <p>Zbuloni fuqinë e dermatologjisë me Eucerin dhe rigjeni shkëlqimin.</p>
                            <div class="hero-cta">
                                <span class="btn-hero">Shiko Koleksionin <i class="fas fa-arrow-right"></i></span>
                            </div>
                        </div>
                    </div>""",
    """                    <div class="hero-content">
                        <div class="hero-text">
                            <span class="hero-label">LABORATOIRES VICHY</span>
                            <h1>Shëndeti është i bukur.</h1>
                            <p>Kujdes profesional për fytyrë dhe trup, i rekomanduar nga dermatologët.</p>
                            <div class="hero-cta">
                                <span class="btn-hero">Zbuloni Vichy <i class="fas fa-arrow-right"></i></span>
                            </div>
                        </div>
                    </div>""",
    """                    <div class="hero-content">
                        <div class="hero-text">
                            <span class="hero-label">DEVELOPED WITH DERMATOLOGISTS</span>
                            <h1>Hidratim që zgjat gjatë gjithë ditës.</h1>
                            <p>Me 3 ceramide esenciale për të ripërtërirë barrierën mbrojtëse të lëkurës.</p>
                            <div class="hero-cta">
                                <span class="btn-hero">Shiko Produktet <i class="fas fa-arrow-right"></i></span>
                            </div>
                        </div>
                    </div>"""
]

for block in blocks:
    content = content.replace(block, "")

with open(path, 'w') as f:
    f.write(content)

print("Successfully cleaned index.html")
