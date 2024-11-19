
target_horizontal = (1920, 1080)
target_vertical = (1080, 1920)

default_sharpness_threshold = 100.0

default_thresholds_exposure = { 
        "overexposed_threshold": 245,  # Límite para considerar un píxel como sobreexpuesto
        "underexposed_threshold": 10,  # Límite para considerar un píxel como subexpuesto
        "tolerance": 0.1  # Proporción máxima permitida para que sea válida
    }

block_size = 32

score_high_niqe = 3
score_medium_niqe = 5.5

score_high_piqa = 10
score_medium_piqa = 20