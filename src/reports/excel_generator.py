import io
import pandas as pd


def generate_excel_report(project_data, prediction_data, feature_importance_df=None):
    output = io.BytesIO()

    project_df = pd.DataFrame(
        list(project_data.items()),
        columns=["Input Parameter", "Value"]
    )

    prediction_df = pd.DataFrame(
        list(prediction_data.items()),
        columns=["Prediction Metric", "Predicted Value"]
    )

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        project_df.to_excel(writer, sheet_name="Project Inputs", index=False)
        prediction_df.to_excel(writer, sheet_name="Predictions", index=False)

        if feature_importance_df is not None and not feature_importance_df.empty:
            feature_importance_df.to_excel(
                writer,
                sheet_name="Feature Importance",
                index=False
            )

        workbook = writer.book

        header_format = workbook.add_format({
            "bold": True,
            "bg_color": "#111827",
            "font_color": "#FFFFFF",
            "border": 1
        })

        cell_format = workbook.add_format({
            "border": 1
        })

        for sheet_name in writer.sheets:
            worksheet = writer.sheets[sheet_name]

            worksheet.set_row(0, 20, header_format)
            worksheet.set_column(0, 0, 30, cell_format)
            worksheet.set_column(1, 1, 25, cell_format)

    output.seek(0)
    return output