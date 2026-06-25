import re
from collections import OrderedDict
from typing import List

import requests

from app.core.config import settings
from app.services.feedback_service import PromptEnhancement

# Old local-model backend (flan-t5-small via HuggingFace transformers).
# Replaced by the DeepSeek API below. Left here in case we ever want to
# fall back to a local model.
# from transformers import pipeline


DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"


class NLPService:
    """Study generation using the DeepSeek chat completions API."""

    def __init__(self) -> None:
        # self._pipe = None
        pass

    # def _load_pipe(self):
    #     if self._pipe is None:
    #         self._pipe = pipeline(
    #             "text2text-generation",
    #             model=settings.hf_summarizer_model,
    #         )
    #     return self._pipe

    # ── Text utilities ────────────────────────────────────────────────

    def split_sentences(self, text):
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def clean_study_text(self, text):
        cleaned = re.sub(r"^\s*Note title:\s*.+?$", "", text, flags=re.MULTILINE)
        cleaned = re.sub(r"^\s*Source file:\s*.+?$", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"^\s*Study content:\s*", "", cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r"\n{2,}", "\n", cleaned)
        return cleaned.strip()

    def assess_text_quality(self, text, purpose="summary"):
        cleaned = self.clean_study_text(text)
        words = re.findall(r"\b[\w'-]+\b", cleaned)
        if len(words) < 8:
            return f"Please provide more text to generate a {purpose}."
        alpha = re.findall(r"\b[a-zA-Z]{3,}\b", cleaned)
        if len(alpha) < 5:
            return f"The text is too unclear to build a useful {purpose}."
        return None

    def chunk_text(self, text, max_chars=800):
        """Smaller chunks so flan-t5-small doesn't get overwhelmed."""
        sentences = self.split_sentences(self.clean_study_text(text))
        chunks, current, size = [], [], 0
        for s in sentences:
            if current and size + len(s) > max_chars:
                chunks.append(" ".join(current))
                current, size = [s], len(s)
            else:
                current.append(s)
                size += len(s)
        if current:
            chunks.append(" ".join(current))
        return chunks

    def select_key_sentences(self, text, limit=5):
        sentences = self.split_sentences(self.clean_study_text(text))
        filtered = [s for s in sentences if len(s.split()) >= 6]
        return filtered[:limit] or sentences[:limit]

    def extract_keywords(self, text, limit=8):
        stopwords = {
            "the","and","is","in","to","of","a","for","that","with","on","as",
            "are","it","an","by","be","this","from","or","at","can","into",
            "about","their","these","those","which","study","content","note",
            "will","also","have","has","been","they","were","was","had",
        }
        words = re.findall(r"\b[a-zA-Z]{4,}\b", self.clean_study_text(text).lower())
        counts = {}
        for w in words:
            if w not in stopwords:
                counts[w] = counts.get(w, 0) + 1
        ranked = sorted(counts.items(), key=lambda x: (x[1], len(x[0])), reverse=True)
        return [w for w, _ in ranked[:limit]]

    def deduplicate_lines(self, lines):
        seen = OrderedDict()
        for line in lines:
            key = re.sub(r"[^a-z0-9]+", " ", line.lower()).strip()
            if key and key not in seen:
                seen[key] = line.strip()
        return list(seen.values())

    def simplify_sentence(self, sentence):
        simplified = sentence.strip()
        replacements = {
            "therefore": "so", "however": "but", "utilize": "use",
            "demonstrates": "shows", "approximately": "about",
            "numerous": "many", "individuals": "people",
            "significant": "important", "consequently": "as a result",
            "facilitate": "help", "subsequent": "later",
            "prior to": "before", "obtain": "get", "commence": "start",
        }
        for hard, easy in replacements.items():
            simplified = re.sub(rf"\b{hard}\b", easy, simplified, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", simplified).strip()

    # ── Model generation ──────────────────────────────────────────────

    def _generate(self, prompt, max_new_tokens=120):
        """Call the DeepSeek chat completions API for text generation."""
        if not settings.deepseek_api_key:
            return ""
        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers={
                    "Authorization": f"Bearer {settings.deepseek_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.deepseek_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_new_tokens,
                    "temperature": 0.3,
                },
                timeout=30,
            )
            response.raise_for_status()
            raw = response.json()["choices"][0]["message"]["content"].strip()
            if len(raw) > 20 and raw.lower().startswith(prompt[:30].lower()):
                return ""
            return raw
        except Exception:
            return ""

    # ── Old local-model generation (flan-t5-small) ────────────────────
    # def _generate_local(self, prompt, max_new_tokens=120):
    #     try:
    #         pipe = self._load_pipe()
    #         result = pipe(prompt, max_new_tokens=max_new_tokens, do_sample=False)
    #         raw = result[0]["generated_text"].strip()
    #         if len(raw) > 20 and raw.lower().startswith(prompt[:30].lower()):
    #             return ""
    #         return raw
    #     except Exception:
    #         return ""

    def _is_echo(self, output: str, prompt_fragment: str) -> bool:
        """Detect if the model echoed the prompt instead of generating."""
        if not output:
            return True
        # If output contains the instruction text, it's an echo
        echo_markers = [
            "write 5 to 7", "bullet points", "concise bullet",
            "study assistant", "capture the key", "numbered points",
        ]
        lower = output.lower()
        return any(m in lower for m in echo_markers)

    def _fallback_bullets(self, text, limit=5):
        """Extract key sentences directly — reliable fallback."""
        sentences = self.select_key_sentences(text, limit)
        return [
            self.simplify_sentence(s) if not s.endswith(".") else self.simplify_sentence(s)
            for s in sentences
        ] or ["No meaningful content found. Please provide more detailed notes."]

    # ── Summarize ─────────────────────────────────────────────────────

    def summarize_text(self, text, enhancement=None):
        issue = self.assess_text_quality(text, "summary")
        if issue:
            return [issue]

        cleaned = self.clean_study_text(text)
        enhancement = enhancement or PromptEnhancement([], "", "")

        # Determine how many bullets to return
        instr = enhancement.personalization_instruction.lower()
        target = 4 if "short" in instr else 7 if "detail" in instr else 5

        chunks = self.chunk_text(cleaned, max_chars=600)
        all_bullets = []

        for chunk in chunks:
            # T5-native format — short and direct
            prompt = f"summarize: {chunk}"
            raw = self._generate(prompt, max_new_tokens=150)

            if raw and not self._is_echo(raw, chunk[:40]):
                # Split on newlines or periods to get individual points
                lines = re.split(r"(?<=[.!?])\s+|\n", raw)
                lines = [re.sub(r"^[-*\d.]+\s*", "", l).strip() for l in lines]
                lines = [l for l in lines if len(l.split()) >= 4]
                all_bullets.extend(lines if lines else [raw])
            else:
                # Fallback: extract key sentences directly
                all_bullets.extend(self._fallback_bullets(chunk, limit=2))

        bullets = self.deduplicate_lines(all_bullets)
        return bullets[:target] or self._fallback_bullets(cleaned, target)

    # ── Explain ───────────────────────────────────────────────────────

    def generate_explanation(self, text, mode, topic_label="", enhancement=None):
        issue = self.assess_text_quality(text, "explanation")
        if issue:
            return [issue], []

        cleaned = self.clean_study_text(text)
        keywords = self.extract_keywords(cleaned)
        enhancement = enhancement or PromptEnhancement([], "", "")

        depth_prefix = {
            "basic":        "explain simply:",
            "intermediate": "explain:",
            "advanced":     "explain in detail:",
        }.get(mode, "explain:")

        # Process in chunks, collect explanations
        chunks = self.chunk_text(cleaned, max_chars=600)
        all_lines = []

        for chunk in chunks:
            prompt = f"{depth_prefix} {chunk}"
            raw = self._generate(prompt, max_new_tokens=180)

            if raw and not self._is_echo(raw, chunk[:40]):
                lines = re.split(r"(?<=[.!?])\s+|\n", raw)
                lines = [re.sub(r"^\d+[.)]\s*", "", l).strip() for l in lines]
                lines = [l for l in lines if len(l.split()) >= 4]
                all_lines.extend(lines if lines else [raw])
            else:
                all_lines.extend(self._fallback_bullets(chunk, limit=2))

        result = self.deduplicate_lines(all_lines)
        return result[:6] or self._fallback_bullets(cleaned, 5), keywords

    # ── Quiz & Slides (no model needed — use extraction) ─────────────

    def generate_quiz_questions(self, text, count=4):
        cleaned = self.clean_study_text(text)
        keywords = self.extract_keywords(cleaned, limit=count)
        sentences = self.select_key_sentences(cleaned, count)
        questions = []
        for i, sentence in enumerate(sentences):
            kw = keywords[i % len(keywords)] if keywords else f"concept {i+1}"
            questions.append({"keyword": kw, "sentence": sentence})
        return questions

    def generate_slide_points(self, text, title=""):
        cleaned = self.clean_study_text(text)
        topic = title or (self.extract_keywords(cleaned, 1) or ["Topic"])[0].title()
        return {"topic": topic, "keywords": self.extract_keywords(cleaned)}

    def simple_frequency_summary(self, text, max_points=5):
        sentences = self.select_key_sentences(text, max_points)
        if not sentences:
            return ["No meaningful content was found to summarize."]
        return [self.simplify_sentence(s) for s in sentences[:max_points]]

    def enforce_quality(self, lines, keywords, max_items=6):
        cleaned = []
        for line in self.deduplicate_lines(lines):
            compact = re.sub(r"\s+", " ", line).strip(" -")
            if compact and len(compact.split()) >= 4:
                cleaned.append(compact)
        return cleaned[:max_items]

    def highlight_keywords(self, sentence, keywords):
        highlighted = sentence
        for kw in keywords[:5]:
            highlighted = re.sub(
                rf"\b({re.escape(kw)})\b", r"**\1**", highlighted, flags=re.IGNORECASE
            )
        return highlighted

    def simplify_concepts(self, text):
        explanation, _ = self.generate_explanation(text, mode="basic")
        return explanation

    # ── Open Q&A ─────────────────────────────────────────────────────────
    # Unlike summarize/explain, this is NOT restricted to the user's notes —
    # the model is explicitly told it may draw on outside knowledge so it can
    # answer questions the study material doesn't cover.

    def answer_question(self, question, context=""):
        question = question.strip()
        if not question:
            return "Please ask a question."

        if context.strip():
            prompt = (
                "You are a helpful study assistant. The student has shared some "
                "study notes below and asked a question. Use the notes if they're "
                "relevant, but you are not limited to them — if the answer requires "
                "information beyond the notes, use your own general knowledge to give "
                "a complete and correct answer. Answer directly and clearly.\n\n"
                f"Study notes:\n{context.strip()}\n\n"
                f"Question: {question}\n\nAnswer:"
            )
        else:
            prompt = (
                "You are a helpful study assistant. Answer the student's question "
                "directly and clearly, drawing on your general knowledge.\n\n"
                f"Question: {question}\n\nAnswer:"
            )

        answer = self._generate(prompt, max_new_tokens=500)
        return answer or "I couldn't generate an answer for that. Try rephrasing the question."


nlp_service = NLPService()
