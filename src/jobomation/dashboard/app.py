import dash_ag_grid as dag
from dash import Dash, html
from jobomation.db.repository import get_jobs

HEIGHT = 650
WIDTH = "100%"
THEME = "themeBalham"
PAGINATION = 20
HEADER_SIZE = 24
FONT_SIZE = 16
FONT_FAMILY = "Arial"
TITLE = "Jobs Dashboard"

def create_app() -> Dash:
    app = Dash(__name__, title=TITLE)

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
            html.H1(children = TITLE,
                    style = { "textAlign": "center", "fontSize": HEADER_SIZE, "fontFamily": FONT_FAMILY }),
            html.P(children = f"{len(jobs)} jobs in database",
                    style = { "textAlign": "center", "fontSize": FONT_SIZE, "fontFamily": FONT_FAMILY }),
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
                    "paginationPageSize": PAGINATION,
                    "theme": THEME,
                },
                style={"height": HEIGHT, "width": WIDTH}
            ),
        ]
    )

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)