from jobomation.collectors.ashby import AshbyCollector
from jobomation.collectors.greenhouse import GreenhouseCollector
from jobomation.collectors.indeed import IndeedCollector

COLLECTORS = {
    collector.source: collector
    for collector in (
        AshbyCollector,
        GreenhouseCollector,
        IndeedCollector
    )
}