import dash_ag_grid as dag
from dash import Dash, Input, Output, dcc, html
from jobomation.db.repository import get_jobs

HEIGHT = 500
WIDTH = "100%"
THEME = "themeBalham"
PAGINATION = 20
HEADER_SIZE = 24
FONT_SIZE = 16
LINE_HEIGHT = 1.5
FONT_FAMILY = "Arial"
TITLE = "Jobs Dashboard"

BASE_COLUMN_DEFS = [
    {"field": "title", "filter": True},
    {"field": "company", "filter": True},
    {"field": "location", "filter": True},
    {"field": "source", "filter": True},
    {"field": "first_published", "headerName": "First Published", "filter": True},
    {"field": "url", "headerName": "URL"},
    {"field": "active", "filter": True},
]

FILTER_COLUMN_DEFS = [
    {"field": "filtered", "filter": True},
    {"field": "filter_reason", "headerName": "Filter Reason", "filter": True},
]

def job_to_row(job) -> dict:
    return {
        "source": job.source,
        "source_job_id": job.source_job_id,
        "title": job.title,
        "company": job.company,
        "location": job.location,
        "first_published": job.first_published,
        "filtered": job.filtered,
        "filter_reason": job.filter_reason,
        "url": job.url,
        "active": job.active,
        "description": job.description,
    }

def create_app() -> Dash:
    app = Dash(__name__, title=TITLE)

    jobs = get_jobs()
    rows = [job_to_row(job) for job in jobs]

    app.layout = html.Div(
        [
            html.H1(
                TITLE,
                style={
                    "textAlign": "center",
                    "fontSize": HEADER_SIZE,
                    "fontFamily": FONT_FAMILY,
                },
            ),

            html.P(
                f"{len(jobs)} jobs in database",
                id="job-count",
                style={
                    "textAlign": "center",
                    "fontSize": FONT_SIZE,
                    "fontFamily": FONT_FAMILY,
                },
            ),

            dcc.Checklist(
                id="show-filtered",
                options=[
                    {
                        "label": "Show filtered jobs",
                        "value": "show",
                    }
                ],
                style={
                    "fontSize": FONT_SIZE,
                    "fontFamily": FONT_FAMILY,
                },
                value=[],
            ),

            dag.AgGrid(
                id="jobs-grid",
                rowData=rows,
                getRowId="params.data.source + ':' + params.data.source_job_id",
                columnDefs=BASE_COLUMN_DEFS,
                defaultColDef={
                    "sortable": True,
                    "resizable": True,
                },
                dashGridOptions={
                    "pagination": True,
                    "paginationPageSize": PAGINATION,
                    "theme": THEME,
                    "rowSelection": {
                        "mode": "singleRow",
                        "enableClickSelection": True,
                    },
                },
                style={
                    "height": HEIGHT,
                    "width": WIDTH,
                },
            ),

            html.Div(
                id="job-details",
                style={
                    "fontFamily": FONT_FAMILY,
                },
            ),
        ]
    )

    @app.callback(
        Output("jobs-grid", "rowData"),
        Output("jobs-grid", "columnDefs"),
        Output("job-count", "children"),
        Input("show-filtered", "value"),
    )
    def update_rows(show_filtered):
        if "show" in show_filtered:
            visible_jobs = jobs
            visible_columns = BASE_COLUMN_DEFS + FILTER_COLUMN_DEFS
            
        else:
            visible_jobs = [job for job in jobs if not job.filtered]
            visible_columns = BASE_COLUMN_DEFS

        return (
            [job_to_row(job) for job in visible_jobs],
            visible_columns,
            f"{len(visible_jobs)} jobs shown ({len(jobs)} in database)",
        )
    
    @app.callback(
        Output("job-details", "children"),
        Input("jobs-grid", "selectedRows"),
    )
    def show_job_details(selected_rows):
        if not selected_rows: return html.P("Select a job to view details.")

        job = selected_rows[0]

        return html.Div(
            [
                html.H2(job["title"]),
                html.H3(job["company"]),

                html.P([
                    html.Strong("Location: "),
                    job["location"],
                ]),

                html.P([
                    html.Strong("Source: "),
                    job["source"],
                ]),

                html.P([
                    html.Strong("First Published: "),
                    job["first_published"],
                ]),

                html.P([
                    html.Strong("Filtered: "),
                    str(job["filtered"]),
                ]),

                html.P([
                    html.Strong("Filter Reason: "),
                    job["filter_reason"] or "None",
                ]),

                html.P(
                    html.A(
                        "Open job posting",
                        href=job["url"],
                        target="_blank",
                    )
                ),

                html.H3("Description"),

                html.Div(
                    job["description"],
                    style={
                        "whiteSpace": "pre-wrap",
                        "lineHeight": LINE_HEIGHT,
                    },
                ),
            ]
        )

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)