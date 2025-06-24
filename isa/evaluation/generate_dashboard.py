import yaml
import os
from datetime import datetime

def generate_dashboard():
    """
    Loads scorecard data from a YAML file and generates a Markdown dashboard.
    """
    scorecard_path = os.path.join('isa', 'reports', 'scorecard.yaml')
    dashboard_path = os.path.join('isa', 'reports', 'status_dashboard.md')

    try:
        with open(scorecard_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: The file {scorecard_path} was not found.")
        return
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return

    markdown_lines = []

    # --- Main Title ---
    markdown_lines.append("# ISA Excellence Dashboard")
    markdown_lines.append(f"> _Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_")
    markdown_lines.append("\n---\n")

    # --- Metadata and Summary ---
    markdown_lines.append("##  оценка Summary")
    if 'evaluatie_metadata' in data:
        meta = data['evaluatie_metadata']
        markdown_lines.append("### Evaluation Metadata")
        for key, value in meta.items():
            markdown_lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        markdown_lines.append("")

    if 'samenvatting_scores' in data:
        summary = data['samenvatting_scores']
        markdown_lines.append("### Summary Scores")
        markdown_lines.append("| Criterium                       | Score |")
        markdown_lines.append("|---------------------------------|-------|")
        for key, value in summary.items():
            markdown_lines.append(f"| {key.replace('_', ' ').title():<31} | {value:<5} |")
        markdown_lines.append("\n---\n")


    # --- Detailed Criteria ---
    markdown_lines.append("## Detailed Criteria Analysis")
    if 'criteria_details' in data:
        for criterion in data['criteria_details']:
            markdown_lines.append(f"\n### {criterion.get('naam', 'N/A')}")
            markdown_lines.append(f"**Score:** `{criterion.get('score', 'N/A')}` | **Trend:** _{criterion.get('trend', 'N/A')}_")
            
            markdown_lines.append("\n> #### Summary")
            markdown_lines.append(f"> {criterion.get('samenvatting', 'No summary provided.')}")
            
            # KPIs
            if 'kpis' in criterion and criterion['kpis']:
                markdown_lines.append("\n**Key Performance Indicators (KPIs):**")
                markdown_lines.append("| KPI Name                  | Value | Target | Status |")
                markdown_lines.append("|---------------------------|-------|--------|--------|")
                for kpi in criterion['kpis']:
                    markdown_lines.append(f"| {kpi.get('naam', ''):<25} | {kpi.get('waarde', ''):<5} | {kpi.get('doel', ''):<6} | {kpi.get('status', ''):<6} |")

            # Gap Analysis
            if 'gap_analyse' in criterion and criterion['gap_analyse']:
                markdown_lines.append("\n**Gap Analysis:**")
                for gap in criterion['gap_analyse']:
                    markdown_lines.append(f"- **Gap:** {gap.get('hiaat', 'N/A')}")
                    markdown_lines.append(f"  - *AI Confidence:* `{gap.get('ai_vertrouwensscore', 'N/A')}`")
                    markdown_lines.append(f"  - *Evidence:* `{gap.get('bewijs_link', 'N/A')}`")

            # Action Points
            if 'actiepunten' in criterion and criterion['actiepunten']:
                markdown_lines.append("\n**Action Points:**")
                markdown_lines.append("| Action                               | Owner         | Ticket ID | Status |")
                markdown_lines.append("|--------------------------------------|---------------|-----------|--------|")
                for action in criterion['actiepunten']:
                    markdown_lines.append(f"| {action.get('actie', ''):<36} | {action.get('eigenaar', ''):<13} | {action.get('ticket_id', ''):<9} | {action.get('status', ''):<6} |")
            
            markdown_lines.append("\n---")


    # --- Write to file ---
    try:
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(markdown_lines))
        print(f"Dashboard successfully generated at {dashboard_path}")
    except IOError as e:
        print(f"Error writing to file {dashboard_path}: {e}")

if __name__ == "__main__":
    generate_dashboard()