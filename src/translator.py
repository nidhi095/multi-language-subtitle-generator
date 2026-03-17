from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

model_name = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)


def translate_text(text, target_lang):

    lang_codes = {
        "hindi": "hin_Deva",
        "kannada": "kan_Knda",
        "english": "eng_Latn"
    }

    tokenizer.src_lang = "eng_Latn"

    encoded = tokenizer(text, return_tensors="pt")

    generated_tokens = model.generate(
        **encoded,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(
            lang_codes[target_lang]
        )
    )

    translated = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)

    return translated[0]
