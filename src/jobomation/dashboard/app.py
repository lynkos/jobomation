import dash_ag_grid as dag
from dash import Dash, html
from jobomation.db.repository import get_jobs

def create_app() -> Dash:
    app = Dash(__name__)

    jobs = get_jobs()

    rows = [
        {
            "title": job.title,
            "company": job.company,
            "location": job.location,
            "source": job.source,
            "first_published": job.first_published,
            "active": job.active,
            "url": job.url,
        }
        for job in jobs
    ]

    column_defs = [
        {"field": "title", "filter": True},
        {"field": "company", "filter": True},
        {"field": "location", "filter": True},
        {"field": "source", "filter": True},
        {"field": "first_published", "filter": True},
        {"field": "active", "filter": True},
        {"field": "url"},
    ]

    app.layout = html.Div(
        [
            html.H1("Jobomation"),
            html.P(f"{len(jobs)} jobs in database"),
            dag.AgGrid(
                id="jobs-grid",
                rowData=rows,
                columnDefs=column_defs,
                defaultColDef={
                    "sortable": True,
                    "resizable": True,
                },
                dashGridOptions={
                    "pagination": True,
                    "paginationPageSize": 20,
                },
                style={"height": 650, "width": "100%"}
            ),
        ]
    )

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)