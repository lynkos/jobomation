import dash_ag_grid as dag
from dash import Dash, Input, Output, dcc, html
from jobomation.db.repository import get_jobs, set_job_active, mark_job_seen

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
    {"field": "compensation", "headerName": "Compensation", "filter": True},
    {"field": "url", "headerName": "URL"},
    {
        "field": "active",
        "filter": True,
        "editable": True,
        "cellDataType": "boolean",
    },
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
        "compensation": format_compensation(job.compensation),
        "compensation_description": job.compensation.description if job.compensation else None,
        "filtered": job.filtered,
        "filter_reason": job.filter_reason,
        "url": job.url,
        "active": job.active,
        "description": job.description,
    }

def format_compensation(compensation) -> str | None:
    if compensation is None: return None

    minimum = compensation.min_amount
    maximum = compensation.max_amount
    currency = compensation.currency
    interval = compensation.interval

    if minimum is not None and maximum is not None: amount = f"{minimum:,.0f} – {maximum:,.0f}"
    elif minimum is not None: amount = f"{minimum:,.0f}+"
    elif maximum is not None: amount = f"Up to {maximum:,.0f}"
    else: amount = None

    if amount is None: return compensation.description
    if currency: amount = f"{currency} {amount}"
    if interval: amount = f"{amount} / {interval}"

    return amount

def update_job_active(events):
    if not events: return

    for event in events:
        if event["colId"] != "active": continue

        row = event["data"]

        set_job_active(
            source = row["source"],
            source_job_id = row["source_job_id"],
            active = row["active"],
        )

def create_app() -> Dash:
    app = Dash(__name__, title = TITLE)

    jobs = get_jobs(filtered = False)
    rows = [ job_to_row(job) for job in jobs ]

    app.layout = html.Div(
        [
            html.H1(
                TITLE,
                style = {
                    "textAlign": "center",
                    "fontSize": HEADER_SIZE,
                    "fontFamily": FONT_FAMILY,
                },
            ),

            dcc.Checklist(
                id = "show-filtered",
                options = [
                    {
                        "label": "Include filtered jobs",
                        "value": "show",
                    }
                ],
                style = {
                    "fontSize": FONT_SIZE,
                    "fontFamily": FONT_FAMILY,
                },
                value = [ ],
            ),

            dag.AgGrid(
                id = "jobs-grid",
                rowData = rows,
                getRowId = "params.data.source + ':' + params.data.source_job_id",
                columnDefs = BASE_COLUMN_DEFS,
                defaultColDef = {
                    "sortable": True,
                    "resizable": True,
                },
                dashGridOptions = {
                    "pagination": True,
                    "paginationPageSize": PAGINATION,
                    "theme": THEME,
                    "rowSelection": {
                        "mode": "singleRow",
                        "enableClickSelection": True,
                    },
                },
                style = {
                    "height": HEIGHT,
                    "width": WIDTH,
                },
            ),

            html.Div(
                id = "job-details",
                style = {
                    "fontFamily": FONT_FAMILY,
                },
            ),
        ]
    )

    @app.callback(
        Output("jobs-grid", "rowData"),
        Output("jobs-grid", "columnDefs"),
        Input("show-filtered", "value"),
    )
    def update_rows(show_filtered):
        if "show" in show_filtered:
            jobs = get_jobs()
            visible_columns = BASE_COLUMN_DEFS + FILTER_COLUMN_DEFS
        else:
            jobs = get_jobs(filtered = False)
            visible_columns = BASE_COLUMN_DEFS

        return (
            [job_to_row(job) for job in jobs],
            visible_columns,
        )
        
    @app.callback(
        Output("job-details", "children"),
        Input("jobs-grid", "selectedRows"),
    )
    def show_job_details(selected_rows):
        if not selected_rows: return html.P("Select a job to view details.")

        job = selected_rows[0]

        mark_job_seen(source = job["source"], source_job_id = job["source_job_id"])

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
                    html.Strong("Compensation: "),
                    job["compensation"] or "Not listed",
                ]),

                html.P([
                    html.Strong("Compensation Details: "),
                    job["compensation_description"],
                ]) if job["compensation_description"] else None,

                html.P([
                    html.Strong("Filtered: "),
                    str(job["filtered"]),
                ]),

                html.P([
                    html.Strong("Filter Reason: "),
                    job["filter_reason"],
                ]) if job["filter_reason"] else None,

                html.P([
                    html.Strong("Job ID: "),
                    job["source_job_id"],
                ]),

                html.P(
                    html.A(
                        "Open job posting",
                        href = job["url"],
                        target = "_blank",
                    )
                ),

                html.H3("Description"),

                html.Div(
                    job["description"],
                    style = {
                        "whiteSpace": "pre-wrap",
                        "lineHeight": LINE_HEIGHT,
                    },
                ),
            ]
        )

    app.callback(
        Input("jobs-grid", "cellValueChanged"),
        prevent_initial_call = True,
    )(update_job_active)
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug = True)