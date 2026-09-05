from pathlib import Path


class ResearchReportGenerator:
    """
    Generates QuantLab research reports from a template.
    """

    def __init__(self, template_path: str | Path):
        self.template_path = Path(template_path)

    def load_template(self) -> str:
        return self.template_path.read_text(encoding="utf-8")

    def generate(self, output_path: str | Path, context: dict) -> Path:
        template = self.load_template()

        for key, value in context.items():
            placeholder = "{{" + key + "}}"
            template = template.replace(placeholder, str(value))

        output_path = Path(output_path)
        output_path.write_text(template, encoding="utf-8")

        return output_path