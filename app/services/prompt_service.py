from dataclasses import dataclass, field


DEFAULT_ROLE = "You are an expert academic tutor who explains complex topics clearly to students."


@dataclass
class PromptTemplate:
    """Reusable prompt template container for generation and refinement steps."""

    role: str
    task: str
    format_rules: list[str]
    tone: str
    text: str
    examples: list[str] = field(default_factory=list)
    mode: str = ""
    extra_instruction: str = ""

    def render(self) -> str:
        """Builds a readable prompt string that can be reused by different engines."""
        sections = [
            f"ROLE:\n{self.role}",
            f"TASK:\n{self.task}",
            f"TONE:\n{self.tone}",
        ]

        if self.mode:
            sections.append(f"MODE:\n{self.mode}")

        sections.append("FORMAT RULES:\n" + "\n".join(f"- {rule}" for rule in self.format_rules))

        if self.extra_instruction:
            sections.append(f"QUALITY CONTROL:\n{self.extra_instruction}")

        if self.examples:
            sections.append("FEW-SHOT EXAMPLES:\n" + "\n\n".join(self.examples))

        sections.append(f"TEXT:\n{self.text}")
        return "\n\n".join(sections)


class PromptService:
    """Central place for reusable prompt engineering rules."""

    def __init__(self) -> None:
        self.role = DEFAULT_ROLE
        self.student_tone = "Simple, student-friendly, clear, and supportive."

    def build_summary_prompt(
        self,
        user_input: str,
        examples: list[str] | None = None,
        adaptive_instruction: str = "",
        personalization_instruction: str = "",
    ) -> PromptTemplate:
        default_examples = [
            (
                "INPUT TEXT:\n"
                "Photosynthesis helps plants convert sunlight into food. Chlorophyll captures light, "
                "and the process also releases oxygen.\n"
                "EXPECTED OUTPUT:\n"
                "- **Photosynthesis** helps plants turn sunlight into food.\n"
                "- **Chlorophyll** captures the light energy needed for the process.\n"
                "- The process also releases **oxygen**."
            ),
            (
                "INPUT TEXT:\n"
                "The water cycle includes evaporation, condensation, and precipitation. These stages move "
                "water through the environment.\n"
                "EXPECTED OUTPUT:\n"
                "- The **water cycle** moves water through the environment.\n"
                "- **Evaporation**, **condensation**, and **precipitation** are the main stages.\n"
                "- Each stage helps water change form and location."
            ),
        ]

        quality_instruction = (
            "Generate an initial summary, improve its clarity and structure, then simplify the language "
            "for student revision."
        )
        if adaptive_instruction:
            quality_instruction += f" {adaptive_instruction}"
        if personalization_instruction:
            quality_instruction += f" {personalization_instruction}"

        return PromptTemplate(
            role=self.role,
            task=(
                "Summarize the following text into clear bullet points. Focus on key ideas only, remove "
                "unnecessary details, and make it easy for a student to revise."
            ),
            format_rules=[
                "Use bullet points",
                "Use short sentences",
                "Highlight important terms with markdown bold",
                "Avoid repetition",
            ],
            tone=self.student_tone,
            text=user_input,
            examples=(examples or []) + default_examples[: max(0, 2 - len(examples or []))],
            extra_instruction=quality_instruction,
        )

    def build_explanation_prompt(
        self,
        user_input: str,
        mode: str,
        examples: list[str] | None = None,
        adaptive_instruction: str = "",
        personalization_instruction: str = "",
    ) -> PromptTemplate:
        default_examples = [
            (
                "INPUT TEXT:\n"
                "Mitosis is the process by which a cell divides into two identical daughter cells.\n"
                "EXPECTED OUTPUT:\n"
                "1. **What it is**: Mitosis is how one cell splits into two matching cells.\n"
                "2. **How it works**: The cell copies its contents and then divides.\n"
                "3. **Why it matters**: It helps living things grow and repair tissues."
            ),
            (
                "INPUT TEXT:\n"
                "Inflation means the general price of goods and services rises over time.\n"
                "EXPECTED OUTPUT:\n"
                "1. **What it is**: Inflation means prices go up over time.\n"
                "2. **Example**: If bread costs more this year than last year, that is inflation.\n"
                "3. **Why it matters**: Money buys less when prices rise."
            ),
        ]

        quality_instruction = (
            "Check that the explanation is accurate, remove redundancy, and make it easier to understand."
        )
        if adaptive_instruction:
            quality_instruction += f" {adaptive_instruction}"
        if personalization_instruction:
            quality_instruction += f" {personalization_instruction}"

        return PromptTemplate(
            role=self.role,
            task=(
                "Explain the following content in simple terms, break it down step-by-step, use examples "
                "where possible, and avoid complex words."
            ),
            format_rules=[
                "Use a structured step-by-step layout",
                "Keep explanations student-friendly",
                "Use examples where helpful",
                "Avoid unnecessary jargon",
            ],
            tone=self.student_tone,
            text=user_input,
            mode=mode,
            examples=(examples or []) + default_examples[: max(0, 2 - len(examples or []))],
            extra_instruction=quality_instruction,
        )

    def build_improvement_prompt(self, generated_output: str, task_name: str) -> PromptTemplate:
        return PromptTemplate(
            role=self.role,
            task=(
                f"Improve the following {task_name} by making it clearer, more accurate, and easier to "
                "understand. Remove redundancy and organize it better."
            ),
            format_rules=[
                "Keep the same meaning",
                "Remove repeated points",
                "Improve flow and readability",
            ],
            tone=self.student_tone,
            text=generated_output,
        )

    def build_accuracy_check_prompt(self, source_text: str, generated_output: str, task_name: str) -> PromptTemplate:
        return PromptTemplate(
            role=self.role,
            task=(
                f"Check this {task_name} for accuracy against the source text and fix anything misleading, "
                "unclear, or unsupported."
            ),
            format_rules=[
                "Preserve correct information",
                "Fix inaccuracies",
                "Keep the result student-friendly",
            ],
            tone=self.student_tone,
            text=f"SOURCE:\n{source_text}\n\nOUTPUT TO CHECK:\n{generated_output}",
        )


prompt_service = PromptService()
