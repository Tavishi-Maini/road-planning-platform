from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


def generate_pdf_report(project_data, prediction_data, feature_importance_df=None):
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    title = "Road Construction Planning & Cost Estimation Report"

    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
            styles["Normal"],
        )
    )

    story.append(Spacer(1, 20))

    # Project Overview
    story.append(Paragraph("1. Project Overview", styles["Heading2"]))

    overview_data = [
        ["Field", "Value"],
        ["Project Name", project_data.get("project_name", "-")],
        ["Location", project_data.get("location", "-")],
        ["Road Category", project_data.get("road_category", "-")],
        ["Terrain Type", project_data.get("terrain_type", "-")],
        ["Road Length", f"{project_data.get('road_length_km', 0)} km"],
        ["Risk Level", project_data.get("risk_level", "-")],
    ]

    story.append(_create_table(overview_data))
    story.append(Spacer(1, 16))

    # Input Parameters
    story.append(Paragraph("2. Input Parameters", styles["Heading2"]))

    input_data = [["Parameter", "Value"]]

    for key, value in project_data.items():
        input_data.append([key, str(value)])

    story.append(_create_table(input_data))
    story.append(Spacer(1, 16))

    # Prediction Summary
    story.append(Paragraph("3. Prediction Summary", styles["Heading2"]))

    prediction_table = [
        ["Target Variable", "Predicted Value"],
        ["Total Cost", f"Rs. {prediction_data.get('total_cost', 0):,.2f}"],
        ["Construction Duration", f"{prediction_data.get('duration', 0):,.2f} months"],
        ["Material Index", f"{prediction_data.get('material_index', 0):,.2f}"],
        ["Manpower Hours per km", f"{prediction_data.get('manpower_hours_per_km', 0):,.2f}"],
        ["Machinery Hours per km", f"{prediction_data.get('machinery_hours_per_km', 0):,.2f}"],
    ]

    story.append(_create_table(prediction_table))
    story.append(Spacer(1, 16))

    # Feature Importance
    story.append(Paragraph("4. Feature Importance", styles["Heading2"]))

    if feature_importance_df is not None and not feature_importance_df.empty:
        feature_table = [["Feature", "Importance Score"]]

        for _, row in feature_importance_df.head(10).iterrows():
            feature_table.append([
                row["feature"],
                f"{row['importance']:.4f}",
            ])

        story.append(_create_table(feature_table))
    else:
        story.append(
            Paragraph(
                "Feature importance data is unavailable for this model.",
                styles["Normal"],
            )
        )

    story.append(Spacer(1, 16))

    # Planning Recommendations
    story.append(Paragraph("5. Planning Recommendations", styles["Heading2"]))

    recommendations = """
    The estimates should be used for preliminary planning, scenario comparison,
    and early-stage infrastructure decision support. Projects with high resource
    intensity should be reviewed for labour availability, machinery deployment,
    material sourcing, and execution risk.
    """

    story.append(Paragraph(recommendations, styles["Normal"]))
    story.append(Spacer(1, 16))

    # Disclaimer
    story.append(Paragraph("6. Disclaimer", styles["Heading2"]))

    disclaimer = """
    This report is generated using machine learning models and user-provided
    project inputs. It is not a substitute for a detailed DPR, BOQ, tender estimate,
    or certified engineering cost assessment.
    """

    story.append(Paragraph(disclaimer, styles["Normal"]))

    doc.build(story)

    buffer.seek(0)
    return buffer


def _create_table(data):
    table = Table(data, repeatRows=1)

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#111827")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#F9FAFB")),
            ]
        )
    )

    return table