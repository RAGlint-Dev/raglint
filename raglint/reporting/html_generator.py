import os

from jinja2 import Environment, FileSystemLoader


def generate_html_report(results: dict, output_file: str = "raglint_report.html"):
    """
    Generate a beautiful HTML report with visualizations.
    """
    # Create Jinja2 environment with autoescape enabled for security
    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=True  # Security: Enable autoescape to prevent XSS
    )
    template = env.get_template("report.html")

    html_content = template.render(results=results)

    with open(output_file, "w") as f:
        f.write(html_content)

    print(f"Report generated at: {output_file}")
