"""
translator.py
-------------
Translates subtitle segments using Helsinki-NLP MarianMT models
(via HuggingFace Transformers). Falls back to Helsinki opus-mt models
for any language pair not directly available.
"""

from __future__ import annotations
from typing import Optional
import copy

from src.speech_to_text import Segment

# Map of language pairs to HuggingFace model identifiers.
# MarianMT covers most pairs; we try a direct route first,
# then pivot through English as an intermediary.
_DIRECT_MODELS: dict[tuple[str, str], str] = {
    ("en", "hi"): "Helsinki-NLP/opus-mt-en-hi",
    ("en", "es"): "Helsinki-NLP/opus-mt-en-es",
    ("en", "fr"): "Helsinki-NLP/opus-mt-en-fr",
    ("en", "de"): "Helsinki-NLP/opus-mt-en-de",
    ("en", "zh"): "Helsinki-NLP/opus-mt-en-zh",
    ("en", "ar"): "Helsinki-NLP/opus-mt-en-ar",
    ("en", "pt"): "Helsinki-NLP/opus-mt-en-ROMANCE",
    ("en", "ru"): "Helsinki-NLP/opus-mt-en-ru",
    ("en", "ja"): "Helsinki-NLP/opus-mt-en-jap",
    ("en", "ko"): "Helsinki-NLP/opus-mt-en-ko",
    ("en", "it"): "Helsinki-NLP/opus-mt-en-it",
    # Reverse pairs (non-English source → English)
    ("hi", "en"): "Helsinki-NLP/opus-mt-hi-en",
    ("es", "en"): "Helsinki-NLP/opus-mt-es-en",
    ("fr", "en"): "Helsinki-NLP/opus-mt-fr-en",
    ("de", "en"): "Helsinki-NLP/opus-mt-de-en",
    ("zh", "en"): "Helsinki-NLP/opus-mt-zh-en",
    ("ar", "en"): "Helsinki-NLP/opus-mt-ar-en",
    ("pt", "en"): "Helsinki-NLP/opus-mt-ROMANCE-en",
    ("ru", "en"): "Helsinki-NLP/opus-mt-ru-en",
    ("ja", "en"): "Helsinki-NLP/opus-mt-jap-en",
    ("ko", "en"): "Helsinki-NLP/opus-mt-ko-en",
    ("it", "en"): "Helsinki-NLP/opus-mt-it-en",
}

# Cache loaded pipelines to avoid reloading on repeated calls
_pipeline_cache: dict[str, object] = {}


def _get_pipeline(model_name: str):
    """Load (or retrieve cached) a HuggingFace translation pipeline."""
    from transformers import pipeline as hf_pipeline

    if model_name not in _pipeline_cache:
        print(f"        Loading model: {model_name}")
        _pipeline_cache[model_name] = hf_pipeline(
            "translation",
            model=model_name,
        )
    return _pipeline_cache[model_name]


def _translate_texts(
    texts: list[str],
    src_lang: str,
    tgt_lang: str,
    batch_size: int = 32,
) -> list[str]:
    """
    Translate a list of strings from src_lang to tgt_lang.
    Uses a pivot through English when no direct model exists.
    """
    if src_lang == tgt_lang:
        return texts

    pair = (src_lang, tgt_lang)

    if pair in _DIRECT_MODELS:
        pipe = _get_pipeline(_DIRECT_MODELS[pair])
        results = pipe(texts, batch_size=batch_size, max_length=512)
        return [r["translation_text"] for r in results]

    # Pivot: src → English → tgt
    en_pair_src = (src_lang, "en")
    en_pair_tgt = ("en", tgt_lang)

    if en_pair_src not in _DIRECT_MODELS or en_pair_tgt not in _DIRECT_MODELS:
        raise ValueError(
            f"No translation path found for {src_lang} → {tgt_lang}. "
            "Ensure both legs (src→en, en→tgt) are available."
        )

    print(f"        No direct model for {src_lang}→{tgt_lang}; pivoting via English.")
    pipe_to_en = _get_pipeline(_DIRECT_MODELS[en_pair_src])
    intermediate = pipe_to_en(texts, batch_size=batch_size, max_length=512)
    en_texts = [r["translation_text"] for r in intermediate]

    pipe_to_tgt = _get_pipeline(_DIRECT_MODELS[en_pair_tgt])
    final = pipe_to_tgt(en_texts, batch_size=batch_size, max_length=512)
    return [r["translation_text"] for r in final]


def translate_subtitles(
    segments: list[Segment],
    target_lang: str,
    source_lang: str = "en",
    batch_size: int = 32,
) -> list[Segment]:
    """
    Translate subtitle segments to target_lang.

    Args:
        segments: List of Segment objects with original text.
        target_lang: ISO-639-1 code of the desired language.
        source_lang: ISO-639-1 code of the source language.
        batch_size: Number of texts to translate at once.

    Returns:
        New list of Segment objects with translated text.
    """
    if source_lang == target_lang:
        return segments

    texts = [seg.text for seg in segments]
    translated_texts = _translate_texts(
        texts,
        src_lang=source_lang,
        tgt_lang=target_lang,
        batch_size=batch_size,
    )

    translated_segments = []
    for seg, translated_text in zip(segments, translated_texts):
        new_seg = copy.copy(seg)
        new_seg.text = translated_text
        translated_segments.append(new_seg)

    return translated_segments